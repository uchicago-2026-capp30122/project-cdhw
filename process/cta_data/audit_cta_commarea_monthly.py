from pathlib import Path
import polars as pl

PROCESSED_DIR = Path("data/processed")
IN_PATH = PROCESSED_DIR / "cta_commarea_monthly_2024.csv"


def main() -> None:
    df = pl.read_csv(IN_PATH)

    print("\n--- BASIC SHAPE ---")
    print("Rows:", df.height)
    print("Columns:", df.width)

    print("\n--- UNIQUE COMMUNITY AREAS ---")
    print("Unique community_area:", df["community_area"].n_unique())
    print("Unique community:", df["community"].n_unique())

    print("\n--- UNIQUE MONTHS ---")
    years = df["year"].unique().sort()
    months = df["month"].unique().sort()
    print("Years:", years.to_list())
    print("Month count:", months.len())
    print("Months:", months.to_list())

    print("\n--- MISSING CHECKS ---")
    print("Missing community_area:", df.select(pl.col("community_area").is_null().sum()).item())
    print("Missing cta_month_total:", df.select(pl.col("cta_month_total").is_null().sum()).item())

    print("\n--- DUPLICATE CHECK (community_area, year, month) ---")
    dups = (
        df.group_by(["community_area", "year", "month"])
        .len()
        .filter(pl.col("len") > 1)
    )
    print("Duplicate groups:", dups.height)

    print("\n--- TOTAL 2024 CTA RIDERSHIP (COMMUNITY AREA AGG) ---")
    total = df.select(pl.col("cta_month_total").sum()).item()
    print("Sum cta_month_total:", total)


if __name__ == "__main__":
    main()