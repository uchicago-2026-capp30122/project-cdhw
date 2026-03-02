import zipfile
import urllib.request
import geopandas as gpd
import pandas as pd
from pathlib import Path

DATA_DIR = Path("data")
PROCESSED_DIR = DATA_DIR / "processed"

# Ensure directories exist, before writing GeoJSON files to them.
DATA_DIR.mkdir(parents=True, exist_ok=True)
PROCESSED_DIR.mkdir(parents=True, exist_ok=True)

# 2024 TIGER/Line Census Tracts for Illinois (STATEFP=17)
TIGER_URL = "https://www2.census.gov/geo/tiger/TIGER2024/TRACT/tl_2024_17_tract.zip"
ZIP_PATH = DATA_DIR / "tl_2024_17_tract.zip"
EXTRACT_DIR = DATA_DIR / "tl_2024_17_tract"

# Cook=031, DuPage=043
COUNTYFPS = ["031", "043"]
OUT_COOK_DUPAGE_GEOJSON = PROCESSED_DIR / "tracts_cook_dupage.geojson"
OUT_CHICAGO_GEOJSON = PROCESSED_DIR / "tracts_chicago.geojson"

CROSSWALK_CSV = PROCESSED_DIR / "tract_to_ca_crosswalk.csv"


def main():
    if not ZIP_PATH.exists():
        print(f"Downloading: {TIGER_URL}")
        urllib.request.urlretrieve(TIGER_URL, ZIP_PATH)

    # Extract (if not already extracted)
    if not EXTRACT_DIR.exists():
        EXTRACT_DIR.mkdir(parents=True, exist_ok=True)
        with zipfile.ZipFile(ZIP_PATH, "r") as z:
            z.extractall(EXTRACT_DIR)

    # Find the .shp inside the extracted folder
    shp_path = None
    for fn in EXTRACT_DIR.iterdir():
        if fn.suffix == ".shp":
            shp_path = fn
            break
    if shp_path is None:
        raise FileNotFoundError("Could not find .shp in extracted TIGER folder")

    gdf = gpd.read_file(shp_path)

    # Filter to Cook + DuPage
    gdf = gdf[gdf["COUNTYFP"].isin(COUNTYFPS)].copy()
    
    # create a GEOID column in a stable way (added)
    # Some TIGER files have GEOID already; if not, build from STATEFP+COUNTYFP+TRACTCE
    if "GEOID" not in gdf.columns:
        gdf["GEOID"] = gdf["STATEFP"].astype(str) + gdf["COUNTYFP"].astype(str) + gdf["TRACTCE"].astype(str)
    gdf["GEOID"] = gdf["GEOID"].astype(str).str.zfill(11)

    # keep a Cook + DuPage copy BEFORE Chicago-only filtering
    gdf_cook_dup = gdf.copy()

    # keep only needed columns + WGS84 for BOTH outputs
    keep_cols = ["GEOID", "COUNTYFP", "geometry"]
    gdf_cook_dup = gdf_cook_dup[keep_cols].to_crs(epsg=4326)

    # write Cook + DuPage tracts output BEFORE Chicago-only filtering 
    print("Writing the GeoJSON for Cook + DuPage county tracts...")
    gdf_cook_dup.to_file(OUT_COOK_DUPAGE_GEOJSON, driver="GeoJSON")
    print(f"Wrote: {OUT_COOK_DUPAGE_GEOJSON} (# tracts = {len(gdf_cook_dup)})")
    
    ## Filter to Chicago-only using centroids & community areas boundary
    # Load community areas
    ca = gpd.read_file(PROCESSED_DIR / "community_areas.geojson")

    # Match CRS
    ca = ca.to_crs(gdf.crs)

    # Dissolve 77 community areas into one city polygon
    city_poly = ca.dissolve().geometry.iloc[0]

    # Keep tracts whose centroid is inside Chicago
    gdf["centroid"] = gdf.geometry.centroid
    gdf_chi = gdf[gdf["centroid"].within(city_poly)].copy()
    gdf_chi = gdf_chi.drop(columns=["centroid"])

    # Keep only needed columns + convert to WGS84
    gdf_chi = gdf_chi[keep_cols].to_crs(epsg=4326)

    # write Chicago-only tracts output
    print("Writing the GeoJSON for Chicago-only tracts...")
    gdf_chi.to_file(str(OUT_CHICAGO_GEOJSON), driver="GeoJSON")
    print(f"Wrote: {OUT_CHICAGO_GEOJSON} (# tracts = {len(gdf_chi)})")


if __name__ == "__main__":
    main()