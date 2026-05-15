"""Department Focus — single-department deep dive."""
from __future__ import annotations

import streamlit as st

st.set_page_config(page_title="Department · Talent Pulse", page_icon="🏢", layout="wide")

from src.theme import inject_global_css
inject_global_css()

from dotenv import load_dotenv
load_dotenv()

from src.data import load_staffing_data, load_source_breakdown, filter_data
from src.kpis import compute_period_kpis, top_recruiters
from src.charts import heatmap_dept_role, source_breakdown_bar

df_all = load_staffing_data()
source_all = load_source_breakdown()

all_depts = sorted(df_all["Department"].unique().tolist())
min_month = df_all["Month"].min().date()
max_month = df_all["Month"].max().date()

with st.sidebar:
    st.header("Filters")
    selected_dept = st.selectbox("Department", options=all_depts, index=0)
    date_range = st.date_input(
        "Date Range",
        value=(min_month, max_month),
        min_value=min_month,
        max_value=max_month,
    )
    df = filter_data(df_all, departments=[selected_dept], date_range=date_range)
    source_df = filter_data(source_all, departments=[selected_dept], date_range=date_range)
    st.caption(f"{len(df):,} rows in view")

st.markdown('<p class="eyebrow">DEPARTMENT FOCUS</p>', unsafe_allow_html=True)
st.title(f"{selected_dept}")

if df.empty:
    st.info("No data for this filter combination.")
    st.stop()

# ── KPI strip ─────────────────────────────────────────────────────────────────
kpis = compute_period_kpis(df)
c1, c2, c3, c4 = st.columns(4)
with c1:
    st.metric("Total Hires", f"{kpis['hires']:,}")
with c2:
    st.metric("Applicants", f"{kpis['applicants']:,}")
with c3:
    st.metric("Avg Time to Fill", f"{kpis['avg_ttf']} days")
with c4:
    st.metric("Avg Cost per Hire", f"${kpis['avg_cost_per_hire']:,.0f}")

st.divider()

# ── Heatmaps ───────────────────────────────────────────────────────────────────
col_h, col_t = st.columns(2)

with col_h:
    st.subheader("Hires — Role × Month")
    fig_hires = heatmap_dept_role(df, "Hires")
    st.plotly_chart(fig_hires, use_container_width=True)

with col_t:
    st.subheader("Time to Fill — Role × Month")
    fig_ttf = heatmap_dept_role(df, "Avg Time to Fill (days)")
    st.plotly_chart(fig_ttf, use_container_width=True)

st.divider()

# ── Recruiters + source breakdown ─────────────────────────────────────────────
col_r, col_s = st.columns([1, 2])

with col_r:
    st.subheader("Top Recruiters")
    rec_df = top_recruiters(df, n=5)
    if rec_df.empty:
        st.info("No recruiter data.")
    else:
        st.dataframe(
            rec_df,
            use_container_width=True,
            hide_index=True,
            column_config={
                "Hires": st.column_config.ProgressColumn(
                    "Hires",
                    min_value=0,
                    max_value=int(rec_df["Hires"].max()),
                    format="%d",
                ),
            },
        )

with col_s:
    st.subheader("Applicant Sources")
    if source_df.empty:
        st.info("No source data for this filter.")
    else:
        fig_source = source_breakdown_bar(source_df)
        st.plotly_chart(fig_source, use_container_width=True)
