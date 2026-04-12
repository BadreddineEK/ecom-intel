import os
import requests
import pandas as pd
from datetime import datetime
from dotenv import load_dotenv

load_dotenv()

META_ADS_TOKEN = os.getenv("META_ADS_TOKEN", "")
META_API_BASE = "https://graph.facebook.com/v19.0/ads_archive"


def search_ads(
    keyword: str,
    country: str = "FR",
    limit: int = 20,
    active_only: bool = True,
) -> list[dict]:
    """
    Search Facebook Ads Library for active ads matching a keyword in France.
    Returns a list of ad metadata dicts.
    """
    if not META_ADS_TOKEN:
        print("[Meta Ads] No token set. Add META_ADS_TOKEN to .env")
        return []

    params = {
        "access_token": META_ADS_TOKEN,
        "ad_reached_countries": country,
        "ad_active_status": "ACTIVE" if active_only else "ALL",
        "search_terms": keyword,
        "ad_delivery_date_min": "",
        "fields": "id,ad_creative_body,ad_snapshot_url,ad_delivery_start_time,ad_delivery_stop_time,page_name,currency,impressions",
        "limit": limit,
    }

    try:
        r = requests.get(META_API_BASE, params=params, timeout=15)
        data = r.json()
        if "error" in data:
            print(f"[Meta Ads] API error: {data['error']['message']}")
            return []
        ads = data.get("data", [])
        results = []
        for ad in ads:
            start = ad.get("ad_delivery_start_time", "")
            days_running = 0
            if start:
                try:
                    days_running = (
                        datetime.now()
                        - datetime.fromisoformat(start.replace("Z", "+00:00")).replace(tzinfo=None)
                    ).days
                except Exception:
                    pass
            results.append({
                "keyword": keyword,
                "ad_id": ad.get("id"),
                "page_name": ad.get("page_name", ""),
                "start_date": start,
                "days_running": days_running,
                "snapshot_url": ad.get("ad_snapshot_url", ""),
            })
        return results
    except Exception as e:
        print(f"[Meta Ads] Request error: {e}")
        return []


def get_ads_signal(keyword: str) -> dict:
    """
    Return a summary signal dict for a keyword:
    - nb_active_ads: total active ads
    - avg_days_running: average duration of running ads (scaling signal)
    - has_scaling_ads: True if any ad running >14 days
    """
    ads = search_ads(keyword)
    if not ads:
        return {"nb_active_ads": 0, "avg_days_running": 0, "has_scaling_ads": False}
    df = pd.DataFrame(ads)
    return {
        "nb_active_ads": len(df),
        "avg_days_running": round(df["days_running"].mean(), 1),
        "has_scaling_ads": bool((df["days_running"] > 14).any()),
    }


if __name__ == "__main__":
    signal = get_ads_signal("organisateur cuisine")
    print(signal)
