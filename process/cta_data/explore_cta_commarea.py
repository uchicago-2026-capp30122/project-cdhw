from pathlib import Path
import polars as pl

IN_PATH = Path("data/processed/cta_commarea_monthly_2024.csv")
OUT_DIR = Path("data/processed/cta_explore")
OUT_DIR.mkdir(parents=True, exist_ok=True)

def main() -> None:
    df = pl.read_csv(IN_PATH)

    # Annual totals per community area (tidy: one row per CA)
    ca_annual = (
        df.group_by(["community_area", "community"])
          .agg(pl.col("cta_month_total").sum().alias("cta_2024_total"))
          .sort("cta_2024_total", descending=True)
    )
    ca_annual.write_csv(OUT_DIR / "cta_commarea_annual_2024.csv")

    # Top 10 / bottom 10
    ca_annual.head(10).write_csv(OUT_DIR / "cta_commarea_top10_2024.csv")
    ca_annual.tail(10).write_csv(OUT_DIR / "cta_commarea_bottom10_2024.csv")

    # Citywide monthly totals (one row per month)
    city_monthly = (
        df.group_by(["year", "month"])
          .agg(pl.col("cta_month_total").sum().alias("cta_city_total"))
          .sort(["year", "month"])
    )
    city_monthly.write_csv(OUT_DIR / "cta_citywide_monthly_2024.csv")

    print("Wrote:")
    print(" -", OUT_DIR / "cta_commarea_annual_2024.csv")
    print(" -", OUT_DIR / "cta_commarea_top10_2024.csv")
    print(" -", OUT_DIR / "cta_commarea_bottom10_2024.csv")
    print(" -", OUT_DIR / "cta_citywide_monthly_2024.csv")

if __name__ == "__main__":
    main()