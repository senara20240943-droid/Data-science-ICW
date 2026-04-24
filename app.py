import streamlit as st
import pandas as pd
import plotly.express as px

st.set_page_config(page_title="Breeds at Risk Dashboard", page_icon="🐄", layout="wide")

# ── Custom CSS ────────────────────────────────────────────────
st.markdown("""
    <style>
    .main { background-color: #f9f9f9; }
    .block-container { padding-top: 2rem; }
    h1 { color: #2c7a4b; }
    h2, h3 { color: #3a3a3a; }
    .metric-container { background-color: #ffffff; border-radius: 10px; padding: 10px; }
    [data-testid="stMetric"] {
        background-color: #ffffff;
        border: 1px solid #e0e0e0;
        border-radius: 10px;
        padding: 15px;
        box-shadow: 2px 2px 8px rgba(0,0,0,0.05);
    }
    [data-testid="stMetricLabel"] { font-size: 14px; color: #666; }
    [data-testid="stMetricValue"] { font-size: 28px; color: #2c7a4b; font-weight: bold; }
    .stSidebar { background-color: #f0f7f4; }
    </style>
""", unsafe_allow_html=True)

@st.cache_data
def load_data():
    return pd.read_csv("clean.csv")

df = load_data()

# ── Sidebar ───────────────────────────────────────────────────
st.sidebar.image("https://upload.wikimedia.org/wikipedia/commons/thumb/5/55/Emblem_of_the_United_Nations.svg/200px-Emblem_of_the_United_Nations.svg.png", width=60)
st.sidebar.title("🔍 Filters")
st.sidebar.markdown("---")

countries = sorted(df["country"].unique())
selected_countries = st.sidebar.multiselect("🌍 Select Countries", countries, default=countries)

year_min, year_max = int(df["year"].min()), int(df["year"].max())
year_range = st.sidebar.slider("📅 Year Range", year_min, year_max, (year_min, year_max))

st.sidebar.markdown("---")
st.sidebar.info("Data: UN SDG Indicator 2.5.2 via World Bank Data360")

# ── Filter ────────────────────────────────────────────────────
filtered = df[
    (df["country"].isin(selected_countries)) &
    (df["year"] >= year_range[0]) &
    (df["year"] <= year_range[1])
]

# ── Header ────────────────────────────────────────────────────
st.markdown("# 🐄 Local Breeds at Risk of Extinction")
st.markdown("**SDG Indicator 2.5.2** — Proportion of local breeds classified as being at risk of extinction across the world.")
st.markdown("---")

# ── KPIs ──────────────────────────────────────────────────────
col1, col2, col3, col4 = st.columns(4)
col1.metric("🌍 Countries", filtered["country"].nunique())
col2.metric("📅 Years Covered", f"{year_range[0]} – {year_range[1]}")
col3.metric("📊 Avg % At Risk", f"{filtered['pct_at_risk'].mean():.1f}%")
col4.metric("📈 Max % At Risk", f"{filtered['pct_at_risk'].max():.1f}%")

st.markdown("---")

# ── Chart 1: Trend ────────────────────────────────────────────
st.subheader("📈 Global Trend Over Time")
trend = filtered.groupby("year")["pct_at_risk"].mean().reset_index()
fig1 = px.line(trend, x="year", y="pct_at_risk",
               markers=True,
               labels={"pct_at_risk": "Avg % At Risk", "year": "Year"},
               color_discrete_sequence=["#2c7a4b"])
fig1.update_traces(line=dict(width=3), marker=dict(size=7))
fig1.update_layout(plot_bgcolor="white", paper_bgcolor="white",
                   yaxis=dict(gridcolor="#eeeeee"), xaxis=dict(gridcolor="#eeeeee"))
st.plotly_chart(fig1, use_container_width=True)

# ── Chart 2 & 3 side by side ──────────────────────────────────
col_a, col_b = st.columns(2)

with col_a:
    st.subheader("📊 Top 15 Countries")
    latest = filtered[filtered["year"] == filtered["year"].max()]
    top15 = latest.sort_values("pct_at_risk", ascending=False).head(15)
    fig2 = px.bar(top15, x="pct_at_risk", y="country", orientation="h",
                  color="pct_at_risk", color_continuous_scale="Reds",
                  labels={"pct_at_risk": "% At Risk", "country": "Country"})
    fig2.update_layout(plot_bgcolor="white", paper_bgcolor="white",
                       yaxis=dict(autorange="reversed"),
                       coloraxis_showscale=False)
    st.plotly_chart(fig2, use_container_width=True)

with col_b:
    st.subheader("📉 Distribution of % At Risk")
    fig4 = px.histogram(filtered, x="pct_at_risk", nbins=30,
                        labels={"pct_at_risk": "% At Risk"},
                        color_discrete_sequence=["#2c7a4b"])
    fig4.update_layout(plot_bgcolor="white", paper_bgcolor="white",
                       yaxis=dict(gridcolor="#eeeeee"))
    st.plotly_chart(fig4, use_container_width=True)

# ── Chart 4: Map ──────────────────────────────────────────────
st.subheader("🗺️ World Map — % Breeds at Risk")
map_data = filtered.groupby("country")["pct_at_risk"].mean().reset_index()
fig3 = px.choropleth(map_data, locations="country", locationmode="country names",
                     color="pct_at_risk", color_continuous_scale="YlOrRd",
                     labels={"pct_at_risk": "Avg % At Risk"})
fig3.update_layout(geo=dict(showframe=False, showcoastlines=True,
                            projection_type="natural earth"),
                   paper_bgcolor="white")
st.plotly_chart(fig3, use_container_width=True)

# ── Raw data ──────────────────────────────────────────────────
with st.expander("📄 View Raw Data"):
    st.dataframe(filtered, use_container_width=True)

st.markdown("---")
st.caption("📌 Source: UN SDG Indicator 2.5.2 via World Bank Data360 | Dashboard built with Streamlit")