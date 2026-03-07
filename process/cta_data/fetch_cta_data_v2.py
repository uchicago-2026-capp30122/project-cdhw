from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
from typing import Iterable, Optional

import pandas as pd

# If geopandas isn't installed, you'll need to add it or run this in your project env.
import geopandas as gpd

# Optional: nicer JW matching if available
try:
    import jellyfish  # type: ignore

    def jw(a: str, b: str) -> float:
        return float(jellyfish.jaro_winkler_similarity(a, b))
except Exception:
    from difflib import SequenceMatcher

    def jw(a: str, b: str) -> float:
        return float(SequenceMatcher(None, a, b).ratio())


RAW_DIR = Path("data/raw")
PROCESSED_DIR = Path("data/processed")
PROCESSED_DIR.mkdir(parents=True, exist_ok=True)

STATIONS_SHP_PATH = RAW_DIR / "cta_stations" / "CTA_RailStations.shp"


RIDERSHIP_RAW_CSV = RAW_DIR / "cta_L_station_entries_monthly_daytype.csv"


RIDERSHIP_VIEW_ID = None  


LINE_COLORS = ("Red", "Blue", "Brown", "Green", "Orange", "Pink", "Purple", "Yellow")


def normalize_text(s: str) -> str:
    """
    Normalize station names into a matching key.
    Keep it simple and predictable.
    """
    if pd.isna(s):
        return ""
    s = str(s).strip().lower()
    s = s.replace("&", "and")
    # unify separators
    s = s.replace("/", " ")
    s = s.replace("-", " ")
    # collapse whitespace
    s = " ".join(s.split())
    return s


def parse_line_colors_from_lines_field(lines: str) -> set[str]:
    """
    Shapefile LINES field often looks like: 'Green Line (Lake)'
    or 'Blue Line' etc. Return set of colors.
    """
    out: set[str] = set()
    if pd.isna(lines):
        return out
    s = str(lines)
    for color in LINE_COLORS:
        if f"{color} Line" in s:
            out.add(color)
    return out


def infer_line_hint_from_ridership_name(station_name: str) -> Optional[str]:
    """
    Use hyphen suffix (branch tag) to infer intended CTA line color.
    This is the key improvement vs “just string similarity”.

    Examples:
      Austin-Forest Park -> Blue
      Austin-Lake -> Green
      Sox-35th-Dan Ryan -> Red
    """
    if pd.isna(station_name):
        return None
    name = str(station_name).strip()


    parts = [p.strip() for p in name.split("-") if p.strip()]
    if len(parts) >= 2:
        suffix = parts[-1].lower()

        if suffix in {"forest park", "o'hare"}:
            return "Blue"
        if suffix in {"lake"}:
            return "Green"
        if suffix in {"dan ryan"}:
            return "Red"
        if suffix in {"cermak"}:

            return "Pink"
        if suffix in {"midway"}:
            return "Orange"

    return None


@dataclass(frozen=True)
class StationIndexRow:
    station_id: int
    longname: str
    lines: str
    line_colors: set[str]
    name_key: str


def load_station_shapefile_index(shp_path: Path) -> gpd.GeoDataFrame:
    """
    Reads the shapefile and builds an index table with line color sets and name keys.
    """
    gdf = gpd.read_file(shp_path)

    for col in ["STATION_ID", "LONGNAME", "LINES"]:
        if col not in gdf.columns:
            raise ValueError(f"Shapefile missing expected column: {col}")

    gdf = gdf.copy()
    gdf["line_colors"] = gdf["LINES"].apply(parse_line_colors_from_lines_field)
    gdf["name_key"] = gdf["LONGNAME"].apply(normalize_text)

    keep_cols = ["STATION_ID", "LONGNAME", "LINES", "line_colors", "name_key", "geometry"]
    return gdf[keep_cols]


def fetch_socrata_csv(view_id: str, limit: int = 50000) -> pd.DataFrame:
    """
    Simple Socrata CSV fetch (no auth). Use only if you set RIDERSHIP_VIEW_ID.
    """
    import urllib.request

    url = f"https://data.cityofchicago.org/resource/{view_id}.csv?$limit={limit}"
    with urllib.request.urlopen(url) as resp:
        df = pd.read_csv(resp)
    return df


def load_ridership_daytype() -> pd.DataFrame:
    """
    Load the CTA monthly day-type averages & totals dataset.

    Expected columns (per portal):
      station_id, stationame, month_beginning,
      avg_weekday_rides, avg_saturday_rides, avg_sunday_holiday_rides, monthtotal
    """
    if RIDERSHIP_RAW_CSV.exists():
        df = pd.read_csv(RIDERSHIP_RAW_CSV)
        return df

    if RIDERSHIP_VIEW_ID:
        return fetch_socrata_csv(RIDERSHIP_VIEW_ID)

    raise FileNotFoundError(
        "Ridership dataset not found. Either:\n"
        f"  - place CSV at {RIDERSHIP_RAW_CSV}\n"
        "  - or set RIDERSHIP_VIEW_ID to fetch from Socrata."
    )

#CLEAN RIDERSHIP

def clean_ridership_monthly_2024(df: pd.DataFrame) -> pd.DataFrame:
    """
    Convert month_beginning to year/month and keep 2024 totals.
    """
    required = {"station_id", "stationame", "month_beginning", "monthtotal"}
    missing = required - set(df.columns)
    if missing:
        raise ValueError(f"Ridership df missing columns: {sorted(missing)}")

    out = df.copy()

#PARSING

    mb = out["month_beginning"]
    if pd.api.types.is_numeric_dtype(mb):
        out["month_beginning_dt"] = pd.to_datetime(mb, unit="ms", errors="coerce")
    else:
        out["month_beginning_dt"] = pd.to_datetime(mb, errors="coerce")

    out["year"] = out["month_beginning_dt"].dt.year
    out["month"] = out["month_beginning_dt"].dt.month

    out = out[out["year"] == 2024].copy()

    # Standardizing names with hints
    out["station_name"] = out["stationame"].astype(str)
    out["name_key"] = out["station_name"].apply(normalize_text)
    out["line_hint"] = out["station_name"].apply(infer_line_hint_from_ridership_name)


    out = out.rename(columns={"monthtotal": "month_total"})
    cols = ["station_id", "station_name", "name_key", "line_hint", "year", "month", "month_total"]
    out = out[cols]

    # DUPLICATES HANDLE
    out = (
        out.groupby(["station_id", "station_name", "name_key", "line_hint", "year", "month"], as_index=False)
        .agg({"month_total": "sum"})
    )

    return out

##MATCHING Handling all candidates

def station_candidates_for_one(
    ridership_station_id: int,
    ridership_station_name: str,
    ridership_key: str,
    line_hint: Optional[str],
    stations_gdf: gpd.GeoDataFrame,
) -> pd.DataFrame:
    """
    Generate candidates for one ridership station.
    If line_hint exists, filter shapefile stations to those containing that line.
    """
    cand = stations_gdf

    if line_hint:
        cand = cand[cand["line_colors"].apply(lambda s: line_hint in s)].copy()

    # EDGE CASE
    if cand.empty:
        cand = stations_gdf.copy()

    cand = cand.assign(
        station_id=ridership_station_id,
        station_name=ridership_station_name,
        score=cand["name_key"].apply(lambda x: jw(ridership_key, x)),
    )

    # Keep match columns
    keep = ["station_id", "station_name", "line_hint", "score", "STATION_ID", "LONGNAME", "LINES"]
    cand = cand.rename(columns={"STATION_ID": "STATION_ID", "LONGNAME": "LONGNAME", "LINES": "LINES"})
    cand["line_hint"] = line_hint
    return cand[keep].sort_values("score", ascending=False)


def build_candidates(
    ridership_stations: pd.DataFrame,
    stations_gdf: gpd.GeoDataFrame,
    top_k: int = 8,
) -> pd.DataFrame:
    """
    Build candidate pairs for each unique ridership station_id.
    """
    uniq = ridership_stations[["station_id", "station_name", "name_key", "line_hint"]].drop_duplicates()

    all_rows: list[pd.DataFrame] = []
    for row in uniq.itertuples(index=False):
        c = station_candidates_for_one(
            ridership_station_id=int(row.station_id),
            ridership_station_name=str(row.station_name),
            ridership_key=str(row.name_key),
            line_hint=(None if pd.isna(row.line_hint) else row.line_hint),
            stations_gdf=stations_gdf,
        )
        all_rows.append(c.head(top_k))

    return pd.concat(all_rows, ignore_index=True)


def make_manual_review(cand: pd.DataFrame, top_k: int = 5) -> pd.DataFrame:
    """
    Manual review file WITHOUT the misleading gap/auto-pick logic.
    Adds:
      - rank
      - passes_line_hint (if line_hint exists, does candidate include that line?)
    """
    out = cand.copy()
    out = out.sort_values(["station_id", "score"], ascending=[True, False])
    out = out.groupby("station_id", as_index=False).head(top_k).copy()

    out["rank"] = out.groupby("station_id").cumcount() + 1

    def passes_line(row) -> bool:
        if not row["line_hint"] or pd.isna(row["line_hint"]):
            return True
        return f"{row['line_hint']} Line" in str(row["LINES"])

    out["passes_line_hint"] = out.apply(passes_line, axis=1)

    out["keep"] = ""          
    out["review_notes"] = "" 

    cols = [
        "station_id", "station_name", "line_hint",
        "rank", "score",
        "STATION_ID", "LONGNAME", "LINES",
        "passes_line_hint",
        "keep", "review_notes",
    ]
    return out[cols]


def main() -> None:
    stations_gdf = load_station_shapefile_index(STATIONS_SHP_PATH)

    stations_out = PROCESSED_DIR / "cta_station_index_from_shapefile.csv"
    # Save geometry as WKT so it's easy to join later without geopandas
    stations_gdf_out = stations_gdf.copy()
    stations_gdf_out["geometry_wkt"] = stations_gdf_out.geometry.to_wkt()
    stations_gdf_out.drop(columns=["geometry"]).to_csv(stations_out, index=False)

    # 2) ridership day-type dataset -> clean 2024 totals
    rid_raw = load_ridership_daytype()
    rid_2024 = clean_ridership_monthly_2024(rid_raw)

    rid_out = PROCESSED_DIR / "cta_ridership_monthly_2024_clean.csv"
    rid_2024.to_csv(rid_out, index=False)

    # 3) candidates + manual review
    cand = build_candidates(rid_2024, stations_gdf, top_k=8)
    cand_out = PROCESSED_DIR / "cta_station_match_candidates_2024_v2.csv"
    cand.to_csv(cand_out, index=False)

    review = make_manual_review(cand, top_k=5)
    review_out = PROCESSED_DIR / "cta_station_manual_review_2024_v2.csv"
    review.to_csv(review_out, index=False)

    print(f"Wrote: {stations_out}")
    print(f"Wrote: {rid_out}")
    print(f"Wrote: {cand_out}")
    print(f"Wrote: {review_out}")
    print(f"Unique ridership stations (2024): {rid_2024['station_id'].nunique()}")
    print(f"Manual review rows: {len(review)}")


if __name__ == "__main__":
    main()