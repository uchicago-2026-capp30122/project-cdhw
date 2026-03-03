from __future__ import annotations

from pathlib import Path

import pandas as pd
import pytest


BASE = Path("data/processed")
COMM_MONTHLY = BASE / "cta_commarea_monthly_2024.csv"
COMM_ANNUAL = BASE / "cta_commarea_annual_2024.csv"


@pytest.mark.skipif(not COMM_MONTHLY.exists(), reason="CTA commarea monthly table not built yet")
def test_commarea_monthly_no_missing() -> None:
    df = pd.read_csv(COMM_MONTHLY)
    assert df["community_area"].isna().sum() == 0
    assert df["cta_month_total"].isna().sum() == 0


@pytest.mark.skipif(not COMM_MONTHLY.exists(), reason="CTA commarea monthly table not built yet")
def test_commarea_monthly_unique_key() -> None:
    df = pd.read_csv(COMM_MONTHLY)
    assert df.duplicated(subset=["community_area", "year", "month"]).sum() == 0


@pytest.mark.skipif(not COMM_MONTHLY.exists(), reason="CTA commarea monthly table not built yet")
def test_commarea_monthly_has_12_months_2024() -> None:
    df = pd.read_csv(COMM_MONTHLY)
    df_2024 = df[df["year"] == 2024]
    assert sorted(df_2024["month"].unique().tolist()) == list(range(1, 13))


@pytest.mark.skipif(not (COMM_MONTHLY.exists() and COMM_ANNUAL.exists()), reason="CTA commarea tables not built yet")
def test_commarea_annual_total_matches_monthly_sum() -> None:
    m = pd.read_csv(COMM_MONTHLY)
    a = pd.read_csv(COMM_ANNUAL)
    m_sum = int(m[m["year"] == 2024]["cta_month_total"].sum())
    a_sum = int(a["cta_2024_total"].sum())
    assert m_sum == a_sum