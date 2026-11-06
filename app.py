from pathlib import Path
import os
import pandas as pd
import streamlit as st
import plotly.express as px
from fred_client import fetch_fred_series
from macro_engine import add_time_series_metrics, flag_unusual_changes

st.set_page_config(page_title="MacroPulse | Economic Data", page_icon="📈", layout="wide")
ROOT = Path(__file__).parent
SAMPLE = ROOT / "data" / "macro_observations.csv"
SERIES = {"CPIAUCSL": "US CPI (index)", "UNRATE": "US Unemployment Rate (%)", "FEDFUNDS": "Federal Funds Rate (%)", "DGS10": "10-Year Treasury Yield (%)"}

st.title("MacroPulse — Economic Data Intelligence")
st.caption("Explore macroeconomic time series, calculate changes and flag unusual movements.")

with st.sidebar:
    st.header("Data source")
    source_mode = st.radio("Choose data", ["Sample dataset", "Fetch from FRED API", "Upload CSV"])
    upload = st.file_uploader("Upload macro CSV", type=["csv"]) if source_mode == "Upload CSV" else None
    selected_series = st.multiselect("FRED series", list(SERIES.keys()), default=["CPIAUCSL", "UNRATE", "FEDFUNDS"]) if source_mode == "Fetch from FRED API" else []
    st.caption("FRED mode requires a free API key in the FRED_API_KEY environment variable.")

if source_mode == "Sample dataset":
    df = pd.read_csv(SAMPLE)
elif source_mode == "Upload CSV":
    if upload is None:
        st.info("Upload a CSV with date, country, series, value, unit and source columns.")
        st.stop()
    df = pd.read_csv(upload)
else:
    api_key = os.getenv("FRED_API_KEY", "")
    if not api_key:
        st.error("FRED_API_KEY is not set. Add your FRED API key to the environment, then restart Streamlit.")
        st.stop()
    if not selected_series:
        st.warning("Select at least one FRED series in the sidebar.")
        st.stop()
    frames = []
    for series_id in selected_series:
        try:
            frames.append(fetch_fred_series(series_id, api_key))
        except Exception as exc:
            st.error(f"Could not fetch {series_id}: {exc}")
    if not frames:
        st.stop()
    df = pd.concat(frames, ignore_index=True)

required = ["date", "country", "series", "value", "unit", "source"]
missing = [c for c in required if c not in df.columns]
if missing:
    st.error("Missing required columns: " + ", ".join(missing))
    st.stop()

try:
    enriched = add_time_series_metrics(df)
except ValueError as exc:
    st.error(str(exc))
    st.stop()

countries = sorted(enriched["country"].dropna().astype(str).unique())
country = st.selectbox("Country / region", countries)
subset = enriched[enriched["country"].astype(str) == country]
series_names = sorted(subset["series"].dropna().astype(str).unique())
series_name = st.selectbox("Indicator", series_names)
view = subset[subset["series"].astype(str) == series_name].sort_values("date")

if view.empty:
    st.warning("No observations available for this selection.")
    st.stop()
latest = view.iloc[-1]
prev = view.iloc[-2] if len(view) > 1 else latest
m1, m2, m3 = st.columns(3)
m1.metric("Latest value", f"{latest['value']:,.3f} {latest['unit']}", f"{latest['date'].date()}")
m2.metric("Month-over-month change", "N/A" if pd.isna(latest["mom_change_pct"]) else f"{latest['mom_change_pct']:.2f}%")
m3.metric("Year-over-year change", "N/A" if pd.isna(latest["yoy_change_pct"]) else f"{latest['yoy_change_pct']:.2f}%")

st.subheader("Indicator history")
st.plotly_chart(px.line(view, x="date", y="value", markers=True, title=f"{series_name} — {country}"), use_container_width=True)

st.subheader("Unusual movements")
flags = flag_unusual_changes(view)
if flags.empty:
    st.info("No unusual movements flagged using the current rolling z-score rule.")
else:
    st.caption("Flags are statistical review prompts, not proof of an economic event or data error.")
    st.dataframe(flags, use_container_width=True, hide_index=True)

st.subheader("Processed observations")
st.dataframe(view, use_container_width=True, hide_index=True)
st.download_button("Download processed series", view.to_csv(index=False).encode("utf-8"), "macropulse_processed.csv", "text/csv")
