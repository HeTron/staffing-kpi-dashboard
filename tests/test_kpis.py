"""Tests for src/kpis.py."""
from __future__ import annotations

import pandas as pd
import pytest

from src.kpis import (
    compute_deltas,
    compute_period_kpis,
    funnel_conversion_rates,
    split_period,
)


def _make_df(n_months: int = 6, hires_per_row: int = 5) -> pd.DataFrame:
    months = pd.date_range("2024-07", periods=n_months, freq="MS")
    rows = []
    for m in months:
        rows.append({
            "Department": "Engineering",
            "Role": "Engineering Senior Backend",
            "Month": m,
            "Recruiter": "Maya Chen",
            "Openings": 3,
            "Applicants": 100,
            "Interviews": 30,
            "Offers": 10,
            "Hires": hires_per_row,
            "Avg Time to Fill (days)": 40.0,
            "Cost per Hire ($)": 10000,
            "Offer Acceptance Rate": 0.5,
        })
    return pd.DataFrame(rows)


def test_compute_period_kpis_basic() -> None:
    df = _make_df(n_months=3, hires_per_row=5)
    kpis = compute_period_kpis(df)
    assert kpis["hires"] == 15
    assert kpis["applicants"] == 300
    assert kpis["avg_ttf"] == pytest.approx(40.0)
    assert set(kpis.keys()) == {
        "applicants", "interviews", "offers", "hires",
        "avg_ttf", "avg_cost_per_hire", "offer_accept_rate", "openings",
    }


def test_compute_deltas_handles_zero_division() -> None:
    curr = {"hires": 10, "applicants": 200}
    prev = {"hires": 0, "applicants": 100}
    deltas = compute_deltas(curr, prev)
    # Zero prior value → None (no divide-by-zero)
    assert deltas["hires"] is None
    assert deltas["applicants"] == pytest.approx(1.0)


def test_funnel_conversion_rates_sum_to_total_path() -> None:
    df = _make_df(n_months=1)
    rates = funnel_conversion_rates(df)
    assert set(rates.keys()) == {"app_to_int", "int_to_off", "off_to_hire", "overall"}
    # overall should equal product of the three stage rates (approximately)
    product = rates["app_to_int"] * rates["int_to_off"] * rates["off_to_hire"]
    assert rates["overall"] == pytest.approx(product, rel=0.01)


def test_split_period_returns_disjoint_frames() -> None:
    df = _make_df(n_months=8)
    current, prior = split_period(df, lookback_months=3)
    if not prior.empty:
        assert current["Month"].min() > prior["Month"].max()
    assert len(current) > 0
