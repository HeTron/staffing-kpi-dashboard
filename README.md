# Talent Pulse

**AI-powered recruiting operations intelligence dashboard**

![Python 3.11+](https://img.shields.io/badge/Python-3.11%2B-blue)
![License: MIT](https://img.shields.io/badge/License-MIT-yellow)

---

## Demo

_Live demo: TBD (Streamlit Cloud deployment pending)_

---

## Features

- **Multi-page dashboard** — Overview, Funnel, Trends, Department Deep Dive, Forecast, AI Insights
- **KPI strip with period deltas** — Applicants, Interviews, Offers, Hires, Avg Time to Fill vs prior period
- **Hiring funnel** — Plotly funnel chart + Sankey diagram showing stage drop-off
- **Time-series trends** — Volume, quality (OAR, TTF), and cost per hire by department
- **Department Deep Dive** — Role × Month heatmaps, top recruiter table, source-of-hire breakdown
- **Forecast** — Linear trend projection with 95% prediction interval, per department
- **AI Insights** — Claude (Sonnet) reads filtered data and writes an executive briefing in seconds
- **Light Executive theme** — Editorial typography, warm cream palette, print-quality Plotly charts

---

## How It Works

```
generate_data.py
  └─► data/staffing_data.csv        (dept × role × month recruiting metrics)
  └─► data/source_breakdown.csv     (applicant source splits with conversion signal)
        │
        ▼
src/data.py          — cached CSV loading + filter helpers
src/kpis.py          — KPI aggregation, delta computation, funnel math
src/charts.py        — Plotly figure factories (funnel, sankey, heatmap, trend, forecast)
src/forecast.py      — Linear regression + 95% PI for n-month projections
src/insights.py      — Claude API integration → executive markdown briefing
        │
        ▼
streamlit_app.py     — Overview page (entry point)
pages/
  1_📈_Funnel.py         — Pipeline analysis
  2_📊_Trends.py         — Time-series trends
  3_🏢_Department_Deep_Dive.py
  4_🔮_Forecast.py       — Predictive projections
  5_🤖_AI_Insights.py    — Claude briefing
```

---

## Tech Stack

| Layer | Tool |
|---|---|
| UI framework | Streamlit |
| Charts | Plotly |
| Data | pandas + numpy |
| Forecasting | scikit-learn (LinearRegression) |
| AI | Anthropic Claude API (claude-sonnet-4-6) |
| Data generation | numpy RNG (seed=42, reproducible) |

---

## Local Setup

```bash
git clone https://github.com/HeTron/staffing-kpi-dashboard.git
cd staffing-kpi-dashboard

python -m venv .venv
source .venv/bin/activate          # Windows: .venv\Scripts\activate

pip install -r requirements.txt

cp .env.example .env
# Optionally add ANTHROPIC_API_KEY to .env for the AI Insights page

python generate_data.py            # Creates data/ CSVs

streamlit run streamlit_app.py
```

---

## Tests

```bash
pytest tests/ -v
```

Tests cover: data loading column contracts, filter correctness, KPI math, delta zero-division handling, and split-period disjointness.

---

## Project Structure

```
staffing-kpi-dashboard/
├── .streamlit/config.toml
├── src/
│   ├── theme.py          # Design tokens + Plotly template + CSS injection
│   ├── data.py           # Cached CSV loading + filter helpers
│   ├── kpis.py           # KPI computation functions
│   ├── charts.py         # Plotly figure factories
│   ├── forecast.py       # Linear trend forecast with 95% PI
│   └── insights.py       # Claude API integration
├── pages/
│   ├── 1_📈_Funnel.py
│   ├── 2_📊_Trends.py
│   ├── 3_🏢_Department_Deep_Dive.py
│   ├── 4_🔮_Forecast.py
│   └── 5_🤖_AI_Insights.py
├── tests/
│   ├── test_data.py
│   └── test_kpis.py
├── data/
│   ├── staffing_data.csv
│   └── source_breakdown.csv
├── streamlit_app.py      # Overview — entry point
├── generate_data.py      # Synthetic data generator
├── requirements.txt
├── .env.example
└── LICENSE
```

---

## License

MIT © 2026 Jason Eid
