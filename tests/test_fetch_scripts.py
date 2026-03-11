import pytest
import pandas as pd
from unittest.mock import patch, MagicMock
from project_cdhw.process.census_data.fetch_census_data import (
    build_census_csv,
    FetchException,
)
from project_cdhw.process.cta_data.fetch_cta_raw import (
    fetch_cta_station_monthly,
    fetch_cta_geo_points,
)
from project_cdhw.process.rideshare_data.fetch_rideshare_data import compile_rideshare


@patch(
    "project_cdhw.process.rideshare_data.fetch_rideshare_data.get_edges_grouped_by_ca"
)
@patch("project_cdhw.process.rideshare_data.fetch_rideshare_data.get_community_areas")
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
        mock_open.assert_called_with(
            "data/processed/rideshare_community_areas.json", "w"
        )


@patch("project_cdhw.process.census_data.fetch_census_data.httpx.get")
def test_build_census_csv(mock_get, tmp_path):
    mock_resp = MagicMock()
    mock_resp.status_code = 200
    mock_resp.json.return_value = [
        ["NAME", "B01003_001E", "state", "county", "tract"],
        ["Tract 1", "1000", "17", "031", "000000"],
    ]
    mock_get.return_value = mock_resp

    out_file = tmp_path / "test_census.csv"

    df = build_census_csv(2024, out_file)

    assert mock_get.call_count == 2
    assert len(df) == 2
    assert df.iloc[0]["NAME"] == "Tract 1"
    assert out_file.exists()


@patch("project_cdhw.process.cta_data.fetch_cta_raw.fetch_csv")
def test_fetch_cta_station_monthly(mock_fetch_csv):
    df_mock = pd.DataFrame({"station_id": [1], "rides": [100]})
    mock_fetch_csv.return_value = df_mock

    with patch(
        "project_cdhw.process.cta_data.fetch_cta_raw.RIDERSHIP_OUT",
        new_callable=MagicMock,
    ) as mock_out:
        fetch_cta_station_monthly()

    mock_fetch_csv.assert_called_once()


@patch("project_cdhw.process.cta_data.fetch_cta_raw.fetch_csv")
def test_fetch_cta_geo_points(mock_fetch_csv):
    df_mock = pd.DataFrame({"station_id": [1], "lat": [41.0]})
    mock_fetch_csv.return_value = df_mock

    with patch(
        "project_cdhw.process.cta_data.fetch_cta_raw.GEO_POINTS_OUT",
        new_callable=MagicMock,
    ) as mock_out:
        fetch_cta_geo_points()

    mock_fetch_csv.assert_called_once()
