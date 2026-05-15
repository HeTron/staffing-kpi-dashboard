"""Plotly figure factories for the Talent Pulse dashboard."""
from __future__ import annotations

import numpy as np
import pandas as pd
import plotly.graph_objects as go

from src.theme import (
    ACCENT_AMBER,
    BACKGROUND,
    BORDER,
    DEPT_PALETTE,
    MUTED_SLATE,
    PRIMARY_NAVY,
    SURFACE,
)


def funnel_chart(stages: dict[str, int]) -> go.Figure:
    labels = list(stages.keys())
    values = list(stages.values())
    colors = [ACCENT_AMBER] * len(labels)
    # Apply opacity gradient: brightest at top, dimmer at bottom
    opacities = [1.0, 0.78, 0.58, 0.42][:len(labels)]
    marker_colors = [
        f"rgba(199,123,58,{o})" for o in opacities
    ]
    fig = go.Figure(
        go.Funnel(
            y=labels,
            x=values,
            textinfo="value+percent initial",
            marker=dict(color=marker_colors, line=dict(color=SURFACE, width=1)),
            connector=dict(line=dict(color=BORDER, width=1)),
        )
    )
    fig.update_layout(height=380, margin=dict(t=20))
    return fig


def sankey_funnel(df: pd.DataFrame) -> go.Figure:
    applicants = int(df["Applicants"].sum())
    interviews = int(df["Interviews"].sum())
    offers = int(df["Offers"].sum())
    hires = int(df["Hires"].sum())
    dropped_app = applicants - interviews
    dropped_int = interviews - offers
    dropped_off = offers - hires

    node_labels = [
        "Applicants", "Interviews", "Offers", "Hires",
        "Screened Out", "No Offer", "Declined / Unfilled",
    ]
    node_colors = [
        PRIMARY_NAVY, "#5B6FA8", "#9E7B47", ACCENT_AMBER,
        MUTED_SLATE, MUTED_SLATE, MUTED_SLATE,
    ]

    fig = go.Figure(
        go.Sankey(
            node=dict(
                pad=15,
                thickness=20,
                line=dict(color=BORDER, width=0.5),
                label=node_labels,
                color=node_colors,
            ),
            link=dict(
                source=[0, 0, 1, 1, 2, 2],
                target=[1, 4, 2, 5, 3, 6],
                value=[interviews, dropped_app, offers, dropped_int, hires, dropped_off],
                color=[
                    "rgba(91,111,168,0.3)",
                    "rgba(107,117,137,0.15)",
                    "rgba(158,123,71,0.3)",
                    "rgba(107,117,137,0.15)",
                    "rgba(199,123,58,0.4)",
                    "rgba(107,117,137,0.15)",
                ],
            ),
        )
    )
    fig.update_layout(height=400, margin=dict(t=20))
    return fig


def dept_comparison_bar(df: pd.DataFrame, metric: str, title: str) -> go.Figure:
    grouped = (
        df.groupby("Department")[metric]
        .sum()
        .sort_values()
        .reset_index()
    )
    fig = go.Figure(
        go.Bar(
            x=grouped[metric],
            y=grouped["Department"],
            orientation="h",
            marker_color=PRIMARY_NAVY,
            text=grouped[metric],
            textposition="outside",
        )
    )
    fig.update_layout(height=380, xaxis_title=metric, margin=dict(t=20))
    return fig


def metric_trend(df_pivot: pd.DataFrame, title: str, y_label: str) -> go.Figure:
    fig = go.Figure()
    for i, col in enumerate(df_pivot.columns):
        fig.add_trace(
            go.Scatter(
                x=df_pivot.index,
                y=df_pivot[col],
                mode="lines+markers",
                name=col,
                line=dict(color=DEPT_PALETTE[i % len(DEPT_PALETTE)], width=2),
                marker=dict(size=5),
            )
        )
    fig.update_layout(
        yaxis_title=y_label,
        height=440,
        legend=dict(orientation="h", yanchor="bottom", y=1.02, x=0, xanchor="left"),
        margin=dict(t=80),
    )
    return fig


def heatmap_dept_role(df: pd.DataFrame, metric: str) -> go.Figure:
    rate_cols = {"Avg Time to Fill (days)", "Offer Acceptance Rate", "Cost per Hire ($)"}
    agg = "mean" if metric in rate_cols else "sum"
    pivot = (
        df.groupby(["Role", "Month"])[metric]
        .agg(agg)
        .unstack("Month")
    )
    pivot.columns = [str(c)[:7] for c in pivot.columns]

    colorscale = [
        [0.0, BACKGROUND],
        [1.0, ACCENT_AMBER],
    ]

    fig = go.Figure(
        go.Heatmap(
            z=pivot.values,
            x=pivot.columns.tolist(),
            y=pivot.index.tolist(),
            colorscale=colorscale,
            colorbar=dict(title=metric),
            hovertemplate="Role: %{y}<br>Month: %{x}<br>" + metric + ": %{z:.1f}<extra></extra>",
        )
    )
    fig.update_layout(
        height=max(300, len(pivot) * 40 + 100),
        xaxis_title="Month",
        yaxis_title="Role",
        margin=dict(l=200, t=20),
    )
    return fig


def forecast_chart(
    history_dates: pd.DatetimeIndex,
    history_values: np.ndarray,
    forecast_dates: pd.DatetimeIndex,
    forecast_values: np.ndarray,
    lower: np.ndarray,
    upper: np.ndarray,
    title: str,
    y_label: str,
) -> go.Figure:
    fig = go.Figure()

    fig.add_trace(
        go.Scatter(
            x=history_dates,
            y=history_values,
            mode="lines",
            name="Historical",
            line=dict(color=PRIMARY_NAVY, width=2),
        )
    )

    if len(forecast_dates) > 0:
        # Confidence band
        fig.add_trace(
            go.Scatter(
                x=list(forecast_dates) + list(forecast_dates[::-1]),
                y=list(upper) + list(lower[::-1]),
                fill="toself",
                fillcolor=f"rgba(199,123,58,0.15)",
                line=dict(color="rgba(0,0,0,0)"),
                name="95% PI",
                hoverinfo="skip",
            )
        )
        # Forecast line
        fig.add_trace(
            go.Scatter(
                x=forecast_dates,
                y=forecast_values,
                mode="lines+markers",
                name="Forecast",
                line=dict(color=ACCENT_AMBER, width=2, dash="dash"),
                marker=dict(size=6),
            )
        )

    fig.update_layout(
        yaxis_title=y_label,
        height=420,
        legend=dict(orientation="h", yanchor="bottom", y=1.02, x=0, xanchor="left"),
        margin=dict(t=80),
    )
    return fig


def source_breakdown_bar(source_df: pd.DataFrame) -> go.Figure:
    sources = source_df["Source"].unique().tolist()
    depts = source_df["Department"].unique().tolist()

    source_colors = {
        "LinkedIn": "#1B2A4E",
        "Referral": "#C77B3A",
        "Career Site": "#3D7A5F",
        "Indeed": "#5B6FA8",
        "Recruiter Outreach": "#9E7B47",
        "Glassdoor": "#6B7589",
    }

    fig = go.Figure()
    totals = source_df.groupby("Department")["Applicants"].sum()

    for source in sources:
        subset = source_df[source_df["Source"] == source].set_index("Department")
        values = [subset.loc[d, "Applicants"] if d in subset.index else 0 for d in depts]
        fig.add_trace(
            go.Bar(
                x=values,
                y=depts,
                name=source,
                orientation="h",
                marker_color=source_colors.get(source, MUTED_SLATE),
            )
        )

    fig.update_layout(
        barmode="stack",
        xaxis_title="Applicants",
        height=420,
        legend=dict(orientation="h", yanchor="bottom", y=1.02, x=0, xanchor="left"),
        margin=dict(t=80),
    )
    return fig
