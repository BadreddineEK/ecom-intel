#!/usr/bin/env python3
"""
EcomIntel — Main scraper entry point.

Usage:
    python run_scraper.py                  # Full run (scrape + score)
    python run_scraper.py --scrape-only    # Only scrape, no scoring
    python run_scraper.py --top 20         # Score only top 20 products
"""

import argparse
import pandas as pd
from pathlib import Path
from scrapers.shopify_scraper import scrape_all_stores, get_multi_store_products
from engine.scorer import score_dataframe

Data_DIR = Path("data")
Data_DIR.mkdir(exist_ok=True)


def main():
    parser = argparse.ArgumentParser(description="EcomIntel product scraper")
    parser.add_argument("--scrape-only", action="store_true", help="Only scrape, skip scoring")
    parser.add_argument("--top", type=int, default=50, help="Number of products to score (default: 50)")
    parser.add_argument("--stores", type=str, help="Comma-separated store slugs to scrape")
    args = parser.parse_args()

    stores = args.stores.split(",") if args.stores else None

    print("=" * 50)
    print("🛒 EcomIntel — Starting product intelligence scan")
    print("=" * 50)

    # Step 1: Scrape
    print("\n[1/3] Scraping Shopify stores...")
    df_raw = scrape_all_stores(stores=stores)
    print(f"✅ {len(df_raw)} total products scraped")
    df_raw.to_csv(Data_DIR / "shopify_raw.csv", index=False)

    if df_raw.empty:
        print("[!] No products found. Check your stores.txt config.")
        return

    if args.scrape_only:
        print("\n✅ Scrape-only mode. Done.")
        return

    # Step 2: Cross-store analysis
    print("\n[2/3] Cross-store product analysis...")
    df_multi = get_multi_store_products(df_raw, min_stores=1)
    print(f"✅ {len(df_multi)} unique product handles (multi-store filtered)")

    # Step 3: Scoring
    print(f"\n[3/3] Scoring top {args.top} products (Trends + Meta Ads + Ali)...")
    df_scored = score_dataframe(df_multi, top_n=args.top)
    df_scored.to_csv(Data_DIR / "results.csv", index=False)

    print("\n" + "=" * 50)
    print(f"✅ Done! {len(df_scored)} products scored")
    print(f"📊 Results saved to data/results.csv")
    print("\n🏆 Top 5 winning products:")
    print(df_scored[["title", "store", "final_score"]].head(5).to_string(index=False))
    print("\n💡 Launch dashboard: streamlit run dashboard/app.py")
    print("=" * 50)


if __name__ == "__main__":
    main()
