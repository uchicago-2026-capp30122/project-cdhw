import pytest
from unittest.mock import patch, MagicMock
import pandas as pd
import json
import os

# Set environment variable before importing api_client
os.environ["SOCRATA_APP_TOKEN"] = "test_token"

from src.api_client import (
    soda3_post,
    get_community_areas,
    get_edges_grouped_by_ca,
    get_population_by_ca,
    fetch_csv,
    download_file
)

@patch('src.api_client.requests.post')
def test_soda3_post_success(mock_post):
    mock_response = MagicMock()
    mock_response.status_code = 200
    mock_response.json.return_value = [{"col": "val"}]
    mock_post.return_value = mock_response

    result = soda3_post('view123', 'SELECT *')
    
    assert result == [{"col": "val"}]
    mock_post.assert_called_once()
    args, kwargs = mock_post.call_args
    assert "https://data.cityofchicago.org/api/v3/views/view123/query.json" in args[0]
    assert kwargs['json']['query'] == 'SELECT *'

@patch('src.api_client.requests.post')
def test_soda3_post_failure(mock_post):
    mock_response = MagicMock()
    mock_response.status_code = 400
    mock_response.text = "Bad Request"
    mock_post.return_value = mock_response

    with pytest.raises(RuntimeError) as exc_info:
        soda3_post('view123', 'SELECT *')
    
    assert "SODA3 error 400" in str(exc_info.value)

@patch('src.api_client.soda3_post')
def test_get_community_areas(mock_soda3_post):
    mock_soda3_post.return_value = [
        {
            "area_numbe": "1",
            "community": " ROGERS PARK ",
            "the_geom": {
                "type": "MultiPolygon",
                "coordinates": [[[[0.0, 0.0], [0.0, 1.0], [1.0, 1.0], [1.0, 0.0], [0.0, 0.0]]]]
            }
        },
        {
            "area_numbe": "2",
            "community": "NORWOOD PARK"
        }
    ]

    result = get_community_areas()
    
    assert len(result) == 1
    assert 1 in result
    assert result[1]["name"] == "ROGERS PARK"
    assert result[1]["lon"] is not None
    assert result[1]["lat"] is not None
    assert result[1]["lon"] == 0.5
    assert result[1]["lat"] == 0.5

@patch('src.api_client.soda3_post')
def test_get_edges_grouped_by_ca(mock_soda3_post):
    mock_soda3_post.return_value = [
        {"pickup_community_area": "1", "dropoff_community_area": "2", "trips": "15"}
    ]

    result = get_edges_grouped_by_ca(date_start="2024-01-01", date_end="2024-01-31")
    
    assert len(result) == 1
    assert result[0] == {"pickup_community_area": "1", "dropoff_community_area": "2", "trips": "15"}
    args, kwargs = mock_soda3_post.call_args
    assert "2024-01-01" in args[1]
    assert "2024-01-31" in args[1]

@patch('src.api_client.soda3_post')
def test_get_population_by_ca(mock_soda3_post):
    mock_soda3_post.return_value = [
        {"community_area": "Rogers Park", "total_population": "55000"},
        {"community_area": "Norwood Park", "total_population": "invalid"},
        {"community_area": "Lake View", "total_population": "100000.0"},
    ]

    result = get_population_by_ca()
    
    assert len(result) == 2
    assert result["Rogers Park"] == 55000
    assert result["Lake View"] == 100000

@patch('src.api_client.pd.read_csv')
def test_fetch_csv(mock_read_csv):
    df_mock = pd.DataFrame({"colA": [1, 2]})
    mock_read_csv.return_value = df_mock

    result = fetch_csv("abcd-1234", limit=100)
    
    pd.testing.assert_frame_equal(result, df_mock)
    mock_read_csv.assert_called_once_with("https://data.cityofchicago.org/resource/abcd-1234.csv?$limit=100")

@patch('src.api_client.requests.get')
def test_download_file(mock_get):
    mock_response = MagicMock()
    mock_response.status_code = 200
    mock_response.content = b"test content"
    mock_get.return_value = mock_response

    result = download_file("http://example.com/file.zip")
    
    assert result == b"test content"
    mock_get.assert_called_once()
