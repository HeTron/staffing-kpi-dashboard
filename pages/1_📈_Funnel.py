"""Pipeline Analysis — full funnel breakdown."""
from __future__ import annotations

import streamlit as st

st.set_page_config(page_title="Funnel · Talent Pulse", page_icon="📈", layout="wide")

from src.theme import inject_global_css
inject_global_css()

from dotenv import load_dotenv
load_dotenv()

from src.data import load_staffing_data, load_source_breakdown, filter_data
from src.kpis import funnel_conversion_rates, funnel_by_department, compute_period_kpis
from src.charts import funnel_chart, sankey_funnel

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
    st.caption(f"{len(df):,} rows in view")

st.markdown('<p class="eyebrow">PIPELINE ANALYSIS</p>', unsafe_allow_html=True)
st.title("Hiring Funnel")

if df.empty:
    st.info("No data for this filter combination.")
    st.stop()

kpis = compute_period_kpis(df)
rates = funnel_conversion_rates(df)

# ── Conversion rate KPIs ───────────────────────────────────────────────────────
st.subheader("Conversion Rates")
c1, c2, c3, c4 = st.columns(4)
with c1:
    st.metric("App → Interview", f"{rates['app_to_int']:.1%}")
with c2:
    st.metric("Interview → Offer", f"{rates['int_to_off']:.1%}")
with c3:
    st.metric("Offer → Hire", f"{rates['off_to_hire']:.1%}")
with c4:
    st.metric("Overall (App → Hire)", f"{rates['overall']:.1%}")

st.divider()

# ── Funnel chart + sankey side by side ────────────────────────────────────────
col_f, col_s = st.columns(2)

with col_f:
    st.subheader("Funnel Chart")
    stages = {
        "Applicants": kpis["applicants"],
        "Interviews": kpis["interviews"],
        "Offers": kpis["offers"],
        "Hires": kpis["hires"],
    }
    fig_funnel = funnel_chart(stages)
    st.plotly_chart(fig_funnel, use_container_width=True)

with col_s:
    st.subheader("Pipeline Sankey")
    fig_sankey = sankey_funnel(df)
    st.plotly_chart(fig_sankey, use_container_width=True)

st.divider()

# ── Funnel by department table ─────────────────────────────────────────────────
st.subheader("Funnel by Department")
dept_df = funnel_by_department(df)

# Add visual bar column for hires
max_hires = dept_df["Hires"].max() if dept_df["Hires"].max() > 0 else 1
dept_df["Hire Rate"] = (dept_df["Hires"] / dept_df["Applicants"].replace(0, 1)).round(4)
dept_df["Hire Rate %"] = dept_df["Hire Rate"].apply(lambda x: f"{x:.1%}")

st.dataframe(
    dept_df[["Department", "Applicants", "Interviews", "Offers", "Hires", "Hire Rate %"]],
    use_container_width=True,
    hide_index=True,
    column_config={
        "Hires": st.column_config.ProgressColumn(
            "Hires",
            min_value=0,
            max_value=int(max_hires),
            format="%d",
        ),
    },
)
