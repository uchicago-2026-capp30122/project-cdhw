import pytest
import pandas as pd
from pathlib import Path
from project_cdhw.process.census_data.aggregate_tract_to_ca import (
    aggregate_to_ca,
    _infer_crosswalk_cols,
)


def test_infer_crosswalk_cols():
    df = pd.DataFrame({"GEOID": [], "community_area": [], "weight": []})
    geoid, ca, w = _infer_crosswalk_cols(df)
    assert geoid == "GEOID"
    assert ca == "community_area"
    assert w == "weight"


def test_aggregate_to_ca(monkeypatch):
    monkeypatch.setattr(
        "project_cdhw.process.census_data.aggregate_tract_to_ca.get_community_areas",
        lambda: {},
    )

    tract_df = pd.DataFrame(
        {
            "GEOID": ["00000000001", "00000000002"],
            "pop_total": [100.0, 200.0],
            "hh_total": [50.0, 100.0],
            "median_hh_income": [50000.0, 80000.0],
        }
    )

    xwalk = pd.DataFrame(
        {
            "GEOID": ["00000000001", "00000000002", "00000000002"],
            "community_area": [1, 1, 2],
            "weight": [1.0, 0.4, 0.6],
        }
    )

    out = aggregate_to_ca(tract_df, xwalk)

    assert list(out["community_area"]) == [1, 2]

    ca1 = out[out["community_area"] == 1].iloc[0]
    ca2 = out[out["community_area"] == 2].iloc[0]

    assert ca1["pop_total"] == 180.0
    assert ca2["pop_total"] == 120.0


def test_csv_file():
    ca_path = Path("data/processed/community_area_census.csv")
    if not ca_path.exists():
        pytest.skip(f"{ca_path} not found")

    df = pd.read_csv(ca_path)

    assert "community_area" in df.columns
    assert "pop_total" in df.columns

    assert (df["pop_total"] > 0).all()
