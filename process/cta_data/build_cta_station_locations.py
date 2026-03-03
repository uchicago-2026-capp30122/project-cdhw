from pathlib import Path
import geopandas as gpd
import pandas as pd


RAW_SHP = Path("data/raw/cta_stations/CTA_RailStations.shp")
OUT_PATH = Path("data/processed/cta_station_locations_rail_clean.csv")


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

    # If the entire name is a suffix phrase (e.g., "forest park"), do NOT drop it.
    # We only drop suffixes when there is something BEFORE the suffix.
    if len(parts) >= 3 and " ".join(parts[-2:]) in BRANCH_SUFFIXES:
        return " ".join(parts[:-2])
    if len(parts) >= 2 and parts[-1] in BRANCH_SUFFIXES:
        return " ".join(parts[:-1])
    return " ".join(parts)


def combine_lines(series: pd.Series) -> str:
    vals = []
    for x in series.dropna().astype(str):
        parts = [p.strip() for p in x.replace(";", ",").split(",")]
        vals.extend([p for p in parts if p])
    return ", ".join(sorted(set(vals)))


def main() -> None:
    gdf = gpd.read_file(RAW_SHP)

    # convert to lat/lon
    gdf = gdf.to_crs("EPSG:4326")
    gdf["lon"] = gdf.geometry.x
    gdf["lat"] = gdf.geometry.y

    # create join_key
    gdf["join_key"] = gdf["LONGNAME"].apply(drop_branch_suffix)

    # collapse to one station location
    loc = (
        gdf.groupby("join_key", as_index=False)
        .agg({
            "STATION_ID": "min",
            "LONGNAME": "first",
            "LINES": combine_lines,
            "lat": "mean",
            "lon": "mean",
        })
    )

    OUT_PATH.parent.mkdir(parents=True, exist_ok=True)
    loc.to_csv(OUT_PATH, index=False)

    print(f"Wrote {OUT_PATH}")
    print(f"Unique station locations: {len(loc)}")


if __name__ == "__main__":
    main()