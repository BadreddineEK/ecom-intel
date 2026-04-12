# 🛒 EcomIntel — Product Intelligence Tool

> Spy on winning e-commerce products in France & Europe — Shopify scraper, Google Trends scoring, Meta Ads Library spy, AliExpress demand — all in one Streamlit dashboard.

![Python](https://img.shields.io/badge/Python-3.10+-blue) ![Streamlit](https://img.shields.io/badge/Streamlit-1.32+-red) ![License](https://img.shields.io/badge/License-MIT-green)

---

## 🎯 What it does

| Feature | Description |
|---|---|
| 🏪 **Shopify Scraper** | Scrapes public `/products.json` from any Shopify store — price, creation date, tags, variants |
| 📈 **Google Trends** | Scores each product keyword on Google Trends (France, 3 months) |
| 📣 **Meta Ads Spy** | Queries Facebook Ads Library API for active ads by keyword (France) |
| 🛍️ **AliExpress Demand** | Estimates order volume and rating via AliExpress API wrapper |
| 🧮 **Scoring Engine** | Combines all signals into a `/100` winning score per product |
| 📊 **Streamlit Dashboard** | Visual interface with filters, rankings, export CSV |
| ⏰ **Auto Scheduler** | GitHub Actions cron — runs every night, saves results |

---

## 🚀 Quick Start

### 1. Clone
```bash
git clone https://github.com/BadreddineEK/ecom-intel.git
cd ecom-intel
```

### 2. Install dependencies
```bash
pip install -r requirements.txt
```

### 3. Configure environment
```bash
cp .env.example .env
# Fill in your Meta Ads API token (free — see below)
```

### 4. Add your target Shopify stores
Edit `config/stores.txt` — one store slug per line:
```
gymshark
allbirds
sezane
cettecollection
```

### 5. Run the scraper
```bash
python run_scraper.py
```

### 6. Launch the dashboard
```bash
streamlit run dashboard/app.py
```

---

## 🔑 API Setup (all free)

### Meta Ads Library API
1. Go to [facebook.com/ads/library/api](https://www.facebook.com/ads/library/api/)
2. Log in with any Facebook account
3. Click **"Get Token"** — copy the access token
4. Paste in `.env` as `META_ADS_TOKEN=your_token_here`

### AliExpress API (optional)
1. Register at [AliExpress Affiliate Program](https://portals.aliexpress.com)
2. Get App Key + Secret
3. Paste in `.env` as `ALI_APP_KEY` and `ALI_APP_SECRET`

> Note: All Shopify scraping and Google Trends require **zero API keys**.

---

## 📁 Project Structure

```
ecom-intel/
├── config/
│   └── stores.txt          # Target Shopify stores list
├── scrapers/
│   ├── shopify_scraper.py  # Shopify /products.json scraper
│   ├── trends_scraper.py   # Google Trends via pytrends
│   ├── meta_ads_spy.py     # Facebook Ads Library API
│   └── aliexpress_api.py   # AliExpress demand data
├── engine/
│   └── scorer.py           # Scoring engine (/100)
├── dashboard/
│   └── app.py              # Streamlit dashboard
├── data/
│   └── results.csv         # Auto-generated output
├── .github/
│   └── workflows/
│       └── daily_scan.yml  # GitHub Actions cron scheduler
├── run_scraper.py          # Main entry point
├── requirements.txt
├── .env.example
└── README.md
```

---

## 🧮 Scoring Formula

Each product receives a score from **0 to 100** based on:

| Signal | Weight | Description |
|---|---|---|
| Google Trends score | 35% | Average interest FR last 3 months |
| Recency (days since creation) | 25% | Newer products score higher |
| Multi-store presence | 20% | Same product on 3+ stores = validated |
| Meta Ads active | 15% | Active ads running >14 days = scaling signal |
| AliExpress orders | 5% | High order count = demand proof |

---

## 📊 Dashboard Preview

The Streamlit dashboard shows:
- 🏆 **Top 10 winning products** of the day (sorted by score)
- 📉 **Trend chart** per product keyword
- 🔎 **Filters** : category, min score, price range, store
- 💾 **Export CSV** button
- 📣 **Meta Ads preview** : nb active ads, ad age

---

## ⚙️ GitHub Actions — Daily Auto Scan

The workflow in `.github/workflows/daily_scan.yml` runs every night at 02:00 (Paris time):
```yaml
schedule:
  - cron: '0 1 * * *'  # 02:00 CET
```
Results are saved in `data/results.csv` and committed automatically.

---

## ⚠️ Ethical & Legal Notes

- Shopify `/products.json` is publicly accessible by design (no auth required)
- Meta Ads Library API is an **official Meta API** — fully legal
- Google Trends is accessed via `pytrends` (public data)
- **Do not use this tool to copy protected content or infringe trademarks**
- Respect `robots.txt` and rate limits on all scrapers

---

## 🛣️ Roadmap

- [ ] Etsy scraper (top sellers France)
- [ ] TikTok Creative Center integration
- [ ] Price history tracker per product
- [ ] Slack/email alert when score > 80
- [ ] Multi-country support (BE, CH, MA)
- [ ] AI product description generator (OpenAI API)

---

## 📄 License

MIT — free to use, modify and distribute.

---

> Built for serious e-commerce entrepreneurs who want data over guesswork.
