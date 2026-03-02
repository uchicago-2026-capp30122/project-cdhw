from pathlib import Path
import pandas as pd
import geopandas as gpd
from shapely.geometry import Point

RID_PATH = Path("data/processed/cta_station_monthly_2024_clean.csv")
LOC_PATH = Path("data/processed/cta_station_locations_rail_clean.csv")

CA_GEO_PATH = Path("data/processed/community_areas.pretty.geojson")
CA_CENSUS_PATH = Path("data/processed/community_area_census.csv")

OUT_PATH = Path("data/processed/cta_station_monthly_2024_geo_commarea.csv")


# These are the ones we already discovered in exploration that need a small mapping
RID_FIX = {
    "medical center": "illinois medical district",
    "east 63rd cottage grove": "cottage grove",

    "addison brown": "addison",
    "irving park brown": "irving park",
    "montrose brown": "montrose",

    "ashland orange": "ashland",
    "halsted orange": "halsted",
    "pulaski orange": "pulaski",
    "western orange": "western",

    "damen brown": "damen",
    "kedzie brown": "kedzie",
    "western brown": "western",

    "roosevelt": "roosevelt state",
    "conservatory": "conservatory central park",
}


BRANCH_SUFFIXES = {
    "forest park", "o hare", "ohare",
    "cermak", "midway", "ravenswood", "lake",
    "congress", "douglas", "dan ryan",
}


def norm(s: str) -> str:
    s = str(s).strip().lower()
    s = s.replace("&", "and")
    s = s.replace("/", " ")
    s = s.replace("-", " ")
    s = " ".join(s.split())
    return s


def drop_branch_suffix(name: str) -> str:
    parts = norm(name).split()
    if len(parts) >= 3 and " ".join(parts[-2:]) in BRANCH_SUFFIXES:
        return " ".join(parts[:-2])
    if len(parts) >= 2 and parts[-1] in BRANCH_SUFFIXES:
        return " ".join(parts[:-1])
    return " ".join(parts)


def main() -> None:
    rid = pd.read_csv(RID_PATH)
    loc = pd.read_csv(LOC_PATH)

    # build rid join_key from station_name
    rid["base_key"] = rid["station_name"].apply(drop_branch_suffix)
    rid["join_key"] = rid["base_key"].replace(RID_FIX)

    # locations already have join_key from shapefile cleaning
    loc["join_key"] = loc["join_key"].astype(str).str.strip()

    # join ridership -> locations
    joined = rid.merge(
        loc[["join_key", "STATION_ID", "LONGNAME", "LINES", "lat", "lon"]],
        on="join_key",
        how="left",
        validate="many_to_one",
    )

    # fail fast if anything didn't attach
    unmatched = joined["lat"].isna().sum()
    if unmatched:
        bad = sorted(joined.loc[joined["lat"].isna(), "station_name"].unique())
        raise ValueError(f"{unmatched} ridership rows did not match a location. Examples: {bad[:20]}")

    # make GeoDataFrame (EPSG:4326)
    joined_gdf = gpd.GeoDataFrame(
        joined,
        geometry=gpd.points_from_xy(joined["lon"], joined["lat"]),
        crs="EPSG:4326",
    )

    ca = gpd.read_file(CA_GEO_PATH)
    if ca.crs is None:
        ca = ca.set_crs("EPSG:4326")
    ca = ca.to_crs(joined_gdf.crs)

    # spatial join: station point within community polygon
    station_with_ca = gpd.sjoin(
        joined_gdf,
        ca[["community_area", "community", "geometry"]],
        how="left",
        predicate="within",
    ).drop(columns=["index_right"])

    station_with_ca = station_with_ca[station_with_ca["community_area"].notna()].copy()
    station_with_ca["community_area"] = station_with_ca["community_area"].astype(int)

    missing_ca = station_with_ca["community_area"].isna().sum()
    if missing_ca:
        examples = station_with_ca.loc[station_with_ca["community_area"].isna(), "station_name"].drop_duplicates().head(20).tolist()
        raise ValueError(f"{missing_ca} rows missing community_area after spatial join. Examples: {examples}")

    # attach census metrics
    census = pd.read_csv(CA_CENSUS_PATH)
    station_with_ca["community_area"] = station_with_ca["community_area"].astype(int)
    census["community_area"] = pd.to_numeric(census["community_area"], errors="coerce").astype("Int64")

    final = station_with_ca.merge(
        census,
        on="community_area",
        how="left",
        validate="many_to_one",
    )

    OUT_PATH.parent.mkdir(parents=True, exist_ok=True)
    # write as CSV (geometry as WKT so it stays inspectable)
    final["geometry"] = final["geometry"].to_wkt()
    final.to_csv(OUT_PATH, index=False)

    print(f"Wrote {OUT_PATH}")
    print(f"Rows: {len(final)}")
    print(f"Stations (ridership station_id): {final['station_id'].nunique()}")
    print(f"Community areas: {final['community_area'].nunique()}")


def station_to_commarea_join(
    stations_gdf,  # GeoDataFrame points
    commareas_gdf, # GeoDataFrame polygons
):
    """
    Return a DataFrame with one row per station, with community_area added.
    Chicago-only: stations with no match are dropped.
    """
    # Build a plain list of (ca_id, polygon) to loop over
    ca_polys = []
    for _, row in commareas_gdf.iterrows():
        ca_polys.append((int(row["community_area"]), row["geometry"]))

    # For speed, prep polygons (optional but good)
    # from shapely.prepared import prep
    # ca_polys = [(ca_id, prep(poly)) for ca_id, poly in ca_polys]

    out_rows = []
    for _, s in stations_gdf.iterrows():
        pt = s["geometry"]  # already a Point
        matched = None

        for ca_id, poly in ca_polys:
            # if poly.contains(pt):  # contains excludes boundary
            if poly.covers(pt):      # covers includes boundary (safer)
                matched = ca_id
                break

        if matched is not None:
            out_rows.append(
                {
                    "join_key": s["join_key"],
                    "STATION_ID": int(s["STATION_ID"]),
                    "LONGNAME": s["LONGNAME"],
                    "LINES": s["LINES"],
                    "community_area": matched,
                    "geometry": s["geometry"],
                }
            )

    return out_rows

if __name__ == "__main__":
    main()