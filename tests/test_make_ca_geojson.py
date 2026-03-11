import pytest
import json
from pathlib import Path
from project_cdhw.process.census_data.make_ca_geojson import standardize_join_key


def test_standardize_join_key():
    mock_geojson = {
        "features": [
            {"properties": {"area_numbe": "1"}},
            {"properties": {"AREA_NUMBE": "2"}},
            {"properties": {"community_area": "3"}},
            {"properties": {"other_field": "4"}},
        ]
    }
    result = standardize_join_key(mock_geojson)
    features = result["features"]

    assert features[0]["properties"]["community_area"] == 1
    assert features[1]["properties"]["community_area"] == 2
    assert features[2]["properties"]["community_area"] == 3
    assert "community_area" not in features[3]["properties"]


def test_processed_geojson():
    processed_path = Path("data/processed/community_areas.geojson")
    if not processed_path.exists():
        pytest.skip(f"{processed_path} not found")

    with processed_path.open() as f:
        data = json.load(f)

    features = data.get("features", [])
    assert len(features) == 77, "Expected exactly 77 community areas"

    for feat in features:
        assert feat.get("geometry") is not None, "Geometry should not be null"
        props = feat.get("properties", {})
        ca = props.get("community_area")
        assert isinstance(ca, int), "community_area must be an integer"
        assert 1 <= ca <= 77, "community_area must be between 1 and 77"
