import pandas as pd
from scrapers.trends_scraper import get_trend_score
from scrapers.meta_ads_spy import get_ads_signal
from scrapers.aliexpress_api import get_demand_score
import time


WEIGHTS = {
    "trend_score": 0.35,      # Google Trends avg interest FR
    "recency_score": 0.25,    # How recently the product was created (newer = better)
    "multi_store_score": 0.20, # Listed on multiple stores = validated demand
    "meta_ads_score": 0.15,   # Active Meta ads running >14 days = scaling
    "ali_demand_score": 0.05, # AliExpress order volume
}


def recency_score(days_since_creation: float) -> float:
    """Score 0-100: newer product = higher score (decays over 90 days)."""
    if pd.isna(days_since_creation):
        return 20.0
    if days_since_creation <= 7:
        return 100.0
    elif days_since_creation <= 30:
        return 80.0
    elif days_since_creation <= 60:
        return 55.0
    elif days_since_creation <= 90:
        return 35.0
    return 15.0


def multi_store_score(store_count: int) -> float:
    """Score 0-100: more stores selling the same product = stronger signal."""
    if store_count >= 5:
        return 100.0
    elif store_count >= 3:
        return 75.0
    elif store_count >= 2:
        return 50.0
    return 20.0


def meta_ads_to_score(signal: dict) -> float:
    """Convert Meta ads signal to 0-100 score."""
    if signal["nb_active_ads"] == 0:
        return 0.0
    base = min(signal["nb_active_ads"] * 5, 60)
    bonus = 40 if signal["has_scaling_ads"] else 0
    return min(base + bonus, 100.0)


def score_product(row: pd.Series, delay: float = 1.0) -> pd.Series:
    """
    Compute the full winning score for a single product row.
    Hits external APIs (Trends, Meta). Use with apply() on a DataFrame.
    """
    keyword = str(row.get("title", ""))[:50]

    # 1. Google Trends
    trend = get_trend_score(keyword)
    time.sleep(delay)

    # 2. Recency
    recency = recency_score(row.get("days_since_creation", 999))

    # 3. Multi-store
    multi = multi_store_score(row.get("store_count", 1))

    # 4. Meta Ads
    ads_signal = get_ads_signal(keyword)
    meta = meta_ads_to_score(ads_signal)
    time.sleep(delay)

    # 5. AliExpress demand
    ali = get_demand_score(keyword) * 20  # scale 0-5 → 0-100

    # Weighted final score
    final_score = (
        trend * WEIGHTS["trend_score"]
        + recency * WEIGHTS["recency_score"]
        + multi * WEIGHTS["multi_store_score"]
        + meta * WEIGHTS["meta_ads_score"]
        + ali * WEIGHTS["ali_demand_score"]
    )

    return pd.Series({
        **row.to_dict(),
        "trend_score": trend,
        "recency_score": recency,
        "multi_store_score": multi,
        "meta_ads_score": meta,
        "ali_demand_score": ali,
        "nb_active_ads": ads_signal["nb_active_ads"],
        "ads_days_running": ads_signal["avg_days_running"],
        "has_scaling_ads": ads_signal["has_scaling_ads"],
        "final_score": round(final_score, 1),
    })


def score_dataframe(df: pd.DataFrame, top_n: int = 50) -> pd.DataFrame:
    """
    Score a sample of products from the scraped DataFrame.
    Only scores top_n products (by recency) to save API calls.
    """
    # Pre-filter: recent products only (< 90 days)
    if "days_since_creation" in df.columns:
        df = df[df["days_since_creation"] < 90].copy()

    # Deduplicate by handle, take first occurrence
    df = df.drop_duplicates(subset="handle", keep="first")

    # Take top_n newest
    df = df.sort_values("days_since_creation").head(top_n)

    print(f"Scoring {len(df)} products...")
    scored = df.apply(score_product, axis=1)
    return scored.sort_values("final_score", ascending=False)
