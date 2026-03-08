"""
clean_cta_data.py

Reads raw CTA files produced by NEW_fetch_cta_raw.py.
Writes two clean files to data/processed/.

the_geom column in geo points contains real lat long coordinates.
point_x / point_y are state plane feet and are ignored.

THE CROSSWALK BETWEEN THE DATASETS-
station_id in geo points matches ridership station_id via:
    ridership.station_id - 40000 == geo.station_id

Inputs:
    data/raw/cta_station_monthly_2024_raw.csv
    data/raw/cta_station_geo_points_raw.csv

Outputs:
    data/processed/cta_station_monthly_2024_clean.csv
    data/processed/cta_station_locations_clean.csv
"""

from pathlib import Path
from typing import NamedTuple
import re
import pandas as pd


RAW_DIR = Path("data/raw")
PROCESSED_DIR = Path("data/processed")

RAW_RIDERSHIP = RAW_DIR / "cta_station_monthly_2024_raw.csv"
RAW_GEO = RAW_DIR / "cta_station_geo_points_raw.csv"

OUT_RIDERSHIP = PROCESSED_DIR / "cta_station_monthly_2024_clean.csv"
OUT_LOCATIONS = PROCESSED_DIR / "cta_station_locations_clean.csv"


class StationRow(NamedTuple):
    station_id: int
    station_name: str
    month_beginning: str
    year: int
    month: int
    month_total: int


class StationLocation(NamedTuple):
    station_id: int
    station_name: str
    line_name: str
    lat: float
    lon: float


def get_lat_lon(the_geom: str) -> tuple[float, float]:
    """
    Pull lat and lon out of a point string like 'POINT (-87.6768 41.8849)'.
    Returns (lat, lon)

    """
    nums = re.findall(r"[-\d.]+", the_geom)
    lon, lat = float(nums[0]), float(nums[1])
    return lat, lon


def clean_ridership() -> list[StationRow]:
    """
    Read raw ridership CSV, keep only 2024 rows, and sum monthly totals
    per station. Some stations have multiple entrances that show up as
    separate rows — we collapse those into one row per station per month.

    """
    df = pd.read_csv(RAW_RIDERSHIP, parse_dates=["month_beginning"])
    df = df[df["month_beginning"].dt.year == 2024].copy()
    df = df.rename(columns={"stationame": "station_name", "monthtotal": "month_total"})
    df["station_name"] = df["station_name"].str.strip()
    df["year"] = df["month_beginning"].dt.year
    df["month"] = df["month_beginning"].dt.month

    # combining all entrances rows into a row per station, given that there are
    # several entries to one station
    df = df.groupby(["station_id", "month_beginning"], as_index=False).agg(
        station_name=("station_name", "first"),
        year=("year", "first"),
        month=("month", "first"),
        month_total=("month_total", "sum"),
    )

    rows = []
    for _, row in df.iterrows():
        rows.append(
            StationRow(
                station_id=int(row["station_id"]),
                station_name=row["station_name"],
                month_beginning=str(row["month_beginning"])[:10],
                year=int(row["year"]),
                month=int(row["month"]),
                month_total=int(row["month_total"]),
            )
        )
    return rows


def clean_locations() -> list[StationLocation]:
    """
    Read raw geo points, parse real WGS-84 coords from the_geom.
    One row per station already — no collapsing needed.
    """
    df = pd.read_csv(RAW_GEO)

    locations = []
    for _, row in df.iterrows():
        lat, lon = get_lat_lon(str(row["the_geom"]))
        locations.append(
            StationLocation(
                station_id=int(row["station_id"]),
                station_name=str(row["longname"]).strip(),
                line_name=str(row["lines"]).strip(),
                lat=lat,
                lon=lon,
            )
        )
    return sorted(locations, key=lambda x: x.station_id)


def main() -> None:
    PROCESSED_DIR.mkdir(parents=True, exist_ok=True)

    ridership = clean_ridership()
    locations = clean_locations()

    pd.DataFrame(ridership).to_csv(OUT_RIDERSHIP, index=False)
    pd.DataFrame(locations).to_csv(OUT_LOCATIONS, index=False)

    print(
        f"Ridership -> {OUT_RIDERSHIP}  ({len(ridership):,} rows, {len(set(r.station_id for r in ridership))} stations)"
    )
    print(f"Locations -> {OUT_LOCATIONS}  ({len(locations)} stations)")
    print("\nLocations sample:")
    print(pd.DataFrame(locations).head(3).to_string())


if __name__ == "__main__":
    main()
