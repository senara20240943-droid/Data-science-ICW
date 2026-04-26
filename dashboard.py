

import streamlit as st
import pandas as pd
import plotly.express as px

#Page configuration
# Sets the browser tab title, icon and uses full screen width
st.set_page_config(page_title="Breeds at Risk Dashboard", page_icon="🐄", layout="wide")

#Custom CSS styling
# Applies dark background, white headings and styled KPI cards
st.markdown("""
    <style>
    .main { background-color: #0e0e0e; }
    .block-container { padding-top: 2rem; }
    h1, h2, h3 { color: #ffffff; }
    [data-testid="stMetric"] {
        background-color: #1a1a1a;
        border: 1px solid #166534;
        border-radius: 12px;
        padding: 15px;
    }
    [data-testid="stMetricLabel"] { color: #aaaaaa; font-size: 13px; }
    [data-testid="stMetricValue"] { color: #4ade80; font-size: 28px; font-weight: bold; }
    .stSidebar { background-color: #111111; }
    </style>
""", unsafe_allow_html=True)

# ── Load data ─────────────────────────────────────────────────
# Reads the cleaned CSV file into a pandas dataframe
# cache_data means the file is only read once and reused on filter changes
@st.cache_data
def load_data():
    return pd.read_csv("clean.csv")

df = load_data()


# ── Sidebar ───────────────────────────────────────────────────
# Creates interactive controls in the sidebar for the user to filter data
st.sidebar.title("🔍 Filters")
# Multiselect dropdown — user can pick one or more countries
selected_countries = st.sidebar.multiselect("🌍 Countries", sorted(df["country"].unique()), default=sorted(df["country"].unique()))
# Slider — user picks a start and end year
year_range = st.sidebar.slider("📅 Year Range", int(df["year"].min()), int(df["year"].max()), (int(df["year"].min()), int(df["year"].max())))
st.sidebar.info("Source: UN SDG 2.5.2 via World Bank Data360")


# ── Filter ────────────────────────────────────────────────────
filtered = df[df["country"].isin(selected_countries) & df["year"].between(year_range[0], year_range[1])]


# ── Header ────────────────────────────────────────────────────
st.markdown("# 🐄 Local Breeds at Risk of Extinction")
st.markdown("**SDG Indicator 2.5.2** — Proportion of local breeds classified as being at risk of extinction.")
st.markdown("---")


# ── KPIs ──────────────────────────────────────────────────────
# Displays 4 summary statistics side by side at the top of the dashboard
col1, col2, col3, col4 = st.columns(4)
col1.metric("🌍 Countries", filtered["country"].nunique())
col2.metric("📅 Years", f"{year_range[0]} – {year_range[1]}")
col3.metric("📊 Avg % At Risk", f"{filtered['pct_at_risk'].mean():.1f}%")
col4.metric("📈 Max % At Risk", f"{filtered['pct_at_risk'].max():.1f}%")
st.markdown("---")


# ── Shared chart style ────────────────────────────────────────
# Defines shared colours and gradient scale used across all charts
BG = "#0e0e0e"
GRID = "#14532d"
GREEN = "#4ade80"
YELLOW = "#fef08a"
SCALE = ["#052e16", "#166534", "#4ade80", "#d9f99d", "#fef08a"]
# Applies consistent dark styling to every chart to match the theme
def dark_layout(fig):
    fig.update_layout(
        plot_bgcolor=BG, paper_bgcolor=BG,
        font=dict(color="#ffffff"),
        xaxis=dict(gridcolor=GRID, zerolinecolor=GRID),
        yaxis=dict(gridcolor=GRID, zerolinecolor=GRID),
        margin=dict(t=40, b=40, l=40, r=40)
    )
    return fig

# ── Chart 1: Area trend (green) ───────────────────────────────
# Shows how the global average % at risk has changed year by year
st.subheader("📈 Global Trend Over Time")
trend = filtered.groupby("year")["pct_at_risk"].mean().reset_index()
fig1 = px.area(trend, x="year", y="pct_at_risk",
               labels={"pct_at_risk": "Avg % At Risk", "year": "Year"},
               color_discrete_sequence=[GREEN])
fig1.update_traces(line=dict(width=2.5), fillcolor="rgba(74,222,128,0.15)")
st.plotly_chart(dark_layout(fig1), use_container_width=True)

# ── Chart 2 & 3 side by side ──────────────────────────────────
col_a, col_b = st.columns(2)

with col_a:
    # Chart 2: Horizontal bar chart of top 15 countries for the latest year
    st.subheader("📊 Top 15 Countries")
    latest_year = filtered["year"].max()
    top15 = filtered[filtered["year"] == latest_year].sort_values("pct_at_risk", ascending=False).head(15)
    fig2 = px.bar(top15, x="pct_at_risk", y="country", orientation="h",
                  color="pct_at_risk", color_continuous_scale=SCALE,
                  labels={"pct_at_risk": "% At Risk", "country": "Country"})
    fig2.update_layout(coloraxis_showscale=False)
    fig2.update_yaxes(autorange="reversed", gridcolor=GRID)
    st.plotly_chart(dark_layout(fig2), use_container_width=True)

with col_b:
    # Chart 3: Histogram showing how % at risk values are spread
    st.subheader("📉 Distribution of % At Risk")
    fig3 = px.histogram(filtered, x="pct_at_risk", nbins=30,
                        labels={"pct_at_risk": "% At Risk"},
                        color_discrete_sequence=[GREEN])
    fig3.update_traces(marker_line_color=BG, marker_line_width=1)
    st.plotly_chart(dark_layout(fig3), use_container_width=True)

# ── Chart 4: Box plot ─────────────────────────────────────────
# Shows the spread and outliers of % at risk grouped by decade
st.subheader("📦 Spread of % At Risk by Decade")
filtered["decade"] = (filtered["year"] // 10 * 10).astype(str) + "s"
fig4 = px.box(filtered, x="decade", y="pct_at_risk",
              color="decade",
              color_discrete_sequence=[GREEN, "#86efac", "#d9f99d", YELLOW, GREEN],
              labels={"pct_at_risk": "% At Risk", "decade": "Decade"})
fig4.update_layout(showlegend=False)
st.plotly_chart(dark_layout(fig4), use_container_width=True)

# ── Chart 5: Tree map ──────────────────────────────────
# Shows each country as a box — larger box = higher % at risk
st.subheader("🟩 Treemap of % At Risk by Country")
latest = filtered[filtered["year"] == filtered["year"].max()]
latest = latest[latest["pct_at_risk"] > 0]

if latest.empty:
    st.info("No at-risk data available for the current filter selection.")
else:
    fig = px.treemap(latest, path=["country"], values="pct_at_risk",
                     color="pct_at_risk",
                     color_continuous_scale="Aggrnyl",
                     labels={"pct_at_risk": "% At Risk"})
    fig.update_layout(paper_bgcolor=BG, font=dict(color="#ffffff"),
                      margin=dict(t=40, b=40, l=40, r=40))
    st.plotly_chart(fig, use_container_width=True)


# ── Chart 6: Map ──────────────────────────────────────────────
# Choropleth map — countries coloured by their average % at risk
st.subheader("🗺️ World Map — % Breeds at Risk")
map_data = filtered.groupby("country")["pct_at_risk"].mean().reset_index()
fig6 = px.choropleth(map_data, locations="country", locationmode="country names",
                     color="pct_at_risk", color_continuous_scale=SCALE,
                     labels={"pct_at_risk": "Avg % At Risk"})
fig6.update_layout(
    paper_bgcolor=BG, font=dict(color="#ffffff"),
    geo=dict(bgcolor=BG, landcolor="#052e16", oceancolor="#0a0a0a",
             showocean=True, showcoastlines=True, coastlinecolor=YELLOW,
             showframe=True, framecolor=GREEN,
             projection_type="natural earth"),
    margin=dict(t=40, b=40)
)
st.plotly_chart(fig6, use_container_width=True)

# ── Raw data ──────────────────────────────────────────────────
# Hidden by default — click to expand and view the filtered dataset as a table
with st.expander("📄 View Raw Data"):
    st.dataframe(filtered, use_container_width=True)

st.markdown("---")
st.caption("📌 Source: UN SDG Indicator 2.5.2 via World Bank Data360 | Built with Streamlit")