"""KPI computation functions for the Talent Pulse dashboard."""
from __future__ import annotations

import pandas as pd


def compute_period_kpis(df: pd.DataFrame) -> dict:
    return {
        "applicants": int(df["Applicants"].sum()),
        "interviews": int(df["Interviews"].sum()),
        "offers": int(df["Offers"].sum()),
        "hires": int(df["Hires"].sum()),
        "avg_ttf": round(float(df["Avg Time to Fill (days)"].mean()), 1),
        "avg_cost_per_hire": round(float(df["Cost per Hire ($)"].mean()), 0),
        "offer_accept_rate": round(float(df["Offer Acceptance Rate"].mean()), 3),
        "openings": int(df["Openings"].sum()),
    }


def compute_deltas(curr_kpis: dict, prev_kpis: dict) -> dict:
    deltas = {}
    for key in curr_kpis:
        curr = curr_kpis[key]
        prev = prev_kpis.get(key, 0)
        if prev == 0:
            deltas[key] = None
        else:
            deltas[key] = round((curr - prev) / abs(prev), 4)
    return deltas


def funnel_conversion_rates(df: pd.DataFrame) -> dict:
    applicants = df["Applicants"].sum()
    interviews = df["Interviews"].sum()
    offers = df["Offers"].sum()
    hires = df["Hires"].sum()
    return {
        "app_to_int": round(interviews / max(applicants, 1), 4),
        "int_to_off": round(offers / max(interviews, 1), 4),
        "off_to_hire": round(hires / max(offers, 1), 4),
        "overall": round(hires / max(applicants, 1), 4),
    }


def funnel_by_department(df: pd.DataFrame) -> pd.DataFrame:
    return (
        df.groupby("Department")[["Applicants", "Interviews", "Offers", "Hires"]]
        .sum()
        .reset_index()
        .sort_values("Hires", ascending=False)
    )


def monthly_metric_by_dept(df: pd.DataFrame, metric: str) -> pd.DataFrame:
    rate_cols = {"Avg Time to Fill (days)", "Offer Acceptance Rate", "Cost per Hire ($)"}
    agg = "mean" if metric in rate_cols else "sum"
    pivot = (
        df.groupby(["Month", "Department"])[metric]
        .agg(agg)
        .unstack("Department")
        .sort_index()
    )
    return pivot


def top_recruiters(df: pd.DataFrame, n: int = 5) -> pd.DataFrame:
    return (
        df.groupby("Recruiter")
        .agg(Hires=("Hires", "sum"), Avg_TTF=("Avg Time to Fill (days)", "mean"))
        .rename(columns={"Avg_TTF": "Avg TTF"})
        .sort_values("Hires", ascending=False)
        .head(n)
        .reset_index()
    )


def split_period(df: pd.DataFrame, lookback_months: int = 3) -> tuple[pd.DataFrame, pd.DataFrame]:
    sorted_months = sorted(df["Month"].unique())
    if len(sorted_months) < lookback_months * 2:
        # Not enough history — return all as current, empty as prior
        return df, df.iloc[0:0]
    recent_cutoff = sorted_months[-lookback_months]
    prior_cutoff = sorted_months[-(lookback_months * 2)]
    current = df[df["Month"] >= recent_cutoff]
    prior = df[(df["Month"] >= prior_cutoff) & (df["Month"] < recent_cutoff)]
    return current, prior
