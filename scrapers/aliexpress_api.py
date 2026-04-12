import os
import requests
import pandas as pd
from dotenv import load_dotenv

load_dotenv()

ALI_APP_KEY = os.getenv("ALI_APP_KEY", "")
ALI_APP_SECRET = os.getenv("ALI_APP_SECRET", "")
ALI_AFFILIATE_API = "https://api-sg.aliexpress.com/sync"


def search_products(keyword: str, limit: int = 10, sort: str = "LAST_VOLUME_DESC") -> list[dict]:
    """
    Search AliExpress for top products by keyword.
    Returns list of product dicts with price, orders, rating.
    Falls back to empty list if no API keys configured.
    """
    if not ALI_APP_KEY:
        print("[AliExpress] No API key set. Skipping AliExpress data.")
        return []
    try:
        import aliexpress_api
        from aliexpress_api import AliexpressApi, models
        api = AliexpressApi(ALI_APP_KEY, ALI_APP_SECRET, models.Language.FR, models.Currency.EUR, "FR")
        items = api.search_products(
            keywords=keyword,
            sort=models.SortBy.LAST_VOLUME_DESC,
            max_sale_price=10000,
            locale="FR",
            page_size=limit,
        )
        if not items:
            return []
        return [{
            "keyword": keyword,
            "product_id": item.product_id,
            "title": item.product_title,
            "price": item.target_sale_price,
            "orders": getattr(item, "lastest_volume", 0),
            "rating": getattr(item, "evaluate_rate", 0),
        } for item in items]
    except Exception as e:
        print(f"[AliExpress] Error: {e}")
        return []


def get_demand_score(keyword: str) -> float:
    """
    Returns a 0-5 demand score based on order volume for a keyword.
    Used as a lightweight demand signal.
    """
    products = search_products(keyword, limit=5)
    if not products:
        return 0.0
    orders = [p.get("orders", 0) for p in products if p.get("orders")]
    if not orders:
        return 0.0
    avg_orders = sum(orders) / len(orders)
    if avg_orders > 10000:
        return 5.0
    elif avg_orders > 5000:
        return 4.0
    elif avg_orders > 1000:
        return 3.0
    elif avg_orders > 100:
        return 2.0
    return 1.0


if __name__ == "__main__":
    print(get_demand_score("car seat gap filler"))
