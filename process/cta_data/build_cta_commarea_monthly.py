from pathlib import Path
import polars as pl

PROCESSED_DIR = Path("data/processed")

IN_PATH = PROCESSED_DIR / "cta_station_monthly_2024_geo_commarea.csv"
OUT_PATH = PROCESSED_DIR / "cta_commarea_monthly_2024.csv"


def _ensure_out_dir() -> None:
    PROCESSED_DIR.mkdir(parents=True, exist_ok=True)


def load_base_table() -> pl.LazyFrame:
    return pl.scan_csv(IN_PATH)


def build_commarea_monthly(base: pl.LazyFrame) -> pl.DataFrame:
    # Keep only what we need and standardize types
    cleaned = (
        base.select(
            [
                pl.col("community_area").cast(pl.Int64),
                pl.col("community").cast(pl.Utf8),
                pl.col("year").cast(pl.Int64),
                pl.col("month").cast(pl.Int64),
                pl.col("month_total").cast(pl.Int64),
            ]
        )
        # safety: keep 2024 only
        .filter(pl.col("year") == 2024)
    )

    # Aggregate: community area x month
    out = (
        cleaned.group_by(["community_area", "community", "year", "month"])
        .agg(pl.col("month_total").sum().alias("cta_month_total"))
        .sort(["community_area", "year", "month"])
        .collect()
    )
    return out


def main() -> None:
    _ensure_out_dir()

    base = load_base_table()
    out = build_commarea_monthly(base)

    out.write_csv(OUT_PATH)
    print(f"Wrote {OUT_PATH} ({out.height} rows, {out['community_area'].n_unique()} community areas)")


if __name__ == "__main__":
    main()