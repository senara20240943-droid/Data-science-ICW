import streamlit as st
import pandas as pd
import plotly.express as px
st.set_page_config(page_title="Proportion of local breeds classified as being at risk of extinction", layout="wide")

@st.cache_data
def load_data():
    return pd.read_csv("clean.csv")

df = load_data()

# ── Sidebar filters ───────────────────────────────────────────
st.sidebar.title("Filters")

countries = sorted(df["country"].unique())
selected_countries = st.sidebar.multiselect("Countries", countries, default=countries)

year_min, year_max = int(df["year"].min()), int(df["year"].max())
year_range = st.sidebar.slider("Year Range", year_min, year_max, (year_min, year_max))

# ── Title ─────────────────────────────────────────────────────
st.title("Local Breeds at Risk of Extinction")
st.markdown("**SDG Indicator 2.5.2** — Proportion of local breeds classified as being at risk of extinction.")

# ── KPIs ──────────────────────────────────────────────────────
col1, col2, col3 = st.columns(3)
col1.metric("Countries", filtered["country"].nunique())
col2.metric("Year Range", f"{year_range[0]} – {year_range[1]}")
col3.metric("Avg % At Risk", f"{filtered['pct_at_risk'].mean():.1f}%")

st.divider()