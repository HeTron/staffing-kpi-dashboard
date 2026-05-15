# CLAUDE.md — Talent Pulse

Project-specific context for Claude working in this repo. Global preferences live in `~/.claude/CLAUDE.md`; AIBC workspace conventions in `~/Projects/aibc/CLAUDE.md`. This file covers only what's specific to **Talent Pulse**.

---

## What this is

**Talent Pulse** — AI-powered recruiting operations intelligence dashboard. Multi-page Streamlit app over a simulated 18-month recruiting dataset, with Plotly charts in a custom "Light Executive" theme and Claude-generated executive briefings.

Portfolio piece — sister project to **Market Edge** (which it deliberately mirrors architecturally but differentiates visually).

Sits in the AIBC workspace at `~/Projects/aibc/staffing-kpi-dashboard/`.

---

## Stack

| Layer | Tool |
|---|---|
| UI | Streamlit (multi-page) |
| Charts | Plotly (custom `talent_pulse` template) |
| Data | pandas + numpy |
| Forecasting | scikit-learn (`LinearRegression` + residual-std PI) |
| AI | Anthropic Claude Sonnet (`claude-sonnet-4-6`) |
| Data gen | numpy default_rng(seed=42) — fully reproducible |
| Tests | pytest |

---

## Layout

```
staffing-kpi-dashboard/
├── .streamlit/config.toml      # Light theme config
├── src/
│   ├── theme.py                # Design tokens, Plotly template, CSS injection
│   ├── data.py                 # Cached CSV loaders + filter helpers
│   ├── kpis.py                 # KPI math, deltas, funnel, period split
│   ├── charts.py               # Plotly figure factories
│   ├── forecast.py             # LinearRegression + 95% prediction interval
│   └── insights.py             # Claude API briefing generator
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
│   ├── staffing_data.csv       # 432 rows — (Dept × Role × Month)
│   └── source_breakdown.csv    # 864 rows — (Dept × Month × Source)
├── streamlit_app.py            # Overview — Streamlit entry point
├── generate_data.py            # Regenerates both CSVs deterministically
├── requirements.txt
├── .env.example
├── LICENSE                     # MIT, 2026 Jason Eid
└── README.md
```

---

## Run

```bash
source .venv/bin/activate
streamlit run streamlit_app.py
```

Opens at `http://localhost:8501`.

To regenerate the dataset (deterministic — same output every time):
```bash
python generate_data.py
```

To run tests:
```bash
pytest tests/ -v
```

---

## Environment

`.env` (optional — only needed for the AI Insights page):

| Var | Required | Purpose |
|---|---|---|
| `ANTHROPIC_API_KEY` | No | Enables Claude briefings on page 5. App degrades gracefully without it (shows a friendly fallback). |

`.env.example` is committed; `.env` is git-ignored.

---

## Design system (load-bearing — don't drift)

Defined in `src/theme.py`. Light Executive palette, editorial typography, print-quality.

| Token | Hex | Use |
|---|---|---|
| `BACKGROUND` | `#FAF7F2` | Page bg (warm cream) |
| `SURFACE` | `#FFFFFF` | Cards |
| `PRIMARY_NAVY` | `#1B2A4E` | Body text, headcount/applicant lines |
| `ACCENT_AMBER` | `#C77B3A` | CTAs, hire metrics, eyebrows, highlights |
| `MUTED_SLATE` | `#6B7589` | Secondary text, axis ticks |
| `SUCCESS_GREEN` | `#3D7A5F` | Positive deltas |
| `WARNING_RED` | `#A8423B` | Negative deltas |
| `BORDER` | `#E8E2D8` | Card borders, gridlines |

Fonts: **Source Serif 4** (headings) + **Inter** (body), both loaded from Google Fonts via injected `<style>` in `theme.inject_global_css()`.

Plotly template `talent_pulse` is registered as the default at module import — every chart should already use it without per-figure overrides.

**Every page must call `inject_global_css()` AFTER `st.set_page_config()`** — otherwise typography won't apply.

---

## Data schema

### `data/staffing_data.csv` (432 rows, one per Dept × Role × Month)

`Department, Role, Month, Recruiter, Openings, Applicants, Interviews, Offers, Hires, Avg Time to Fill (days), Cost per Hire ($), Offer Acceptance Rate`

- 8 departments, 2-3 named roles each (e.g. "Engineering Senior Backend", "Sales AE")
- 18 months: `2024-07` → `2025-12`
- Funnel math is realistic (Interviews = Applicants × 0.25-0.55, etc.)
- Hires capped near openings — TTF and Cost per Hire are dept-dependent
- 5 named recruiters in the pool

### `data/source_breakdown.csv` (864 rows, one per Dept × Month × Source)

`Department, Month, Source, Applicants, Hires`

- 6 sources: LinkedIn, Referral, Career Site, Indeed, Recruiter Outreach, Glassdoor
- **Referrals have intentionally higher conversion** — a hidden signal Claude is supposed to surface in AI Insights

---

## Architectural conventions

- **Module split mirrors Market Edge** — `src/` for logic, `pages/` for views, `tests/` for unit tests.
- **All data loaders are `@st.cache_data` decorated** in `src/data.py`. Tests bypass caching by calling raw helpers (or by using fresh DataFrames).
- **All chart functions return `go.Figure`** — never call `st.plotly_chart` inside `src/charts.py`.
- **All KPI math lives in `src/kpis.py`** — pages should not do aggregations inline.
- **Forecast is intentionally simple** — linear trend + 95% PI from residual std. Documented in the page footnote so reviewers know it's a baseline, not Prophet/Holt-Winters.
- **Claude integration in `src/insights.py`** patterned after Market Edge's `src/explain.py`. Model: `claude-sonnet-4-6`. Falls back gracefully if SDK missing or no API key.

---

## Things to never break

- **Don't change the color palette** without updating both `.streamlit/config.toml` and `src/theme.py` together — they must agree.
- **Don't reorder funnel stages** — Applicants → Interviews → Offers → Hires is assumed everywhere (charts, KPI math, Claude prompt).
- **Don't break the data generator's seed** (`np.random.default_rng(42)`) — tests and the AI Insights "interesting signal" (referral conversion lift) depend on the deterministic output.
- **Don't rename CSV columns** without updating `src/data.py`, `src/kpis.py`, every page, and `tests/`. Column names are load-bearing.
- **Don't move CSVs out of `data/`** — `src/data.DATA_DIR` resolves relative to `src/`.

---

## Testing

8 tests covering data loading, filtering, KPI math, delta zero-division, funnel conversion, and period split. Fast (<1s).

```bash
pytest tests/ -v
```

If you add a new metric or chart, add tests for the math, not the rendering.

---

## Known issues / pending

- **Live demo deployed**: https://talent-pulse.streamlit.app — `ANTHROPIC_API_KEY` set as Streamlit Cloud secret. Auto-deploys from `main` on push.
- **Screenshots** — README has no images yet. Capture Overview + AI Insights pages and add to a `docs/screenshots/` folder.
- **`.venv` shebang stale** — venv was created when project lived under `~/PycharmProjects/`. `python -m pip` works fine; rebuilding the venv (`rm -rf .venv && python3.11 -m venv .venv && pip install -r requirements.txt`) cleans this permanently. Low priority — only matters if someone calls `pip` directly.

---

## Reference

- Sister project (architectural template): `~/Projects/aibc/market-edge/`
- Live Market Edge demo: https://market-edge.streamlit.app
- Anthropic SDK pattern: `~/Projects/aibc/market-edge/src/explain.py`

---

*Last updated: 2026-05-14 — initial CLAUDE.md after full rewrite from the original 50-line single-page seaborn dashboard.*
