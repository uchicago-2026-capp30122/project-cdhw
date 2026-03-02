"""
Download Chicago Community Areas boundaries (GeoJSON)
and standardize the join key to: properties.community_area

Output:
    data/processed/community_areas.geojson
"""

import json
from pathlib import Path
import httpx

OUT_PATH = Path("data/processed/community_areas.geojson")

# Chicago Data Portal dataset ID:
# "Boundaries - Community Areas (current)"
DATASET_ID = "cauq-8yn6"


def download_geojson() -> dict:
    """
    Download community areas GeoJSON using the geospatial export endpoint
    (matches what the Chicago Data Portal "Export GeoJSON" uses).
    """
    # same view id that src/api_client.py references for CA geometry
    view_id = "igwz-8jzy"

    url = (
        f"https://data.cityofchicago.org/api/geospatial/{view_id}"
        "?method=export&format=GeoJSON"
    )

    headers = {
        "Accept": "application/json",
        "User-Agent": "project-cdhw (httpx)"
    }

    with httpx.Client(timeout=120.0, follow_redirects=True) as client:
        resp = client.get(url, headers=headers)
        resp.raise_for_status()
        return resp.json()


def standardize_join_key(geojson: dict) -> dict:
    """
    Ensure every feature has:
        properties.community_area (int 1-77)

    The source dataset uses 'area_numbe'
    """
    for feature in geojson.get("features", []):
        props = feature.get("properties", {})

        raw = (
            props.get("area_numbe")
            or props.get("AREA_NUMBE")
            or props.get("community_area")
        )

        if raw is None:
            continue

        props["community_area"] = int(raw)
        feature["properties"] = props

    return geojson


def main():
    OUT_PATH.parent.mkdir(parents=True, exist_ok=True)

    print("Downloading community areas GeoJSON...")
    geojson = download_geojson()

    print("Standardizing join key...")
    geojson = standardize_join_key(geojson)

    # OUT_PATH.write_text(json.dumps(geojson)) # minified printing (all 77 CAs on 1 row)
    # OUT_PATH.write_text(json.dumps(geojson, indent=2)) # verbose printing, easier to read, but slower Dash performance.

    features = geojson.get("features", [])

    # creating GeoJSON #1: 1 community area per line
    out_main = OUT_PATH  # data/processed/community_areas.geojson
    with out_main.open("w") as f:
        f.write('{"type":"FeatureCollection","features":[\n')
        for i, feat in enumerate(features):
            line = json.dumps(feat, separators=(",", ":"))
            f.write(line)
            f.write(",\n" if i < len(features) - 1 else "\n")
        f.write("]}")

    # creating GeoJSON #2: pretty-print version (for readability/debugging only)
    out_pretty = OUT_PATH.with_name("community_areas.pretty.geojson")
    out_pretty.write_text(json.dumps(geojson, indent=2))

    print(f"Wrote {out_main}")
    print(f"Wrote {out_pretty}")
    print(f"Feature count: {len(features)}")


if __name__ == "__main__":
    main()