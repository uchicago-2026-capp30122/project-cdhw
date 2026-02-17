import pytest
from unittest.mock import patch, MagicMock
from src.api_client import get_community_areas, get_edges_grouped_by_ca, get_population_by_ca

# Sample mocked data
SAMPLE_AREAS_RESPONSE = [
    {
        "area_numbe": "1",
        "community": "ROGERS PARK",
        "the_geom": {
            "type": "MultiPolygon",
            "coordinates": [[[[ -87.67, 42.02], [-87.66, 42.02], [-87.66, 42.01], [-87.67, 42.01]]]]
        }
    }
]

SAMPLE_TRIPS_RESPONSE = [
    {
        "pickup_community_area": "1",
        "dropoff_community_area": "2",
        "trips": "100"
    }
]

SAMPLE_POPULATION_RESPONSE = [
    {"community_area": "ROGERS PARK", "total_population": "50000.0"},
    {"community_area": "INVALID AREA", "total_population": "nan"}
]

@patch("src.api_client.requests.post")
@patch("src.api_client.os.environ.get")
def test_get_community_areas(mock_env, mock_post):
    """Test fetching and parsing community areas."""
    mock_env.return_value = "fake_token"
    
    # Mock successful response
    mock_resp = MagicMock()
    mock_resp.status_code = 200
    mock_resp.json.return_value = SAMPLE_AREAS_RESPONSE
    mock_post.return_value = mock_resp
    
    areas = get_community_areas()
    
    assert 1 in areas
    assert areas[1]["name"] == "ROGERS PARK"
    assert "lon" in areas[1]
    assert "lat" in areas[1]

@patch("src.api_client.requests.post")
def test_get_edges_grouped_by_ca(mock_post):
    """Test fetching and parsing aggregated trip data."""
    mock_resp = MagicMock()
    mock_resp.status_code = 200
    mock_resp.json.return_value = SAMPLE_TRIPS_RESPONSE
    mock_post.return_value = mock_resp
    
    edges = get_edges_grouped_by_ca("2025-01-01", "2025-01-02")
    
    assert isinstance(edges, list)
    assert len(edges) == 1
    assert edges[0]["trips"] == "100"

@patch("src.api_client.requests.post")
def test_get_population_by_ca(mock_post):
    """Test fetching and robust int(float(str)) parsing of population data."""
    mock_resp = MagicMock()
    mock_resp.status_code = 200
    mock_resp.json.return_value = SAMPLE_POPULATION_RESPONSE
    mock_post.return_value = mock_resp
    
    pop_map = get_population_by_ca()
    
    assert "ROGERS PARK" in pop_map
    assert pop_map["ROGERS PARK"] == 50000  # Should be converted to int
    assert "INVALID AREA" not in pop_map   # Should be skipped

@patch("src.api_client.requests.post")
def test_api_failure(mock_post):
    """Test that non-200 responses raise RuntimeError."""
    mock_resp = MagicMock()
    mock_resp.status_code = 403
    mock_resp.text = "Forbidden"
    mock_post.return_value = mock_resp
    
    with pytest.raises(RuntimeError) as excinfo:
        get_community_areas()
    
    assert "SODA3 error 403" in str(excinfo.value)
