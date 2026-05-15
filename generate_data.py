"""Generate synthetic staffing KPI data for the Talent Pulse dashboard."""
from __future__ import annotations

from pathlib import Path

import numpy as np
import pandas as pd

RNG = np.random.default_rng(seed=42)

DATA_DIR = Path(__file__).resolve().parent / "data"
DATA_DIR.mkdir(exist_ok=True)

MONTHS = pd.date_range("2024-07", "2025-12", freq="MS")

DEPARTMENTS = [
    "Engineering",
    "Product",
    "Design",
    "Marketing",
    "Sales",
    "Customer Success",
    "Finance",
    "People Ops",
]

ROLES = {
    "Engineering": ["Engineering Senior Backend", "Engineering Senior Frontend", "Engineering Staff SRE"],
    "Product": ["Product Senior PM", "Product Associate PM", "Product Principal PM"],
    "Design": ["Design Senior IC", "Design Lead", "Design Principal"],
    "Marketing": ["Marketing Growth Lead", "Marketing Brand Manager", "Marketing Content Strategist"],
    "Sales": ["Sales AE", "Sales Senior AE", "Sales SDR"],
    "Customer Success": ["Customer Success CSM", "Customer Success Senior CSM", "Customer Success Manager"],
    "Finance": ["Finance Analyst", "Finance Senior Analyst", "Finance Controller"],
    "People Ops": ["People Ops Recruiter", "People Ops Senior HRBP", "People Ops Coordinator"],
}

RECRUITERS = ["Maya Chen", "Devon Park", "Aisha Patel", "Marcus Reid", "Sofia Ruiz"]

TTF_RANGES = {
    "Engineering": (35, 55),
    "Product": (30, 48),
    "Design": (28, 45),
    "Marketing": (22, 38),
    "Sales": (18, 32),
    "Customer Success": (20, 35),
    "Finance": (25, 40),
    "People Ops": (20, 34),
}

COST_RANGES = {
    "Engineering": (8000, 15000),
    "Product": (6000, 11000),
    "Design": (5000, 9000),
    "Marketing": (3000, 6500),
    "Sales": (3500, 7000),
    "Customer Success": (2500, 5500),
    "Finance": (4000, 8000),
    "People Ops": (3000, 6000),
}

SOURCES = ["LinkedIn", "Referral", "Career Site", "Indeed", "Recruiter Outreach", "Glassdoor"]

SOURCE_WEIGHTS = {
    "LinkedIn": 0.30,
    "Referral": 0.20,
    "Career Site": 0.18,
    "Indeed": 0.14,
    "Recruiter Outreach": 0.11,
    "Glassdoor": 0.07,
}

# Referral intentionally has higher hire conversion — signal for AI to find
SOURCE_HIRE_RATES = {
    "LinkedIn": 0.04,
    "Referral": 0.14,
    "Career Site": 0.05,
    "Indeed": 0.03,
    "Recruiter Outreach": 0.08,
    "Glassdoor": 0.03,
}


def _assign_recruiter(dept: str, role: str) -> str:
    idx = abs(hash(f"{dept}:{role}")) % len(RECRUITERS)
    return RECRUITERS[idx]


def build_staffing_data() -> pd.DataFrame:
    rows = []
    for dept in DEPARTMENTS:
        roles = ROLES[dept]
        ttf_low, ttf_high = TTF_RANGES[dept]
        cost_low, cost_high = COST_RANGES[dept]

        for role in roles:
            recruiter = _assign_recruiter(dept, role)
            for month in MONTHS:
                openings = int(RNG.integers(1, 7))
                applicants = int(RNG.integers(25, 181))
                interviews = int(round(applicants * RNG.uniform(0.25, 0.55)))
                offers = int(round(interviews * RNG.uniform(0.15, 0.45)))
                hires = int(min(offers, round(openings * RNG.uniform(0.6, 1.2))))
                ttf = round(float(RNG.uniform(ttf_low, ttf_high)) + float(RNG.normal(0, 2)), 1)
                cost = int(RNG.integers(cost_low, cost_high + 1))
                oar = round(hires / max(offers, 1), 2)

                rows.append({
                    "Department": dept,
                    "Role": role,
                    "Month": month.strftime("%Y-%m"),
                    "Recruiter": recruiter,
                    "Openings": openings,
                    "Applicants": applicants,
                    "Interviews": interviews,
                    "Offers": offers,
                    "Hires": hires,
                    "Avg Time to Fill (days)": ttf,
                    "Cost per Hire ($)": cost,
                    "Offer Acceptance Rate": oar,
                })
    return pd.DataFrame(rows)


def build_source_breakdown(staffing_df: pd.DataFrame) -> pd.DataFrame:
    monthly_dept = (
        staffing_df.groupby(["Department", "Month"])["Applicants"].sum().reset_index()
    )
    rows = []
    for _, row in monthly_dept.iterrows():
        dept = row["Department"]
        month = row["Month"]
        total_applicants = int(row["Applicants"])

        weights = np.array([SOURCE_WEIGHTS[s] for s in SOURCES], dtype=float)
        noise = RNG.uniform(-0.02, 0.02, size=len(weights))
        weights = np.maximum(weights + noise, 0.01)
        weights = weights / weights.sum()

        counts = RNG.multinomial(total_applicants, weights)
        for source, count in zip(SOURCES, counts):
            hire_rate = SOURCE_HIRE_RATES[source]
            hires = int(round(count * hire_rate * RNG.uniform(0.7, 1.3)))
            hires = max(0, hires)
            rows.append({
                "Department": dept,
                "Month": month,
                "Source": source,
                "Applicants": int(count),
                "Hires": hires,
            })
    return pd.DataFrame(rows)


if __name__ == "__main__":
    staffing_df = build_staffing_data()
    staffing_df.to_csv(DATA_DIR / "staffing_data.csv", index=False)

    source_df = build_source_breakdown(staffing_df)
    source_df.to_csv(DATA_DIR / "source_breakdown.csv", index=False)

    print(
        f"Generated {len(staffing_df)} rows → data/staffing_data.csv | "
        f"{len(source_df)} rows → data/source_breakdown.csv"
    )
