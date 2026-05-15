"""Claude-powered insight generation for filtered staffing data."""
from __future__ import annotations

import os
from typing import Any

import pandas as pd

try:
    from anthropic import Anthropic
    _ANTHROPIC_AVAILABLE = True
except ImportError:
    _ANTHROPIC_AVAILABLE = False

MODEL = "claude-sonnet-4-6"


def _build_summary(df: pd.DataFrame, source_df: pd.DataFrame) -> dict[str, Any]:
    """Pack filtered data into a compact JSON-serializable summary for Claude."""
    from src.kpis import (
        compute_period_kpis,
        funnel_conversion_rates,
        funnel_by_department,
        top_recruiters,
    )

    totals = compute_period_kpis(df)
    rates = funnel_conversion_rates(df)
    dept_funnel = funnel_by_department(df)

    top3_hires = dept_funnel.head(3)[["Department", "Hires"]].to_dict("records")
    bottom3_oar = (
        df.groupby("Department")["Offer Acceptance Rate"]
        .mean()
        .sort_values()
        .head(3)
        .reset_index()
        .rename(columns={"Offer Acceptance Rate": "Avg Offer Acceptance Rate"})
        .to_dict("records")
    )

    avg_ttf_by_dept = (
        df.groupby("Department")["Avg Time to Fill (days)"]
        .mean()
        .round(1)
        .reset_index()
        .to_dict("records")
    )

    recruiters = top_recruiters(df, n=1)
    top_recruiter = recruiters.to_dict("records")[0] if not recruiters.empty else {}

    # MoM trend: last 3 vs prior 3 months on total hires
    monthly_hires = (
        df.groupby("Month")["Hires"].sum().sort_index()
    )
    if len(monthly_hires) >= 6:
        recent_3 = int(monthly_hires.iloc[-3:].sum())
        prior_3 = int(monthly_hires.iloc[-6:-3].sum())
    elif len(monthly_hires) >= 3:
        recent_3 = int(monthly_hires.iloc[-3:].sum())
        prior_3 = None
    else:
        recent_3 = int(monthly_hires.sum())
        prior_3 = None

    # Source conversion rates
    source_rates: list[dict] = []
    if not source_df.empty:
        src_agg = (
            source_df.groupby("Source")[["Applicants", "Hires"]].sum().reset_index()
        )
        src_agg["Conversion Rate"] = (
            src_agg["Hires"] / src_agg["Applicants"].replace(0, 1)
        ).round(4)
        source_rates = src_agg.sort_values("Conversion Rate", ascending=False).to_dict("records")

    months_in_view = df["Month"].nunique() if "Month" in df.columns else "?"
    depts_in_view = df["Department"].nunique() if "Department" in df.columns else "?"

    return {
        "period": {
            "months": months_in_view,
            "departments": depts_in_view,
        },
        "totals": totals,
        "funnel_rates": {k: f"{v:.1%}" for k, v in rates.items()},
        "top3_departments_by_hires": top3_hires,
        "bottom3_departments_by_offer_acceptance": bottom3_oar,
        "avg_ttf_by_department": avg_ttf_by_dept,
        "top_recruiter": top_recruiter,
        "source_conversion_rates": source_rates,
        "mom_hires": {
            "recent_3_months": recent_3,
            "prior_3_months": prior_3,
        },
    }


def generate_insights(df: pd.DataFrame, source_df: pd.DataFrame) -> str:
    """Return markdown briefing. Falls back to a friendly stub if no API key."""
    if not _ANTHROPIC_AVAILABLE:
        return (
            "_Anthropic SDK not installed. Run `pip install anthropic` "
            "and set `ANTHROPIC_API_KEY` in `.env` to enable AI insights._"
        )

    api_key = os.getenv("ANTHROPIC_API_KEY")
    if not api_key:
        return (
            "_Set `ANTHROPIC_API_KEY` in `.env` to enable Claude-generated insights._\n\n"
            "_(The dashboard works fully without it — only this page is gated.)_"
        )

    summary = _build_summary(df, source_df)
    client = Anthropic(api_key=api_key)

    prompt = f"""You are an executive recruiting analyst writing for a CHRO. Below is a JSON snapshot of recruiting performance for a filtered period.

DATA:
{summary}

Write a brief, professional briefing in this exact markdown structure:

### TL;DR
2-3 sentences summarizing the headline story.

### What Stands Out
- 3-5 bullet observations grounded in the numbers (cite specific values).

### Recommended Actions
- 2-3 concrete actions a hiring leader should take this quarter.

Tone: editorial, decisive, executive-ready. No hedging, no preamble. Use the bullets exactly as specified."""

    msg = client.messages.create(
        model=MODEL,
        max_tokens=1200,
        messages=[{"role": "user", "content": prompt}],
    )
    return msg.content[0].text
