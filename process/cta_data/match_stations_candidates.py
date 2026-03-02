import re
from pathlib import Path

import pandas as pd
import geopandas as gpd

RAW_DIR = Path("data/raw")
PROCESSED_DIR = Path("data/processed")


def norm_name(text: str) -> str:
    """
    Normalize station names for string similarity.

    Returns:
        lowercase string with punctuation removed and separators normalized.
    """
    if not isinstance(text, str):
        return ""
    s = text.lower().strip()
    s = s.replace("&", "and")
    s = re.sub(r"[^a-z0-9\s]", " ", s)
    s = re.sub(r"\s+", " ", s).strip()
    return s


def jw_similarity(a: str, b: str) -> float:
    """
    Jaro-Winkler similarity in [0,1].
    Uses jellyfish if available; falls back to rapidfuzz ratio scaled to [0,1].
    """
    a = a or ""
    b = b or ""
    try:
        import jellyfish  # type: ignore

        return float(jellyfish.jaro_winkler_similarity(a, b))
    except ModuleNotFoundError:
        from rapidfuzz import fuzz  # type: ignore

        return float(fuzz.WRatio(a, b)) / 100.0


def load_ridership_stations() -> pd.DataFrame:
    """
    Load unique ridership stations from cleaned monthly dataset.

    Returns:
        DataFrame with station_id (ridership), station_name, name_key
    """
    rid = pd.read_csv(PROCESSED_DIR / "cta_station_monthly_2024_clean.csv")
    rid_st = rid[["station_id", "station_name"]].drop_duplicates().copy()
    rid_st["station_id"] = pd.to_numeric(rid_st["station_id"], errors="raise").astype(int)
    rid_st["name_key"] = rid_st["station_name"].map(norm_name)
    return rid_st


def load_shape_stations() -> pd.DataFrame:
    """
    Load unique shapefile stations.

    Returns:
        DataFrame with STATION_ID (shapefile), LONGNAME, LINES, long_key
    """
    gdf = gpd.read_file(RAW_DIR / "cta_stations")
    st = gdf[["STATION_ID", "LONGNAME", "LINES"]].drop_duplicates().copy()
    st["STATION_ID"] = pd.to_numeric(st["STATION_ID"], errors="raise").astype(int)
    st["long_key"] = st["LONGNAME"].map(norm_name)
    return st


def make_candidates(threshold: float = 0.70) -> pd.DataFrame:
    """
    Compute candidate matches between ridership station_name and shapefile LONGNAME.

    Strategy:
        For each ridership station, score against ALL shapefile stations,
        keep those with similarity >= threshold, then rank.

    Returns:
        Long candidate table (one ridership station can have multiple candidates)
        with columns:
            station_id, station_name, STATION_ID, LONGNAME, LINES, score
    """
    rid = load_ridership_stations()
    shp = load_shape_stations()

    rows = []
    for _, r in rid.iterrows():
        rk = r["name_key"]
        for _, s in shp.iterrows():
            sk = s["long_key"]
            score = jw_similarity(rk, sk)
            if score >= threshold:
                rows.append(
                    {
                        "station_id": int(r["station_id"]),
                        "station_name": r["station_name"],
                        "STATION_ID": int(s["STATION_ID"]),
                        "LONGNAME": s["LONGNAME"],
                        "LINES": s["LINES"],
                        "score": float(score),
                    }
                )

    cand = pd.DataFrame(rows)
    if len(cand) == 0:
        return cand

    cand = cand.sort_values(["station_id", "score"], ascending=[True, False])
    return cand


def main() -> None:
    PROCESSED_DIR.mkdir(parents=True, exist_ok=True)

    threshold = 0.70
    cand = make_candidates(threshold=threshold)

    out_path = PROCESSED_DIR / "cta_station_match_candidates_2024.csv"
    cand.to_csv(out_path, index=False)

    print(f"Wrote candidates: {out_path}")
    if len(cand) == 0:
        print("No candidates found. Threshold too high or normalization mismatch.")
        return

    # quick summary: how many ridership stations have at least 1 candidate?
    covered = cand["station_id"].nunique()
    total = pd.read_csv(PROCESSED_DIR / "cta_station_monthly_2024_clean.csv")[["station_id"]].drop_duplicates().shape[0]
    print(f"Ridership stations covered by >= {threshold:.2f}: {covered}/{total}")

    # show top 3 candidates for first few stations
    print("\nSample (top 3 per station for first 5 stations):")
    sample = (
        cand.groupby("station_id", as_index=False)
        .head(3)
        .groupby("station_id", as_index=False)
        .head(3)
    )
    print(sample.head(15))


if __name__ == "__main__":
    main()