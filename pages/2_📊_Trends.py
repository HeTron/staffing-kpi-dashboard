"""Time Series — volume, quality, and cost trends."""
from __future__ import annotations

import streamlit as st

st.set_page_config(page_title="Trends · Talent Pulse", page_icon="📊", layout="wide")

from src.theme import inject_global_css
inject_global_css()

from dotenv import load_dotenv
load_dotenv()

from src.data import load_staffing_data, filter_data
from src.kpis import monthly_metric_by_dept
from src.charts import metric_trend

df_all = load_staffing_data()

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

st.markdown('<p class="eyebrow">TIME SERIES</p>', unsafe_allow_html=True)
st.title("Trends")

if df.empty:
    st.info("No data for this filter combination.")
    st.stop()

tab_volume, tab_quality, tab_cost = st.tabs(["Volume", "Quality", "Cost"])

with tab_volume:
    st.subheader("Applicant Volume")
    pivot_app = monthly_metric_by_dept(df, "Applicants")
    if not pivot_app.empty:
        st.plotly_chart(
            metric_trend(pivot_app, "Monthly Applicants by Department", "Applicants"),
            use_container_width=True,
        )

    st.subheader("Hires")
    pivot_hire = monthly_metric_by_dept(df, "Hires")
    if not pivot_hire.empty:
        st.plotly_chart(
            metric_trend(pivot_hire, "Monthly Hires by Department", "Hires"),
            use_container_width=True,
        )

    col_a, col_b = st.columns(2)
    with col_a:
        st.metric("Total Applicants", f"{df['Applicants'].sum():,}")
        st.metric("Total Hires", f"{df['Hires'].sum():,}")
    with col_b:
        st.metric("Avg Applicants / Month", f"{df.groupby('Month')['Applicants'].sum().mean():,.0f}")
        st.metric("Avg Hires / Month", f"{df.groupby('Month')['Hires'].sum().mean():,.1f}")

with tab_quality:
    st.subheader("Offer Acceptance Rate")
    pivot_oar = monthly_metric_by_dept(df, "Offer Acceptance Rate")
    if not pivot_oar.empty:
        st.plotly_chart(
            metric_trend(pivot_oar, "Monthly Offer Acceptance Rate by Department", "Offer Acceptance Rate"),
            use_container_width=True,
        )

    st.subheader("Avg Time to Fill (days)")
    pivot_ttf = monthly_metric_by_dept(df, "Avg Time to Fill (days)")
    if not pivot_ttf.empty:
        st.plotly_chart(
            metric_trend(pivot_ttf, "Monthly Avg Time to Fill by Department", "Days"),
            use_container_width=True,
        )

    col_a, col_b = st.columns(2)
    with col_a:
        st.metric("Avg Offer Acceptance Rate", f"{df['Offer Acceptance Rate'].mean():.1%}")
    with col_b:
        st.metric("Avg Time to Fill", f"{df['Avg Time to Fill (days)'].mean():.1f} days")

with tab_cost:
    st.subheader("Cost per Hire")
    pivot_cost = monthly_metric_by_dept(df, "Cost per Hire ($)")
    if not pivot_cost.empty:
        st.plotly_chart(
            metric_trend(pivot_cost, "Monthly Avg Cost per Hire by Department", "Cost ($)"),
            use_container_width=True,
        )

    col_a, col_b = st.columns(2)
    with col_a:
        st.metric("Avg Cost per Hire", f"${df['Cost per Hire ($)'].mean():,.0f}")
    with col_b:
        most_expensive = df.groupby("Department")["Cost per Hire ($)"].mean().idxmax()
        st.metric("Highest Avg Cost Dept", most_expensive)
