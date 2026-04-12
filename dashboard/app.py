import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from pathlib import Path
import os
import sys

sys.path.append(str(Path(__file__).parent.parent))

from scrapers.trends_scraper import get_trend_score

DATA_PATH = Path("data/results.csv")

st.set_page_config(
    page_title="EcomIntel — Product Intelligence",
    page_icon="🛒",
    layout="wide",
    initial_sidebar_state="expanded",
)

# ─── Custom CSS ───────────────────────────────────────────────────────────────
st.markdown("""
<style>
    .metric-card {
        background: #f8f9fa;
        padding: 1rem;
        border-radius: 8px;
        border-left: 4px solid #ff4b4b;
    }
    .score-high { color: #00c48c; font-weight: bold; }
    .score-mid  { color: #ffa500; font-weight: bold; }
    .score-low  { color: #ff4b4b; font-weight: bold; }
</style>
""", unsafe_allow_html=True)

# ─── Header ───────────────────────────────────────────────────────────────────
st.title("🛒 EcomIntel — Product Intelligence Dashboard")
st.caption("Winning products radar | Shopify + Google Trends + Meta Ads + AliExpress")

# ─── Sidebar ──────────────────────────────────────────────────────────────────
with st.sidebar:
    st.header("⚙️ Filters")
    min_score = st.slider("Min score", 0, 100, 40)
    max_price = st.slider("Max price (€)", 5, 500, 150)
    show_scaling_only = st.checkbox("Scaling Meta Ads only", value=False)
    top_n = st.selectbox("Show top N products", [10, 25, 50, 100], index=0)
    st.divider()
    st.header("🔍 Quick Trend Check")
    manual_kw = st.text_input("Enter a keyword")
    if st.button("Check Trend") and manual_kw:
        with st.spinner("Fetching Google Trends..."):
            score = get_trend_score(manual_kw)
        st.metric("Trend Score (FR, 3m)", f"{score}/100")

# ─── Load data ────────────────────────────────────────────────────────────────
if not DATA_PATH.exists():
    st.warning("""
    ⚠️ No data found. Run the scraper first:
    ```bash
    python run_scraper.py
    ```
    """)
    st.stop()

df = pd.read_csv(DATA_PATH)

# ─── Apply filters ────────────────────────────────────────────────────────────
df = df[df["final_score"] >= min_score]
if "price_min" in df.columns:
    df = df[df["price_min"] <= max_price]
if show_scaling_only and "has_scaling_ads" in df.columns:
    df = df[df["has_scaling_ads"] == True]

df = df.sort_values("final_score", ascending=False).head(top_n)

# ─── KPI Row ──────────────────────────────────────────────────────────────────
col1, col2, col3, col4 = st.columns(4)
col1.metric("🏆 Products analyzed", len(df))
col2.metric("📈 Avg score", f"{df['final_score'].mean():.1f}/100" if not df.empty else "—")
if "nb_active_ads" in df.columns:
    col3.metric("📣 Total active ads", int(df["nb_active_ads"].sum()))
if "trend_score" in df.columns:
    col4.metric("🔥 Avg trend score", f"{df['trend_score'].mean():.1f}")

st.divider()

# ─── Top Products Table ───────────────────────────────────────────────────────
st.subheader("🏆 Top Winning Products")

def color_score(val):
    color = "#00c48c" if val >= 70 else ("#ffa500" if val >= 45 else "#ff4b4b")
    return f"color: {color}; font-weight: bold"

display_cols = [c for c in [
    "title", "store", "price_min", "final_score",
    "trend_score", "nb_active_ads", "has_scaling_ads", "days_since_creation"
] if c in df.columns]

if not df.empty:
    styled = df[display_cols].style.applymap(color_score, subset=["final_score"])
    st.dataframe(styled, use_container_width=True, height=400)
else:
    st.info("No products match your filters.")

st.divider()

# ─── Score Distribution ───────────────────────────────────────────────────────
if not df.empty and "final_score" in df.columns:
    col_a, col_b = st.columns(2)

    with col_a:
        st.subheader("📊 Score Distribution")
        fig_hist = px.histogram(
            df, x="final_score", nbins=20,
            title="Distribution of winning scores",
            labels={"final_score": "Score /100"},
            color_discrete_sequence=["#ff4b4b"]
        )
        st.plotly_chart(fig_hist, use_container_width=True)

    with col_b:
        st.subheader("🏪 Products by Store")
        if "store" in df.columns:
            store_counts = df["store"].value_counts().reset_index()
            store_counts.columns = ["store", "count"]
            fig_bar = px.bar(
                store_counts.head(10),
                x="store", y="count",
                title="Top stores by winning products",
                color_discrete_sequence=["#ff4b4b"]
            )
            st.plotly_chart(fig_bar, use_container_width=True)

st.divider()

# ─── Trend vs Score scatter ────────────────────────────────────────────────────
if not df.empty and "trend_score" in df.columns:
    st.subheader("📈 Trend Score vs Winning Score")
    fig_scatter = px.scatter(
        df,
        x="trend_score", y="final_score",
        hover_data=["title", "store", "price_min"],
        color="final_score",
        color_continuous_scale="RdYlGn",
        title="Each dot = 1 product | Top-right = best candidates",
        labels={"trend_score": "Google Trends Score", "final_score": "Winning Score"},
    )
    st.plotly_chart(fig_scatter, use_container_width=True)

st.divider()

# ─── Export ───────────────────────────────────────────────────────────────────
st.subheader("💾 Export")
col_dl1, col_dl2 = st.columns(2)
with col_dl1:
    csv = df.to_csv(index=False).encode("utf-8")
    st.download_button("⬇️ Download CSV", csv, "ecom_intel_results.csv", "text/csv")
with col_dl2:
    if st.button("🔄 Refresh Data"):
        st.rerun()
