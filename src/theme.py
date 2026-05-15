"""Design system: color constants, Plotly template, and global CSS injection."""
from __future__ import annotations

import plotly.graph_objects as go
import plotly.io as pio

BACKGROUND = "#FAF7F2"
SURFACE = "#FFFFFF"
PRIMARY_NAVY = "#1B2A4E"
ACCENT_AMBER = "#C77B3A"
MUTED_SLATE = "#6B7589"
SUCCESS_GREEN = "#3D7A5F"
WARNING_RED = "#A8423B"
BORDER = "#E8E2D8"

DEPT_PALETTE = [
    "#1B2A4E",
    "#C77B3A",
    "#3D7A5F",
    "#7A4E3D",
    "#5B6FA8",
    "#9E7B47",
    "#6B7589",
    "#8C5A8A",
]

FONT_HEAD = '"Source Serif 4", "Source Serif Pro", Georgia, serif'
FONT_BODY = '"Inter", "Helvetica Neue", system-ui, sans-serif'

TALENT_PULSE_TEMPLATE = go.layout.Template(
    layout=dict(
        paper_bgcolor=SURFACE,
        plot_bgcolor=SURFACE,
        font=dict(family=FONT_BODY, color=PRIMARY_NAVY, size=13),
        title=dict(font=dict(family=FONT_HEAD, size=18, color=PRIMARY_NAVY)),
        colorway=DEPT_PALETTE,
        xaxis=dict(
            gridcolor=BORDER,
            linecolor=BORDER,
            zerolinecolor=BORDER,
            tickfont=dict(color=MUTED_SLATE),
        ),
        yaxis=dict(
            gridcolor=BORDER,
            linecolor=BORDER,
            zerolinecolor=BORDER,
            tickfont=dict(color=MUTED_SLATE),
        ),
        legend=dict(font=dict(color=PRIMARY_NAVY), bgcolor="rgba(0,0,0,0)"),
        margin=dict(l=60, r=30, t=60, b=50),
    )
)
pio.templates["talent_pulse"] = TALENT_PULSE_TEMPLATE
pio.templates.default = "talent_pulse"


def inject_global_css() -> None:
    """Call once per page (after st.set_page_config) to apply editorial typography."""
    import streamlit as st

    st.markdown(
        """
<style>
@import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600&family=Source+Serif+4:wght@400;600;700&display=swap');

html, body, [class*="css"] { font-family: 'Inter', system-ui, sans-serif; color: #1B2A4E; }
h1, h2, h3, h4 { font-family: 'Source Serif 4', Georgia, serif !important; color: #1B2A4E !important; letter-spacing: -0.01em; }
h1 { font-weight: 700; font-size: 2.4rem !important; }
h2 { font-weight: 600; font-size: 1.6rem !important; border-bottom: 1px solid #E8E2D8; padding-bottom: 0.4rem; }
h3 { font-weight: 600; font-size: 1.2rem !important; }

[data-testid="stMetric"] {
    background: #FFFFFF;
    border: 1px solid #E8E2D8;
    padding: 1rem 1.2rem;
    border-radius: 4px;
}
[data-testid="stMetricLabel"] {
    font-family: 'Inter', sans-serif !important;
    text-transform: uppercase;
    letter-spacing: 0.08em;
    font-size: 0.7rem !important;
    color: #6B7589 !important;
}
[data-testid="stMetricValue"] {
    font-family: 'Source Serif 4', Georgia, serif !important;
    font-weight: 600;
    color: #1B2A4E !important;
}
[data-testid="stMetricDelta"] svg { display: none; }

div.stButton > button[kind="primary"] {
    background: #C77B3A; color: #FFFFFF; border: none;
    font-family: 'Inter', sans-serif; font-weight: 500; letter-spacing: 0.02em;
}
div.stButton > button[kind="primary"]:hover { background: #B56A2D; }

[data-testid="stSidebar"] { background: #F5F1E8; border-right: 1px solid #E8E2D8; }

.insight-card {
    background: #FFFFFF;
    border-left: 4px solid #C77B3A;
    padding: 1.2rem 1.4rem;
    border-radius: 2px;
    margin: 0.5rem 0;
    font-family: 'Source Serif 4', Georgia, serif;
    font-size: 1.02rem;
    line-height: 1.6;
    color: #1B2A4E;
    box-shadow: 0 1px 3px rgba(27, 42, 78, 0.04);
}
.eyebrow {
    font-family: 'Inter', sans-serif;
    text-transform: uppercase;
    letter-spacing: 0.12em;
    font-size: 0.72rem;
    color: #C77B3A;
    font-weight: 600;
    margin-bottom: 0.3rem;
}
hr { border-color: #E8E2D8 !important; }
</style>
        """,
        unsafe_allow_html=True,
    )
