"""Simple linear forecast with prediction interval."""
from __future__ import annotations

import numpy as np
import pandas as pd
from sklearn.linear_model import LinearRegression


def forecast_metric(monthly_series: pd.Series, n_months: int = 3) -> dict:
    """Fit a linear trend on the series and project n_months forward.

    Returns forecast_dates, forecast_values, lower, upper (95% PI based on residual std).
    """
    s = monthly_series.dropna().sort_index()
    if len(s) < 4:
        return {
            "forecast_dates": pd.DatetimeIndex([]),
            "forecast_values": np.array([]),
            "lower": np.array([]),
            "upper": np.array([]),
        }

    X = np.arange(len(s)).reshape(-1, 1)
    y = s.values.astype(float)
    model = LinearRegression().fit(X, y)
    residuals = y - model.predict(X)
    sigma = float(np.std(residuals, ddof=1)) if len(residuals) > 1 else 0.0

    future_X = np.arange(len(s), len(s) + n_months).reshape(-1, 1)
    yhat = model.predict(future_X)

    last_month = s.index[-1]
    future_dates = pd.date_range(
        start=last_month + pd.offsets.MonthBegin(1), periods=n_months, freq="MS"
    )

    z = 1.96
    lower = np.maximum(yhat - z * sigma, 0)
    upper = yhat + z * sigma

    return {
        "forecast_dates": future_dates,
        "forecast_values": yhat,
        "lower": lower,
        "upper": upper,
    }
