from pathlib import Path
import pandas as pd

PROCESSED_DIR = Path("data/processed")

CAND_PATH = PROCESSED_DIR / "cta_station_match_candidates_2024.csv"
OUT_REVIEW_PATH = PROCESSED_DIR / "cta_station_manual_review_2024.csv"


def main() -> None:
    cand = pd.read_csv(CAND_PATH)

    # Keep only top K candidates per ridership station (so review is small)
    TOP_K = 5
    cand = cand.sort_values(["station_id", "score"], ascending=[True, False])
    cand_top = cand.groupby("station_id", as_index=False).head(TOP_K).copy()

    # Add ranking + helpful “gap” metric (top1 vs top2) to auto-flag easy matches
    cand_top["rank"] = cand_top.groupby("station_id").cumcount() + 1

    # compute gap between best and second-best within each station_id
    best = cand_top[cand_top["rank"] == 1][["station_id", "score"]].rename(columns={"score": "best_score"})
    second = cand_top[cand_top["rank"] == 2][["station_id", "score"]].rename(columns={"score": "second_score"})
    gaps = best.merge(second, on="station_id", how="left")
    gaps["gap"] = gaps["best_score"] - gaps["second_score"].fillna(0)

    cand_top = cand_top.merge(gaps[["station_id", "best_score", "second_score", "gap"]], on="station_id", how="left")

    # auto_pick suggestion: strong best score + clear separation from runner-up
    cand_top["auto_pick_suggested"] = (cand_top["rank"] == 1) & (cand_top["best_score"] >= 0.90) & (cand_top["gap"] >= 0.05)

    # Manual review columns to edit
    cand_top["keep"] = ""          # I fill: y/n (only one 'y' per station_id)
    cand_top["review_notes"] = ""  # I fill optionally

    cols = [
        "station_id", "station_name",
        "rank", "score",
        "STATION_ID", "LONGNAME", "LINES",
        "best_score", "second_score", "gap",
        "auto_pick_suggested",
        "keep", "review_notes",
    ]

    cand_top[cols].to_csv(OUT_REVIEW_PATH, index=False)

    # quick stats
    total_stations = cand["station_id"].nunique()
    review_rows = len(cand_top)
    auto = cand_top["auto_pick_suggested"].sum()

    print(f"Wrote: {OUT_REVIEW_PATH}")
    print(f"Ridership stations: {total_stations}")
    print(f"Review rows (top {TOP_K} each): {review_rows}")
    print(f"Stations with auto-pick suggestion (rank=1): {auto}")


if __name__ == "__main__":
    main()