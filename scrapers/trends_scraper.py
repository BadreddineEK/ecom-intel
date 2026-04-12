import time
import pandas as pd
from pytrends.request import TrendReq

pytrends = TrendReq(hl="fr-FR", tz=60, geo="FR")


def get_trend_score(keyword: str, geo: str = "FR", timeframe: str = "today 3-m") -> float:
    """
    Return average Google Trends interest score (0-100) for a keyword in France
    over the last 3 months. Returns 0 if no data.
    """
    try:
        pytrends.build_payload([keyword], geo=geo, timeframe=timeframe)
        df = pytrends.interest_over_time()
        if df.empty or keyword not in df.columns:
            return 0.0
        return round(float(df[keyword].mean()), 1)
    except Exception as e:
        print(f"[Trends] Error for '{keyword}': {e}")
        return 0.0


def get_related_queries(keyword: str) -> dict:
    """Return top and rising related queries for a keyword."""
    try:
        pytrends.build_payload([keyword], geo="FR", timeframe="today 3-m")
        related = pytrends.related_queries()
        top = related.get(keyword, {}).get("top")
        rising = related.get(keyword, {}).get("rising")
        return {
            "top": top.head(5).to_dict() if top is not None else {},
            "rising": rising.head(5).to_dict() if rising is not None else {},
        }
    except Exception as e:
        print(f"[Trends] Related queries error: {e}")
        return {}


def score_keywords_batch(keywords: list[str], delay: float = 1.5) -> pd.DataFrame:
    """Score a list of keywords and return a DataFrame with scores."""
    results = []
    for kw in keywords:
        score = get_trend_score(kw)
        results.append({"keyword": kw, "trend_score": score})
        time.sleep(delay)  # Respect rate limits
    return pd.DataFrame(results)


if __name__ == "__main__":
    test_keywords = ["organisateur tiroir", "masque sommeil", "gap filler voiture"]
    df = score_keywords_batch(test_keywords)
    print(df)
