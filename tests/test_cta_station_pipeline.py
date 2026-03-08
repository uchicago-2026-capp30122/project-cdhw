from pathlib import Path
import pandas as pd
import pytest


PROCESSED = Path("data/processed")

RIDERSHIP = PROCESSED / "cta_station_monthly_2024_clean.csv"
LOCATIONS = PROCESSED / "cta_station_locations_clean.csv"
GEO_CA = PROCESSED / "cta_station_monthly_2024_geo_commarea.csv"


@pytest.mark.skipif(not RIDERSHIP.exists(), reason="ridership file not built yet")
def test_ridership_no_missing_totals():
    df = pd.read_csv(RIDERSHIP)
    assert df["month_total"].isna().sum() == 0


@pytest.mark.skipif(not RIDERSHIP.exists(), reason="ridership file not built yet")
def test_ridership_unique_station_month():
    df = pd.read_csv(RIDERSHIP)
    assert df.duplicated(subset=["station_id", "month"]).sum() == 0


@pytest.mark.skipif(not LOCATIONS.exists(), reason="locations file not built yet")
def test_locations_no_missing_coords():
    df = pd.read_csv(LOCATIONS)
    assert df["lat"].isna().sum() == 0
    assert df["lon"].isna().sum() == 0


@pytest.mark.skipif(not LOCATIONS.exists(), reason="locations file not built yet")
def test_locations_chicago_lat_range():
    df = pd.read_csv(LOCATIONS)
    assert df["lat"].between(41.6, 42.1).all()


@pytest.mark.skipif(
    not GEO_CA.exists(), reason="geom community area file not built yet"
)
def test_geo_commarea_no_missing_community():
    df = pd.read_csv(GEO_CA)
    assert df["community_area"].isna().sum() == 0
    assert df["community"].isna().sum() == 0


@pytest.mark.skipif(
    not GEO_CA.exists(), reason="geom community area file not built yet"
)
def test_geo_commarea_id_bridge():
    df = pd.read_csv(GEO_CA)
    assert ((df["station_id"] - 40000) == df["geo_station_id"]).all()
