"""
1) Build the tract → community area crosswalk (weights)

Implement/run:
process/census_data/build_tract_to_ca_crosswalk.py

Inputs
data/processed/il_tracts_2024_cook031_dup043.geojson
data/processed/community_areas.geojson

Output
data/processed/tract_to_ca_crosswalk.csv
1 row per tract x CA overlap, so split tracts will take up >1 row.

What to sanity check
Columns: GEOID, community_area, weight
For most GEOIDs: sum(weight) ≈ 1.0

"""
# import warnings
from pathlib import Path
import geopandas as gpd
import pandas as pd


TRACTS_GEOJSON = Path("data/processed/il_tracts_2024_cook031_dup043.geojson")
CA_GEOJSON = Path("data/processed/community_areas.geojson")
OUT_CSV = Path("data/processed/tract_to_ca_crosswalk.csv")

# A good local projected CRS for Chicago/IL area calculations.
# (Area units don't matter for ratios; we just want a projected CRS, not lat/lon.)
AREA_CRS_EPSG = 3435  # NAD83 / Illinois East (ftUS)


# def _fix_geometries(gdf: gpd.GeoDataFrame) -> gpd.GeoDataFrame:
#     """Fix common invalid polygon issues (self-intersections, etc.)."""
#     gdf = gdf.copy()
#     # buffer(0) is a common quick fix for invalid polygons
#     gdf["geometry"] = gdf["geometry"].buffer(0)
#     return gdf


def main():
    if not TRACTS_GEOJSON.exists():
        raise FileNotFoundError(f"Missing tracts GeoJSON: {TRACTS_GEOJSON}")
    if not CA_GEOJSON.exists():
        raise FileNotFoundError(f"Missing community areas GeoJSON: {CA_GEOJSON}")

    OUT_CSV.parent.mkdir(parents=True, exist_ok=True)

    print("Reading tracts...")
    tracts = gpd.read_file(TRACTS_GEOJSON)

    # # Our Dash app uses featureidkey="properties.GEOID"
    # if "GEOID" not in tracts.columns:
    #     raise KeyError("Tracts GeoJSON must contain a GEOID column.")

    tracts["GEOID"] = tracts["GEOID"].astype(str).str.zfill(11)
    tracts = tracts[["GEOID", "geometry"]].copy()

    print("Reading community areas...")
    cas = gpd.read_file(CA_GEOJSON)

    if "community_area" not in cas.columns:
        raise KeyError("Community Areas GeoJSON must contain a community_area column in properties.")

    cas["community_area"] = pd.to_numeric(cas["community_area"], errors="coerce").astype("Int64")
    cas = cas.dropna(subset=["community_area"]).copy()
    cas["community_area"] = cas["community_area"].astype(int)
    cas = cas[["community_area", "geometry"]].copy()

    # Reproject both to a projected CRS for area calculations
    print(f"Projecting to EPSG:{AREA_CRS_EPSG} for area computations...")
    tracts = tracts.to_crs(epsg=AREA_CRS_EPSG)
    cas = cas.to_crs(epsg=AREA_CRS_EPSG)

    # # Fix invalid geometries (apparently common in boundary datasets)
    # with warnings.catch_warnings():
    #     warnings.simplefilter("ignore")
    #     tracts = _fix_geometries(tracts)
    #     cas = _fix_geometries(cas)

    # Compute each tract's total area
    tracts["tract_area"] = tracts.geometry.area
    tract_area = tracts[["GEOID", "tract_area"]].copy()

    print("Computing intersections (this can take a bit)...")
    # Intersection overlay: one row per (tract, community_area) overlap
    inter = gpd.overlay(tracts[["GEOID", "geometry"]], cas, how="intersection", keep_geom_type=True)

    if inter.empty:
        raise RuntimeError("Intersection result is empty. Check that both layers overlap and CRS is correct.")

    inter["inter_area"] = inter.geometry.area

    # Join tract areas and compute weight
    inter = inter.merge(tract_area, on="GEOID", how="left")
    inter["weight"] = inter["inter_area"] / inter["tract_area"]

    # Clean output
    out = inter[["GEOID", "community_area", "weight"]].copy()
    out = out.dropna(subset=["weight"])
    out = out[out["weight"] > 0]  # discard non-overlaps or numerical junk

    # Optional: drop extremely small slivers
    # out = out[out["weight"] >= 1e-6]

    # Normalize weights per tract to sum to 1 (helps with tiny floating-point drift)
    wsum = out.groupby("GEOID")["weight"].transform("sum")
    out["weight"] = out["weight"] / wsum

    # Save
    out.to_csv(OUT_CSV, index=False)
    print(f"Wrote {OUT_CSV} with {len(out):,} rows")

    # Sanity checks
    sums = out.groupby("GEOID")["weight"].sum()
    print(f"Tracts: {sums.shape[0]:,}")
    print(f"Weight sums (min/mean/max): {sums.min():.6f} / {sums.mean():.6f} / {sums.max():.6f}")

    split = (out.groupby("GEOID").size() > 1).sum()
    print(f"Tracts split across >1 community area: {split:,}")


if __name__ == "__main__":
    main()