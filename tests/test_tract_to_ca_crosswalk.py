import pytest
import pandas as pd
from pathlib import Path


def test_crosswalk_csv():
    crosswalk_path = Path("data/processed/tract_to_ca_crosswalk.csv")
    if not crosswalk_path.exists():
        pytest.skip(f"{crosswalk_path} not found")

    df = pd.read_csv(crosswalk_path)

    # columns exist
    assert "GEOID" in df.columns
    assert "community_area" in df.columns
    assert "weight" in df.columns

    # weights are in range
    assert (df["weight"] > 0).all(), "Found weights <= 0"
    assert (df["weight"] <= 1.0001).all(), "Found weights > 1"

    # sum of weights
    grouped_weights = df.groupby("GEOID")["weight"].sum()
    assert (grouped_weights >= 0.98).all(), "Some tracts have weight sum < 0.98"
    assert (grouped_weights <= 1.02).all(), "Some tracts have weight sum > 1.02"

    # community_area values
    assert df["community_area"].between(1, 77).all(), "Community area not in 1-77"
