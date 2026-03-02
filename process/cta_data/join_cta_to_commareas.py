# import re
# from pathlib import Path
# from typing import Optional, Tuple

# import pandas as pd
# import geopandas as gpd


# RAW_DIR = Path("data/raw")
# PROCESSED_DIR = Path("data/processed")

# # Manual name fixes: ridership station_name -> shapefile LONGNAME
# # These are normalized by norm_name() before use.
# MANUAL_LONGNAME = {
#     "east 63rd-cottage grove": "cottage grove",
#     "medical center": "illinois medical district",
#     "roosevelt": "roosevelt/state",
#     "conservatory": "conservatory-central park",
# }

# # Ridership dataset encodes branch context as a suffix after '-'.
# # We use that suffix to disambiguate stations that share a base name.
# SUFFIX_TO_LINE = {
#     "forest park": "blue",
#     "cermak": "pink",
#     "brown": "brown",
#     "orange": "orange",
#     "lake": "green",
# }


# def norm_name(text: str) -> str:
#     """
#     Normalize station names for joining.

#     Input:
#         text: arbitrary station name text

#     Returns:
#         A lowercase, whitespace-normalized string with punctuation removed,
#         and '-' and '/' treated as separators.
#     """
#     if not isinstance(text, str):
#         return ""
#     s = text.lower().strip()
#     s = s.replace("&", "and")
#     s = re.sub(r"[^a-z0-9\s/\-]", "", s)  # keep / and - briefly
#     s = s.replace("/", " ")
#     s = s.replace("-", " ")
#     s = re.sub(r"\s+", " ", s).strip()
#     return s


# def split_station_variant(station_name: str) -> Tuple[str, Optional[str]]:
#     """
#     Split ridership station_name into a base name and an optional line hint.

#     Examples:
#         'Pulaski-Forest Park' -> ('Pulaski', 'blue')
#         'Damen-Lake'          -> ('Damen', 'green')
#         'Roosevelt'           -> ('Roosevelt', None)

#     Input:
#         station_name: ridership station_name value

#     Returns:
#         (base_name, line_hint) where line_hint is one of:
#         {'blue','pink','brown','orange','green'} or None.
#     """
#     if not isinstance(station_name, str):
#         return "", None

#     parts = station_name.strip().split("-")
#     if len(parts) >= 2:
#         suffix = parts[-1].strip().lower()
#         base = "-".join(parts[:-1]).strip()
#         line_hint = SUFFIX_TO_LINE.get(suffix)
#         if line_hint:
#             return base, line_hint

#     return station_name.strip(), None


# def load_station_monthly_ridership_2024() -> pd.DataFrame:
#     """
#     Load cleaned 2024 station-level monthly ridership totals.

#     Returns:
#         DataFrame with columns including:
#         station_id (ridership station identifier),
#         station_name,
#         year, month, month_total
#     """
#     path = PROCESSED_DIR / "cta_station_monthly_2024_clean.csv"
#     return pd.read_csv(path)


# def load_community_areas() -> gpd.GeoDataFrame:
#     """
#     Load Chicago community area polygons (your chicomm shapefile folder).

#     Returns:
#         GeoDataFrame with CHICOMNO, DISTNAME, geometry, and CRS EPSG:4269.
#     """
#     return gpd.read_file(RAW_DIR / "chicomm")


# def load_cta_station_points(target_crs) -> gpd.GeoDataFrame:
#     """
#     Load CTA station point shapefile and reproject to match target_crs.

#     Input:
#         target_crs: CRS of community areas (so spatial join is valid)

#     Returns:
#         GeoDataFrame with STATION_ID, LONGNAME, LINES, geometry in target_crs.
#     """
#     stations = gpd.read_file(RAW_DIR / "cta_stations")
#     return stations.to_crs(target_crs)


# def line_hint_matches(lines_text: str, line_hint: Optional[str]) -> bool:
#     """
#     Decide whether a station shapefile row is compatible with a ridership line hint.

#     Inputs:
#         lines_text: shapefile LINES field (string like 'Blue Line (Congress)')
#         line_hint: normalized hint like 'blue' or None

#     Returns:
#         True if line_hint is None (no restriction), else True only if hint appears in lines_text.
#     """
#     if line_hint is None:
#         return True
#     if lines_text is None or (isinstance(lines_text, float) and pd.isna(lines_text)):
#         return False
#     return str(line_hint).lower() in str(lines_text).lower()


# def build_station_crosswalk(
#     ridership_df: pd.DataFrame,
#     stations_gdf: gpd.GeoDataFrame,
# ) -> pd.DataFrame:
#     """
#     Build a crosswalk mapping ridership station_id -> shapefile STATION_ID.

#     Why needed:
#         Ridership uses station_id like 40900,
#         shapefile uses STATION_ID like 230,
#         so we match using station name + line context.

#     Inputs:
#         ridership_df: station monthly ridership (contains station_id, station_name)
#         stations_gdf: station points shapefile (contains STATION_ID, LONGNAME, LINES)

#     Returns:
#         DataFrame with columns:
#         station_id, station_name, STATION_ID, LONGNAME, LINES

#     Raises:
#         ValueError if any ridership stations cannot be mapped.
#     """
#     ridership_stations = ridership_df[["station_id", "station_name"]].drop_duplicates().copy()
#     ridership_stations["station_id"] = pd.to_numeric(ridership_stations["station_id"], errors="raise").astype(int)

#     # Parse base name + line hint from ridership naming conventions
#     base_names = []
#     line_hints = []
#     for name in ridership_stations["station_name"].tolist():
#         base, hint = split_station_variant(name)
#         base_names.append(base)
#         line_hints.append(hint)
#     ridership_stations["base_name"] = base_names
#     ridership_stations["line_hint"] = line_hints

#     ridership_stations["base_key"] = ridership_stations["base_name"].map(norm_name)

#     # Apply manual overrides (normalized)
#     manual_map = {norm_name(k): norm_name(v) for k, v in MANUAL_LONGNAME.items()}
#     ridership_stations["join_key"] = ridership_stations["base_key"].map(lambda k: manual_map.get(k, k))

#     # Prepare station shapefile keys
#     station_lookup = stations_gdf[["STATION_ID", "LONGNAME", "LINES"]].drop_duplicates().copy()
#     station_lookup["STATION_ID"] = pd.to_numeric(station_lookup["STATION_ID"], errors="raise").astype(int)
#     station_lookup["long_key"] = station_lookup["LONGNAME"].map(norm_name)
#     station_lookup["lines_norm"] = station_lookup["LINES"].astype(str).str.lower()

#     # Candidate join by name
#     candidates = ridership_stations.merge(
#         station_lookup,
#         left_on="join_key",
#         right_on="long_key",
#         how="left",
#     )

#     # Filter candidates using line hints when present
#     keep_flags = []
#     for _, row in candidates.iterrows():
#         keep_flags.append(line_hint_matches(row["lines_norm"], row["line_hint"]))
#     candidates["line_ok"] = keep_flags
#     candidates = candidates[candidates["line_ok"]].copy()

#     # Pick one shapefile station per ridership station_id
#     crosswalk = (
#         candidates.sort_values(["station_id"])
#         .drop_duplicates(subset=["station_id"])
#         [["station_id", "station_name", "STATION_ID", "LONGNAME", "LINES"]]
#     )

#     missing = crosswalk[crosswalk["STATION_ID"].isna()].copy()
#     if len(missing) > 0:
#         raise ValueError(
#             f"Crosswalk missing STATION_ID for {len(missing)} stations. "
#             f"Examples:\n{missing[['station_id','station_name']].head(20)}"
#         )

#     return crosswalk


# def attach_station_geometry_to_ridership(
#     ridership_df: pd.DataFrame,
#     crosswalk_df: pd.DataFrame,
#     stations_gdf: gpd.GeoDataFrame,
# ) -> gpd.GeoDataFrame:
#     """
#     Add station point geometry to each station-month ridership row.

#     Inputs:
#         ridership_df: station-month totals (station_id, year, month, month_total, station_name)
#         crosswalk_df: mapping station_id -> STATION_ID
#         stations_gdf: station points with STATION_ID + geometry

#     Returns:
#         GeoDataFrame of ridership rows with geometry attached.
#     """
#     ridership_df = ridership_df.copy()
#     ridership_df["station_id"] = pd.to_numeric(ridership_df["station_id"], errors="raise").astype(int)

#     crosswalk_df = crosswalk_df.copy()
#     crosswalk_df["station_id"] = pd.to_numeric(crosswalk_df["station_id"], errors="raise").astype(int)
#     crosswalk_df["STATION_ID"] = pd.to_numeric(crosswalk_df["STATION_ID"], errors="raise").astype(int)

#     ridership_with_station_id = ridership_df.merge(
#         crosswalk_df[["station_id", "STATION_ID"]],
#         on="station_id",
#         how="left",
#         validate="many_to_one",
#     )

#     missing = ridership_with_station_id[ridership_with_station_id["STATION_ID"].isna()][["station_id", "station_name"]].drop_duplicates()
#     if len(missing) > 0:
#         raise ValueError(f"{len(missing)} stations missing STATION_ID after crosswalk merge:\n{missing.head(30)}")

#     station_points = stations_gdf[["STATION_ID", "geometry"]].drop_duplicates().copy()
#     station_points["STATION_ID"] = pd.to_numeric(station_points["STATION_ID"], errors="raise").astype(int)

#     ridership_with_geometry = ridership_with_station_id.merge(
#         station_points,
#         on="STATION_ID",
#         how="left",
#         validate="many_to_one",
#     )

#     gdf = gpd.GeoDataFrame(ridership_with_geometry, geometry="geometry", crs=stations_gdf.crs)
#     if gdf["geometry"].isna().any():
#         bad = gdf[gdf["geometry"].isna()][["station_id", "station_name", "STATION_ID"]].drop_duplicates().head(30)
#         raise ValueError(f"Some ridership rows did not get station geometry. Examples:\n{bad}")

#     return gdf


# def spatial_join_stations_to_commareas(
#     station_ridership_gdf: gpd.GeoDataFrame,
#     commareas_gdf: gpd.GeoDataFrame,
# ) -> gpd.GeoDataFrame:
#     """
#     Spatially assign each station point to a community area polygon.

#     Inputs:
#         station_ridership_gdf: station-month ridership rows with point geometry
#         commareas_gdf: community area polygons (CHICOMNO, DISTNAME, geometry)

#     Returns:
#         GeoDataFrame where each station-month row has CHICOMNO and DISTNAME.
#     """
#     comm_small = commareas_gdf[["CHICOMNO", "DISTNAME", "geometry"]].copy()

#     joined = gpd.sjoin(
#         station_ridership_gdf,
#         comm_small,
#         how="left",
#         predicate="within",
#     )

#     if joined["CHICOMNO"].isna().any():
#         bad = joined[joined["CHICOMNO"].isna()][["station_id", "station_name"]].drop_duplicates().head(20)
#         raise ValueError(f"Some stations did not join to a community area. Examples:\n{bad}")

#     return joined


# def aggregate_commarea_monthly_ridership(joined_gdf: gpd.GeoDataFrame) -> pd.DataFrame:
#     """
#     Aggregate station-month entries to community-area-month totals.

#     Input:
#         joined_gdf: station-month rows with CHICOMNO, DISTNAME

#     Returns:
#         DataFrame with:
#         CHICOMNO, DISTNAME, year, month, comm_area_total_entries
#     """
#     return (
#         joined_gdf.groupby(["CHICOMNO", "DISTNAME", "year", "month"], as_index=False)["month_total"]
#         .sum()
#         .rename(columns={"month_total": "comm_area_total_entries"})
#     )


# def main() -> None:
#     """
#     End-to-end pipeline for CTA station ridership -> community area monthly totals.

#     Writes:
#         data/processed/cta_station_crosswalk_2024.csv
#         data/processed/cta_commarea_monthly_2024_clean.csv
#     """
#     PROCESSED_DIR.mkdir(parents=True, exist_ok=True)

#     ridership_df = load_station_monthly_ridership_2024()
#     commareas_gdf = load_community_areas()
#     stations_gdf = load_cta_station_points(commareas_gdf.crs)

#     crosswalk_df = build_station_crosswalk(ridership_df, stations_gdf)
#     crosswalk_df.to_csv(PROCESSED_DIR / "cta_station_crosswalk_2024.csv", index=False)

#     station_ridership_gdf = attach_station_geometry_to_ridership(ridership_df, crosswalk_df, stations_gdf)
#     joined_gdf = spatial_join_stations_to_commareas(station_ridership_gdf, commareas_gdf)

#     commarea_monthly_df = aggregate_commarea_monthly_ridership(joined_gdf)
#     commarea_monthly_df.to_csv(PROCESSED_DIR / "cta_commarea_monthly_2024_clean.csv", index=False)

#     print("Wrote:")
#     print(" - data/processed/cta_station_crosswalk_2024.csv")
#     print(" - data/processed/cta_commarea_monthly_2024_clean.csv")


# if __name__ == "__main__":
#     main()