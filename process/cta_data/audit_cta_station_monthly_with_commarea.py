from pathlib import Path
import pandas as pd

from pathlib import Path

BASE_DIR = Path(__file__).resolve().parents[2]  # project root
IN_PATH = BASE_DIR / "data/processed/cta_station_monthly_2024_geo_commarea.csv"


def main() -> None:
    df = pd.read_csv(IN_PATH)

    print("\n--- BASIC SHAPE ---")
    print("Rows:", len(df))
    print("Columns:", len(df.columns))

    print("\n--- UNIQUE STATIONS ---")
    print("Unique station_id:", df["station_id"].nunique())
    print("Unique station_name:", df["station_name"].nunique())

    print("\n--- UNIQUE MONTHS ---")
    print("Unique year values:", df["year"].unique())
    print("Unique month count:", df["month"].nunique())
    print("Months present:", sorted(df["month"].unique()))

    print("\n--- COMMUNITY AREA CHECK ---")
    missing_ca = df["community_area"].isna().sum()
    print("Missing community_area rows:", missing_ca)

    print("\n--- DUPLICATE CHECK (station_id, year, month) ---")
    dup_count = (
        df.duplicated(subset=["station_id", "year", "month"])
        .sum()
    )
    print("Duplicate rows:", dup_count)

    print("\n--- TOTAL 2024 RIDERSHIP (ALL STATIONS) ---")
    print("Sum of month_total:", df["month_total"].sum())

    print("\nAudit complete.\n")
    
    dups = df[df.duplicated(subset=["station_id", "year", "month"], keep=False)]
    print("\nDuplicate rows detail:")
    print(dups.sort_values(["station_id", "month"]))

    # df = df.drop_duplicates(subset=["station_id", "year", "month"])

if __name__ == "__main__":
    main()