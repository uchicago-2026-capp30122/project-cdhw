import os
import requests
from shapely.geometry import shape as shape_geojson
from dotenv import load_dotenv
import pandas as pd

# Load environment variables from .env file
load_dotenv()

# ----------------------------
# Config
# ----------------------------
SOCRATA_APP_TOKEN = os.environ.get("SOCRATA_APP_TOKEN")
if not SOCRATA_APP_TOKEN:
    raise RuntimeError("SOCRATA_APP_TOKEN is not set (fish: set -x SOCRATA_APP_TOKEN your_token).")

HEADERS = {
    "Accept": "application/json",
    "X-App-Token": SOCRATA_APP_TOKEN,
}

# SODA 3.0 view IDs
COMMUNITY_AREAS = "igwz-8jzy"   # Community area boundaries (GeoJSON geometry)
TNP_TRIPS_2025 = "6dvr-xwnh"    # Rideshare trips dataset
ACS_CA = "t68z-cikk"            # American Community Survey data by community area
CTA_STATIONS = "vmyy-m9qj"      # CTA Stations
CTA_RIDERSHIP = "t2rn-p8d7"     # CTA Monthly L entries
CTA_GEO_POINTS = "3tzw-cg4m"    # CTA Station Location Joinder
CTA_STATIONS_ZIP_URL = (
    "https://data.cityofchicago.org/download/vmyy-m9qj/application%2Fx-zip-compressed"
)
# ----------------------------
# SODA3 query + row extraction
# ----------------------------
def soda3_post(view_id: str, soql: str, page_number: int = 1, page_size: int = 50000, timeout=(10, 300)):
    url = f"https://data.cityofchicago.org/api/v3/views/{view_id}/query.json"
    payload = {
        "query": soql,
        "page": {"pageNumber": page_number, "pageSize": page_size},
        "includeSynthetic": False,
    }
    resp = requests.post(url, headers=HEADERS, json=payload, timeout=timeout)
    if resp.status_code != 200:
        raise RuntimeError(f"SODA3 error {resp.status_code}: {resp.text[:1200]}")
    return resp.json()

# ----------------------------
# Community Areas -> centroids (GeoJSON dict geometry)
# ----------------------------
def get_community_areas():
    """
    Returns a dict keyed by community area id (as int), with:
      - name
      - lon/lat centroid
    Node IDs are derived from the API so they automatically track future changes.
    """
    soql = "SELECT area_numbe, community, the_geom"
    rows = soda3_post(COMMUNITY_AREAS, soql, page_size=5000)

    areas = {}  # ca_id -> {"name": str, "lon": float, "lat": float}
    for r in rows:
        if not isinstance(r, dict):
            raise RuntimeError(f"Unexpected row type from community areas API: {type(r)}")

        ca_raw = r.get("area_numbe")
        name = (r.get("community") or "").strip()
        geom_raw = r.get("the_geom")

        if ca_raw is None or geom_raw is None:
            continue

        ca_id = int(ca_raw)

        # GeoJSON dict like: {"type":"MultiPolygon","coordinates":[...]}
        geom = shape_geojson(geom_raw)
        c = geom.centroid  # x=lon, y=lat (WGS84)
        areas[ca_id] = {"name": name, "lon": float(c.x), "lat": float(c.y)}

    if len(areas) == 0:
        raise RuntimeError("No community areas returned; check API token / permissions / view id.")
    return areas

# ----------------------------
# Rideshare edges (grouped OD counts) via SODA3
# ----------------------------
def get_edges_grouped_by_ca(date_start=None, date_end=None):
    where = [
        "pickup_community_area IS NOT NULL",
        "dropoff_community_area IS NOT NULL",
    ]
    if date_start and date_end:
        where.append(f"trip_start_timestamp >= '{date_start}'")
        where.append(f"trip_start_timestamp <  '{date_end}'")

    soql = f"""
    SELECT
      pickup_community_area,
      dropoff_community_area,
      count(*) AS trips
    WHERE
      {" AND ".join(where)}
    GROUP BY
      pickup_community_area,
      dropoff_community_area
    """

    return soda3_post(TNP_TRIPS_2025, soql, page_size=10000, timeout=(10, 600))

# ----------------------------
# ACS Population -> dict {Area Name: Population}
# ----------------------------
def get_population_by_ca():
    """
    Returns a dict mapping community area NAME (str) -> Total Population (int).
    Note: The ACS dataset uses names ('Rogers Park', 'West Ridge', etc.),
    not the numeric ID, so we'll match by name later.
    """
    soql = "SELECT community_area, total_population"
    rows = soda3_post(ACS_CA, soql, page_size=1000)



    pop_map = {}
    for r in rows:
        if not isinstance(r, dict):
            continue
        
        c_name = r.get("community_area")
        pop_str = r.get("total_population")

        if c_name and pop_str:
            try:
                # Parse population count
                pop_map[c_name.strip()] = int(float(pop_str))
            except ValueError:
                pass  # skip if population is not a valid number
    
    return pop_map

# ----------------------------
# CTA Information, Reading files
# ----------------------------

def fetch_csv(view_id: str, limit: int = 50000) -> pd.DataFrame:
    url = f"https://data.cityofchicago.org/resource/{view_id}.csv?$limit={limit}"
    return pd.read_csv(url)

def download_file(url: str, timeout=(10, 120)) -> bytes:
    resp = requests.get(url, headers=HEADERS, timeout=timeout)
    if resp.status_code != 200:
        raise RuntimeError(f"Download error {resp.status_code}: {resp.text[:1200]}")
    return resp.content