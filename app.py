import streamlit as st
import pandas as pd
import plotly.express as px

st.set_page_config(page_title="Breeds at Risk Dashboard", page_icon="🐄", layout="wide")

@st.cache_data
def load_data():
    return pd.read_csv("/Users/senarajayawardena/Desktop/IIT 2y/SEM 02/Data Science /ICW/Data Science/clean.csv")

df = load_data()

# ── Sidebar filters ───────────────────────────────────────────
st.sidebar.title("Filters")

countries = sorted(df["country"].unique())
selected_countries = st.sidebar.multiselect("Countries", countries, default=countries)

year_min, year_max = int(df["year"].min()), int(df["year"].max())
year_range = st.sidebar.slider("Year Range", year_min, year_max, (year_min, year_max))

# ── Filter data ───────────────────────────────────────────────
filtered = df[
    (df["country"].isin(selected_countries)) &
    (df["year"] >= year_range[0]) &
    (df["year"] <= year_range[1])
]

# ── Title ─────────────────────────────────────────────────────
st.title("🐄 Local Breeds at Risk of Extinction")
st.markdown("**SDG Indicator 2.5.2** — Proportion of local breeds classified as being at risk of extinction.")

# ── KPIs ──────────────────────────────────────────────────────
col1, col2, col3 = st.columns(3)
col1.metric("Countries", filtered["country"].nunique())
col2.metric("Year Range", f"{year_range[0]} – {year_range[1]}")
col3.metric("Avg % At Risk", f"{filtered['pct_at_risk'].mean():.1f}%")

st.divider()

# ── Chart 1: Global trend over time ───────────────────────────
st.subheader("📈 Global Trend Over Time")
trend = filtered.groupby("year")["pct_at_risk"].mean().reset_index()
fig1 = px.line(trend, x="year", y="pct_at_risk",
               labels={"pct_at_risk": "Avg % At Risk", "year": "Year"},
               markers=True)
st.plotly_chart(fig1, use_container_width=True)

# ── Chart 2: Top 15 countries ─────────────────────────────────
st.subheader("📊 Top 15 Countries (Latest Year)")
latest = filtered[filtered["year"] == filtered["year"].max()]
top15 = latest.sort_values("pct_at_risk", ascending=False).head(15)
fig2 = px.bar(top15, x="country", y="pct_at_risk",
              color="pct_at_risk", color_continuous_scale="Reds",
              labels={"pct_at_risk": "% At Risk", "country": "Country"})
st.plotly_chart(fig2, use_container_width=True)

# ── Chart 3: World map ────────────────────────────────────────
st.subheader("🗺️ World Map — % Breeds at Risk")
map_data = filtered.groupby("country")["pct_at_risk"].mean().reset_index()
fig3 = px.choropleth(map_data, locations="country", locationmode="country names",
                     color="pct_at_risk", color_continuous_scale="YlOrRd",
                     labels={"pct_at_risk": "Avg % At Risk"})
st.plotly_chart(fig3, use_container_width=True)

# ── Chart 4: Distribution ─────────────────────────────────────
st.subheader("📉 Distribution of % At Risk Values")
fig4 = px.histogram(filtered, x="pct_at_risk", nbins=30,
                    labels={"pct_at_risk": "% At Risk"},
                    color_discrete_sequence=["teal"])
st.plotly_chart(fig4, use_container_width=True)

# ── Raw data ──────────────────────────────────────────────────
with st.expander("View Raw Data"):
    st.dataframe(filtered, use_container_width=True)

st.caption("Source: UN SDG Indicator 2.5.2 via World Bank Data360")