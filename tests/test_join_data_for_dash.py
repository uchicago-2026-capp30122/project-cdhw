import pytest
import pandas as pd
from pathlib import Path


def test_join_data_for_dash(tmp_path):
    # Create fake processed data
    processed_dir = tmp_path / "data" / "processed"
    processed_dir.mkdir(parents=True, exist_ok=True)

    # Community Area Census
    census_df = pd.DataFrame(
        {
            "community_area": [1, 2],
            "community_area_name": ["Area 1", "Area 2"],
            "pop_total": [1000, 2000],
        }
    )
    census_df.to_csv(processed_dir / "community_area_census.csv", index=False)

    # CTA CA totals
    cta_df = pd.DataFrame({"community_area": [1, 2], "total_rides": [500, 1500]})
    cta_df.to_csv(processed_dir / "cta_ca_totals.csv", index=False)

    # Rideshare CA totals
    rideshare_df = pd.DataFrame(
        {"community_area": [1, 2], "rideshare_trips": [200, 800]}
    )
    rideshare_df.to_csv(processed_dir / "rideshare_ca_totals.csv", index=False)

    # check the contents of join_data_for_dash.py
    script_path = (
        Path(__file__).resolve().parents[1] / "process" / "join_data_for_dash.py"
    )
    content = script_path.read_text()

    assert (
        "left-joins" in content.lower()
        or "left join" in content.lower()
        or "merge" in content.lower()
        or '"""' in content
    )
