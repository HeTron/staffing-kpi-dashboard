"""Data loading utilities with Streamlit caching."""
from __future__ import annotations

from pathlib import Path

import pandas as pd
import streamlit as st

DATA_DIR = Path(__file__).resolve().parent.parent / "data"


def _load_staffing_raw() -> pd.DataFrame:
    df = pd.read_csv(DATA_DIR / "staffing_data.csv")
    df["Month"] = pd.to_datetime(df["Month"])
    return df


def _load_source_breakdown_raw() -> pd.DataFrame:
    df = pd.read_csv(DATA_DIR / "source_breakdown.csv")
    df["Month"] = pd.to_datetime(df["Month"])
    return df


@st.cache_data
def load_staffing_data() -> pd.DataFrame:
    return _load_staffing_raw()


@st.cache_data
def load_source_breakdown() -> pd.DataFrame:
    return _load_source_breakdown_raw()


def filter_data(
    df: pd.DataFrame,
    departments: list[str] | None = None,
    date_range: tuple | None = None,
) -> pd.DataFrame:
    out = df.copy()
    if departments:
        out = out[out["Department"].isin(departments)]
    if date_range and len(date_range) == 2:
        start = pd.to_datetime(date_range[0])
        end = pd.to_datetime(date_range[1])
        out = out[(out["Month"] >= start) & (out["Month"] <= end)]
    return out
