"""Predictive — linear forecast per department."""
from __future__ import annotations

import streamlit as st

st.set_page_config(page_title="Forecast · Talent Pulse", page_icon="🔮", layout="wide")

from src.theme import inject_global_css
inject_global_css()

from dotenv import load_dotenv
load_dotenv()

import pandas as pd

from src.data import load_staffing_data, filter_data
from src.forecast import forecast_metric
from src.charts import forecast_chart
from src.kpis import monthly_metric_by_dept

df_all = load_staffing_data()

all_depts = sorted(df_all["Department"].unique().tolist())
min_month = df_all["Month"].min().date()
max_month = df_all["Month"].max().date()

METRIC_OPTIONS = ["Hires", "Applicants"]

with st.sidebar:
    st.header("Filters")
    selected_depts = st.multiselect("Departments", options=all_depts, default=all_depts)
    metric = st.selectbox("Metric to Forecast", options=METRIC_OPTIONS, index=0)
    horizon = st.slider("Forecast Horizon (months)", min_value=1, max_value=6, value=3)

    if not selected_depts:
        selected_depts = all_depts

    df = filter_data(df_all, departments=selected_depts)
    st.caption(f"{len(df):,} rows in view")

st.markdown('<p class="eyebrow">PREDICTIVE</p>', unsafe_allow_html=True)
st.title("Forecast")
st.markdown(
    f"Projecting **{metric}** for the next **{horizon} months** "
    f"across {len(selected_depts)} department(s)."
)

if df.empty:
    st.info("No data for this filter combination.")
    st.stop()

# ── Aggregated total forecast ──────────────────────────────────────────────────
st.subheader(f"Aggregate — All Selected Departments")
agg_monthly = df.groupby("Month")[metric].sum().sort_index()
agg_result = forecast_metric(agg_monthly, n_months=horizon)

if len(agg_result["forecast_dates"]) > 0:
    total_forecast = int(round(sum(agg_result["forecast_values"])))
    c1, c2, c3 = st.columns(3)
    with c1:
        st.metric(f"Projected {metric} (next {horizon}mo)", f"{total_forecast:,}")
    with c2:
        recent_avg = float(agg_monthly.iloc[-3:].mean()) if len(agg_monthly) >= 3 else float(agg_monthly.mean())
        forecast_avg = float(agg_result["forecast_values"].mean())
        delta_pct = (forecast_avg - recent_avg) / max(abs(recent_avg), 1)
        st.metric("Forecast vs Recent Avg", f"{delta_pct:+.1%}")
    with c3:
        pi_width = float((agg_result["upper"] - agg_result["lower"]).mean())
        st.metric("Avg 95% PI Width", f"±{pi_width / 2:.1f}")

fig_agg = forecast_chart(
    history_dates=agg_monthly.index,
    history_values=agg_monthly.values,
    forecast_dates=agg_result["forecast_dates"],
    forecast_values=agg_result["forecast_values"],
    lower=agg_result["lower"],
    upper=agg_result["upper"],
    title=f"Total {metric} — All Departments",
    y_label=metric,
)
st.plotly_chart(fig_agg, use_container_width=True)

st.divider()

# ── Per-department forecasts ───────────────────────────────────────────────────
st.subheader("Department-Level Forecasts")

pivot = monthly_metric_by_dept(df, metric)

if pivot.empty:
    st.info("Not enough monthly data to generate per-department forecasts.")
else:
    cols = st.columns(2)
    for i, dept in enumerate(pivot.columns):
        series = pivot[dept].dropna()
        result = forecast_metric(series, n_months=horizon)

        with cols[i % 2]:
            if len(result["forecast_dates"]) == 0:
                st.caption(f"{dept}: insufficient data (<4 months)")
                continue

            fig = forecast_chart(
                history_dates=series.index,
                history_values=series.values,
                forecast_dates=result["forecast_dates"],
                forecast_values=result["forecast_values"],
                lower=result["lower"],
                upper=result["upper"],
                title=dept,
                y_label=metric,
            )
            st.plotly_chart(fig, use_container_width=True)

st.divider()
st.caption(
    "Methodology: Linear regression on monthly observations · "
    "95% prediction interval from residual std · "
    "Simple baseline — does not capture seasonality."
)
