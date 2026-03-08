"""
NEW_fetch_cta_raw.py

Fetches raw CTA data from the Chicago Data Portal API.

Outputs:
    data/raw/cta_station_monthly_2024_raw.csv
    data/raw/cta_station_geo_points_raw.csv
"""

from pathlib import Path
import sys

ROOT_DIR = Path(__file__).resolve().parents[2]
if str(ROOT_DIR) not in sys.path:
    sys.path.insert(0, str(ROOT_DIR))

from src.api_client import (
    CTA_GEO_POINTS,
    CTA_RIDERSHIP,
    fetch_csv,
)


RAW_DIR = Path("data/raw")

RIDERSHIP_OUT  = RAW_DIR / "cta_station_monthly_2024_raw.csv"
GEO_POINTS_OUT = RAW_DIR / "cta_station_geo_points_raw.csv"


def ensure_raw_dirs() -> None:
    RAW_DIR.mkdir(parents=True, exist_ok=True)


def fetch_cta_station_monthly() -> None:
    """Fetch CTA L monthly station ridership raw data."""
    ridership_raw = fetch_csv(CTA_RIDERSHIP, limit=100000)
    ridership_raw.to_csv(RIDERSHIP_OUT, index=False)


def fetch_cta_geo_points() -> None:
    """Fetch CTA station geo points raw data."""
    geo_points_raw = fetch_csv(CTA_GEO_POINTS, limit=5000)
    geo_points_raw.to_csv(GEO_POINTS_OUT, index=False)


def main() -> None:
    ensure_raw_dirs()
    fetch_cta_station_monthly()
    fetch_cta_geo_points()

    print(f"Wrote raw monthly ridership to: {RIDERSHIP_OUT}")
    print(f"Wrote raw station geo points to: {GEO_POINTS_OUT}")


if __name__ == "__main__":
    main()