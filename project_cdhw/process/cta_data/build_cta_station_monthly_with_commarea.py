"""
build_cta_station_monthly_with_commarea.py

Joins CTA ridership -> station locations -> community areas -> census.

ID bridge: ridership station_id - 40000 == location station_id

Inputs:
    data/processed/cta_station_monthly_2024_clean.csv
    data/processed/cta_station_locations_clean.csv
    data/processed/community_areas.pretty.geojson
    data/processed/community_area_census.csv

Output:
    data/processed/cta_station_monthly_2024_geo_commarea.csv
"""

from pathlib import Path
from typing import NamedTuple
from shapely.geometry import Point, shape
import json
import pandas as pd


RID_PATH = Path("data/processed/cta_station_monthly_2024_clean.csv")
LOC_PATH = Path("data/processed/cta_station_locations_clean.csv")
CA_GEO_PATH = Path("data/processed/community_areas.pretty.geojson")
CA_CEN_PATH = Path("data/processed/community_area_census.csv")
OUT_PATH = Path("data/processed/cta_station_monthly_yearly_2024_geo_commarea.csv")


class RidershipRow(NamedTuple):
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


class CommunityArea(NamedTuple):
    community_area: int
    community: str
    polygon: object


class CensusRow(NamedTuple):
    community_area: int
    pop_total: float
    median_hh_income: float
    pct_no_vehicle_hh: float
    pct_disabled: float
    pct_65_plus: float
    transportation_need_index_0_100: float
    need_quintile: str


def load_ridership(path: Path) -> list[RidershipRow]:
    """Read cleaned ridership CSV into a list of RidershipRows."""
    df = pd.read_csv(path)
    rows = []
    for _, row in df.iterrows():
        rows.append(
            RidershipRow(
                station_id=int(row["station_id"]),
                station_name=str(row["station_name"]),
                month_beginning=str(row["month_beginning"]),
                year=int(row["year"]),
                month=int(row["month"]),
                month_total=int(row["month_total"]),
            )
        )
    return rows


def load_locations(path: Path) -> dict[int, StationLocation]:
    """
    Read cleaned station locations into a dict keyed by station_id.
    Makes lookup O(1) when joining to ridership.
    """
    df = pd.read_csv(path)
    locations = {}
    for _, row in df.iterrows():
        sid = int(row["station_id"])
        locations[sid] = StationLocation(
            station_id=sid,
            station_name=str(row["station_name"]),
            line_name=str(row["line_name"]),
            lat=float(row["lat"]),
            lon=float(row["lon"]),
        )
    return locations


def load_community_areas(path: Path) -> list[CommunityArea]:
    """Read community area GeoJSON into a list of CommunityArea NamedTuples."""
    with open(path) as f:
        geojson = json.load(f)

    areas = []
    for feature in geojson["features"]:
        props = feature["properties"]
        areas.append(
            CommunityArea(
                community_area=int(props["community_area"]),
                community=str(props["community"]),
                polygon=shape(feature["geometry"]),
            )
        )
    return areas


def load_census(path: Path) -> dict[int, CensusRow]:
    """Read census CSV into a dict keyed by community_area."""
    df = pd.read_csv(path)
    census = {}
    for _, row in df.iterrows():
        ca = int(row["community_area"])
        census[ca] = CensusRow(
            community_area=ca,
            pop_total=row["pop_total"],
            median_hh_income=row["median_hh_income"],
            pct_no_vehicle_hh=row["pct_no_vehicle_hh"],
            pct_disabled=row["pct_disabled"],
            pct_65_plus=row["pct_65_plus"],
            transportation_need_index_0_100=row["transportation_need_index_0_100"],
            need_quintile=row["need_quintile"],
        )
    return census


def find_community_area(point: Point, community_areas: list[CommunityArea]):
    """
    Return the CommunityArea that contains the point, or None if outside Chicago.
    """
    for ca in community_areas:
        if ca.polygon.covers(point):
            return ca
    return None


def main() -> None:
    OUT_PATH.parent.mkdir(parents=True, exist_ok=True)

    ridership_rows = load_ridership(RID_PATH)
    locations = load_locations(LOC_PATH)
    community_areas = load_community_areas(CA_GEO_PATH)
    census = load_census(CA_CEN_PATH)

    out_rows = []
    dropped = 0

    for rid in ridership_rows:
        # bridge: ridership station_id - 40000 == location station_id
        geo_station_id = rid.station_id - 40000
        loc = locations.get(geo_station_id)

        if loc is None:
            print(
                f"  No location found for station_id {rid.station_id} ({rid.station_name})"
            )
            continue

        point = Point(loc.lon, loc.lat)
        ca = find_community_area(point, community_areas)

        # drop stations outside Chicago
        if ca is None:
            dropped += 1
            continue

        cen = census.get(ca.community_area)

        row = {
            "station_id": rid.station_id,
            "station_name": rid.station_name,
            "month_beginning": rid.month_beginning,
            "year": rid.year,
            "month": rid.month,
            "month_total": rid.month_total,
            "geo_station_id": geo_station_id,
            "line_name": loc.line_name,
            "lat": loc.lat,
            "lon": loc.lon,
            "community_area": ca.community_area,
            "community": ca.community,
            "pop_total": cen.pop_total if cen else None,
            "median_hh_income": cen.median_hh_income if cen else None,
            "pct_no_vehicle_hh": cen.pct_no_vehicle_hh if cen else None,
            "pct_disabled": cen.pct_disabled if cen else None,
            "pct_65_plus": cen.pct_65_plus if cen else None,
            "transportation_need_index_0_100": cen.transportation_need_index_0_100
            if cen
            else None,
            "need_quintile": cen.need_quintile if cen else None,
        }
        out_rows.append(row)

    final = pd.DataFrame(out_rows)
    annual = final.groupby("station_id")["month_total"].sum().rename("annual_total")
    final = final.merge(annual, on="station_id")

    final.to_csv(OUT_PATH, index=False)

    print(f"Dropped {dropped} rows outside Chicago city limits")
    print(f"Wrote {OUT_PATH}")
    print(f"Rows:            {len(final)}")
    print(f"Stations:        {final['station_id'].nunique()}")
    print(f"Community areas: {final['community_area'].nunique()}")


if __name__ == "__main__":
    main()
