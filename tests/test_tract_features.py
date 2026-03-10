import pytest
import pandas as pd
from process.census_data.make_tract_features import (
    add_need_component_scores,
    add_need_index_percentile,
)


def test_add_need_component_scores():
    df = pd.DataFrame(
        {
            "GEOID": ["00000000001", "00000000002", "00000000003"],
            "pct_no_vehicle_hh": [10, 20, 30],  # Higher = higher need
            "median_hh_income": [50000, 30000, 10000],  # Lower = higher need
        }
    )

    res = add_need_component_scores(
        df, high_vars={"pct_no_vehicle_hh"}, low_vars={"median_hh_income"}
    )

    assert "pct_no_vehicle_hh_need_0_100" in res.columns
    assert "median_hh_income_need_0_100" in res.columns

    scores = res["pct_no_vehicle_hh_need_0_100"].tolist()
    assert scores[0] < scores[1] < scores[2]

    inc_scores = res["median_hh_income_need_0_100"].tolist()
    assert inc_scores[0] < inc_scores[1] < inc_scores[2]


def test_add_need_index_percentile():
    df = pd.DataFrame(
        {
            "GEOID": ["00000000001", "00000000002"],
            "var1_need_0_100": [20.0, 80.0],
            "var2_need_0_100": [40.0, 60.0],
        }
    )
    weights = {"var1": 1.0, "var2": 1.0}
    res = add_need_index_percentile(df, weights=weights)

    assert "transportation_need_index_0_100" in res.columns
    assert res.loc[0, "transportation_need_index_0_100"] == 30.0  # (20+40)/2
    assert res.loc[1, "transportation_need_index_0_100"] == 70.0  # (80+60)/2


def test_tract_features_file():
    from pathlib import Path

    features_path = Path("data/processed/tract_features.csv")
    if not features_path.exists():
        pytest.skip(f"{features_path} not found")

    df = pd.read_csv(features_path, dtype={"GEOID": str})

    # GEOID is string and 11 characters
    assert pd.api.types.is_string_dtype(df["GEOID"])
    assert (df["GEOID"].str.len() == 11).all()

    # transport_need_index exists and is within expected range
    assert "transportation_need_index_0_100" in df.columns
    assert df["transportation_need_index_0_100"].dropna().ge(0).all()
    assert df["transportation_need_index_0_100"].dropna().le(100).all()
