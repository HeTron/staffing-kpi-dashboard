"""Talent Pulse — Overview (entry point)."""
from __future__ import annotations

import streamlit as st

st.set_page_config(
    page_title="Talent Pulse",
    page_icon="📊",
    layout="wide",
    initial_sidebar_state="expanded",
)

from src.theme import inject_global_css
inject_global_css()

from dotenv import load_dotenv
load_dotenv()

from src.data import load_staffing_data, load_source_breakdown, filter_data
from src.kpis import compute_period_kpis, compute_deltas, split_period, funnel_by_department
from src.charts import funnel_chart, metric_trend, dept_comparison_bar
from src.theme import ACCENT_AMBER, SUCCESS_GREEN, WARNING_RED, MUTED_SLATE

# ── Header ────────────────────────────────────────────────────────────────────
st.markdown('<p class="eyebrow">RECRUITING OPERATIONS INTELLIGENCE</p>', unsafe_allow_html=True)
st.title("Talent Pulse")
st.markdown("Real-time visibility into hiring funnel, recruiter performance, and pipeline health.")

st.divider()

# ── Load data ─────────────────────────────────────────────────────────────────
df_all = load_staffing_data()
source_all = load_source_breakdown()

all_depts = sorted(df_all["Department"].unique().tolist())
min_month = df_all["Month"].min().date()
max_month = df_all["Month"].max().date()

# ── Sidebar filters ───────────────────────────────────────────────────────────
with st.sidebar:
    st.header("Filters")
    selected_depts = st.multiselect(
        "Departments",
        options=all_depts,
        default=all_depts,
    )
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

if df.empty:
    st.info("No data for this filter combination.")
    st.stop()

# ── KPI strip ─────────────────────────────────────────────────────────────────
st.subheader("Key Metrics")

current, prior = split_period(df, lookback_months=3)
curr_kpis = compute_period_kpis(current)
prev_kpis = compute_period_kpis(prior) if not prior.empty else {}
deltas = compute_deltas(curr_kpis, prev_kpis) if prev_kpis else {}

c1, c2, c3, c4, c5 = st.columns(5)

def _fmt_delta(key: str, invert: bool = False) -> str | None:
    d = deltas.get(key)
    if d is None:
        return None
    pct = f"{d:+.1%}"
    return pct


with c1:
    st.metric("Applicants", f"{curr_kpis['applicants']:,}", delta=_fmt_delta("applicants"))
with c2:
    st.metric("Interviews", f"{curr_kpis['interviews']:,}", delta=_fmt_delta("interviews"))
with c3:
    st.metric("Offers", f"{curr_kpis['offers']:,}", delta=_fmt_delta("offers"))
with c4:
    st.metric("Hires", f"{curr_kpis['hires']:,}", delta=_fmt_delta("hires"))
with c5:
    # TTF: lower is better — invert display interpretation but keep raw delta
    st.metric(
        "Avg Time to Fill",
        f"{curr_kpis['avg_ttf']} days",
        delta=_fmt_delta("avg_ttf"),
        delta_color="inverse",
    )

st.divider()

# ── Funnel ─────────────────────────────────────────────────────────────────────
col_funnel, col_trend = st.columns([1, 2])

with col_funnel:
    st.subheader("Hiring Funnel")
    all_kpis = compute_period_kpis(df)
    stages = {
        "Applicants": all_kpis["applicants"],
        "Interviews": all_kpis["interviews"],
        "Offers": all_kpis["offers"],
        "Hires": all_kpis["hires"],
    }
    fig_funnel = funnel_chart(stages)
    st.plotly_chart(fig_funnel, use_container_width=True)

with col_trend:
    st.subheader("Monthly Hires by Department")
    from src.kpis import monthly_metric_by_dept
    pivot_hires = monthly_metric_by_dept(df, "Hires")
    if pivot_hires.empty:
        st.info("No trend data available.")
    else:
        fig_trend = metric_trend(pivot_hires, title="Monthly Hires", y_label="Hires")
        st.plotly_chart(fig_trend, use_container_width=True)

st.divider()

# ── Department comparison ──────────────────────────────────────────────────────
st.subheader("Department Performance — Total Hires")
fig_bar = dept_comparison_bar(df, metric="Hires", title="Total Hires by Department")
st.plotly_chart(fig_bar, use_container_width=True)

st.divider()

# ── Footer ────────────────────────────────────────────────────────────────────
st.caption(
    "Talent Pulse · Built by Jason Eid · "
    "[github.com/HeTron/staffing-kpi-dashboard](https://github.com/HeTron/staffing-kpi-dashboard)"
)
