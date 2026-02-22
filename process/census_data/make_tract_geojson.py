import os
import zipfile
import urllib.request

import geopandas as gpd

DATA_DIR = "data"
os.makedirs(DATA_DIR, exist_ok=True)

# 2024 TIGER/Line Census Tracts for Illinois (STATEFP=17)
TIGER_URL = "https://www2.census.gov/geo/tiger/TIGER2024/TRACT/tl_2024_17_tract.zip"
ZIP_PATH = os.path.join(DATA_DIR, "tl_2024_17_tract.zip")
EXTRACT_DIR = os.path.join(DATA_DIR, "tl_2024_17_tract")

# Cook=031, DuPage=043
COUNTYFPS = ["031", "043"]

OUT_GEOJSON = os.path.join(DATA_DIR, "il_tracts_2024_cook031_dup043.geojson")


def main():
    if not os.path.exists(ZIP_PATH):
        print(f"Downloading: {TIGER_URL}")
        urllib.request.urlretrieve(TIGER_URL, ZIP_PATH)

    # Extract (only if not already extracted)
    if not os.path.exists(EXTRACT_DIR):
        os.makedirs(EXTRACT_DIR, exist_ok=True)
        with zipfile.ZipFile(ZIP_PATH, "r") as z:
            z.extractall(EXTRACT_DIR)

    # Find the .shp inside the extracted folder
    shp_path = None
    for fn in os.listdir(EXTRACT_DIR):
        if fn.endswith(".shp"):
            shp_path = os.path.join(EXTRACT_DIR, fn)
            break
    if shp_path is None:
        raise FileNotFoundError("Could not find .shp in extracted TIGER folder")

    gdf = gpd.read_file(shp_path)

    # Filter to Cook + DuPage
    gdf = gdf[gdf["COUNTYFP"].isin(COUNTYFPS)].copy()

    # Keep what we need; GEOID is the tract join key (11 digits)
    gdf = gdf[["GEOID", "COUNTYFP", "geometry"]].copy()

    # GeoJSON likes WGS84 lat/lon
    gdf = gdf.to_crs(epsg=4326)

    gdf.to_file(OUT_GEOJSON, driver="GeoJSON")
    print(f"Wrote: {OUT_GEOJSON}  (rows={len(gdf)})")


if __name__ == "__main__":
    main()