import pytest
import pandas as pd
from unittest.mock import patch, MagicMock
from process.census_data.fetch_census_data import build_census_csv, FetchException
from process.cta_data.fetch_cta_raw import (
    fetch_cta_station_monthly,
    fetch_cta_geo_points,
)
from process.rideshare_data.fetch_rideshare_data import compile_rideshare


@patch("process.rideshare_data.fetch_rideshare_data.get_edges_grouped_by_ca")
@patch("process.rideshare_data.fetch_rideshare_data.get_community_areas")
def test_compile_rideshare(mock_areas, mock_edges, tmp_path):
    mock_edges.return_value = [
        {"pickup_community_area": "1", "dropoff_community_area": "2", "trips": 100}
    ]

    mock_areas.return_value = {
        1: {"name": "Area 1", "lat": 41.1, "lon": -87.1},
        2: {"name": "Area 2", "lat": 41.2, "lon": -87.2},
    }

    with patch("builtins.open", new_callable=MagicMock) as mock_open:
        compile_rideshare()
        # Verify it opened the file to write
        mock_open.assert_called_with(
            "data/processed/rideshare_community_areas.json", "w"
        )
