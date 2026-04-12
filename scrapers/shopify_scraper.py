import requests
import pandas as pd
from datetime import datetime
import time
import os
from pathlib import Path

DELAY = int(os.getenv("SCRAPER_DELAY", 2))
STORES_FILE = Path("config/stores.txt")


def load_stores() -> list[str]:
    """Load store slugs from config file, ignoring comments."""
    with open(STORES_FILE) as f:
        return [
            line.strip()
            for line in f.readlines()
            if line.strip() and not line.startswith("#")
        ]


def scrape_store(store_slug: str) -> list[dict]:
    """Scrape all products from a Shopify store's public /products.json endpoint."""
    url = f"https://{store_slug}.myshopify.com/products.json?limit=250"
    try:
        r = requests.get(url, timeout=10, headers={"User-Agent": "Mozilla/5.0"})
        if r.status_code != 200:
            return []
        products = r.json().get("products", [])
        results = []
        for p in products:
            variants = p.get("variants", [{}])
            prices = [float(v.get("price", 0)) for v in variants if v.get("price")]
            results.append({
                "store": store_slug,
                "product_id": p.get("id"),
                "title": p.get("title", ""),
                "handle": p.get("handle", ""),
                "tags": ",".join(p.get("tags", [])),
                "product_type": p.get("product_type", ""),
                "price_min": min(prices) if prices else 0,
                "price_max": max(prices) if prices else 0,
                "variants_count": len(variants),
                "images_count": len(p.get("images", [])),
                "created_at": p.get("created_at", ""),
                "updated_at": p.get("updated_at", ""),
                "scraped_at": datetime.now().isoformat(),
            })
        return results
    except Exception as e:
        print(f"[!] Error scraping {store_slug}: {e}")
        return []


def scrape_all_stores(stores: list[str] = None) -> pd.DataFrame:
    """Scrape all stores and return a combined DataFrame."""
    if stores is None:
        stores = load_stores()
    all_products = []
    for i, store in enumerate(stores):
        print(f"[{i+1}/{len(stores)}] Scraping {store}...")
        products = scrape_store(store)
        print(f"  → {len(products)} products found")
        all_products.extend(products)
        time.sleep(DELAY)
    df = pd.DataFrame(all_products)
    if not df.empty:
        df["created_at"] = pd.to_datetime(df["created_at"], errors="coerce", utc=True)
        df["days_since_creation"] = (
            (pd.Timestamp.now(tz="UTC") - df["created_at"]).dt.days
        )
    return df


def get_multi_store_products(df: pd.DataFrame, min_stores: int = 2) -> pd.DataFrame:
    """Find products listed across multiple stores (strong validation signal)."""
    store_counts = (
        df.groupby("handle")["store"]
        .nunique()
        .reset_index()
        .rename(columns={"store": "store_count"})
    )
    df = df.merge(store_counts, on="handle", how="left")
    return df[df["store_count"] >= min_stores].copy()


if __name__ == "__main__":
    df = scrape_all_stores()
    print(f"\n✅ Total products scraped: {len(df)}")
    df.to_csv("data/shopify_raw.csv", index=False)
    print("Saved to data/shopify_raw.csv")
