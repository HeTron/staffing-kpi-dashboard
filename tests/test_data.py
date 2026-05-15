"""Tests for src/data.py."""
from __future__ import annotations

import pandas as pd
import pytest

from src.data import _load_staffing_raw, _load_source_breakdown_raw, filter_data

REQUIRED_STAFFING_COLS = {
    "Department",
    "Role",
    "Month",
    "Recruiter",
    "Openings",
    "Applicants",
    "Interviews",
    "Offers",
    "Hires",
    "Avg Time to Fill (days)",
    "Cost per Hire ($)",
    "Offer Acceptance Rate",
}

REQUIRED_SOURCE_COLS = {"Department", "Month", "Source", "Applicants", "Hires"}


def test_load_staffing_data_columns() -> None:
    df = _load_staffing_raw()
    assert REQUIRED_STAFFING_COLS.issubset(set(df.columns))
    assert len(df) > 0


def test_load_source_breakdown_columns() -> None:
    df = _load_source_breakdown_raw()
    assert REQUIRED_SOURCE_COLS.issubset(set(df.columns))
    assert len(df) > 0


def test_filter_by_departments() -> None:
    df = _load_staffing_raw()
    filtered = filter_data(df, departments=["Engineering", "Sales"])
    assert set(filtered["Department"].unique()) == {"Engineering", "Sales"}


def test_filter_by_date_range() -> None:
    df = _load_staffing_raw()
    start = pd.Timestamp("2024-10-01")
    end = pd.Timestamp("2025-03-01")
    filtered = filter_data(df, date_range=(start, end))
    assert (filtered["Month"] >= start).all()
    assert (filtered["Month"] <= end).all()
