"""AI Analysis — Claude-generated executive briefing."""
from __future__ import annotations

import streamlit as st

st.set_page_config(page_title="AI Insights · Talent Pulse", page_icon="🤖", layout="wide")

from src.theme import inject_global_css
inject_global_css()

from dotenv import load_dotenv
load_dotenv()

from src.data import load_staffing_data, load_source_breakdown, filter_data
from src.insights import generate_insights

df_all = load_staffing_data()
source_all = load_source_breakdown()

all_depts = sorted(df_all["Department"].unique().tolist())
min_month = df_all["Month"].min().date()
max_month = df_all["Month"].max().date()

with st.sidebar:
    st.header("Filters")
    selected_depts = st.multiselect("Departments", options=all_depts, default=all_depts)
    date_range = st.date_input(
        "Date Range",
        value=(min_month, max_month),
        min_value=min_month,
        max_value=max_month,
    )
    if not selected_depts:
        selected_depts = all_depts
    df = filter_data(df_all, departments=selected_depts, date_range=date_range)
    source_df = filter_data(source_all, departments=selected_depts, date_range=date_range)
    st.caption(f"{len(df):,} rows in view")

st.markdown('<p class="eyebrow">AI ANALYSIS</p>', unsafe_allow_html=True)
st.title("AI Insights")
st.markdown(
    "Claude reads your filtered recruiting data and writes an executive briefing. "
    "Approximately 5 seconds per generation."
)
st.caption(
    "Dashboard is fully functional without an API key — only this page requires `ANTHROPIC_API_KEY` in `.env`."
)

st.divider()

if df.empty:
    st.info("No data for this filter combination.")
    st.stop()

generate = st.button("Generate Insight", type="primary")

if generate:
    with st.spinner("Claude is analyzing your recruiting data..."):
        result = generate_insights(df, source_df)

    with st.container(border=True):
        st.markdown(result)
