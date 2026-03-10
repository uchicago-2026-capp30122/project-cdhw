"""
This script builds the csv "data/processed/ca_trip_totals.csv"
which contains community-area level rideshare trip totals.
"""

from pathlib import Path
import pandas as pd


def main():
    root = Path(__file__).resolve().parents[2]
    in_path = root / "data" / "processed" / "rideshare_community_areas.json"
    out_path = root / "data" / "processed" / "ca_trip_totals.csv"

    df = pd.read_json(in_path)
    df["trips"] = pd.to_numeric(df["trips"], errors="coerce").fillna(0)

    pickup_totals = (
        df.groupby("pickup_community_area", as_index=False)["trips"]
        .sum()
        .rename(columns={"pickup_community_area": "community_area"})
    )

    dropoff_totals = (
        df.groupby("dropoff_community_area", as_index=False)["trips"]
        .sum()
        .rename(columns={"dropoff_community_area": "community_area"})
    )

    ca_totals = pd.concat([pickup_totals, dropoff_totals], ignore_index=True)
    ca_totals["community_area"] = pd.to_numeric(
        ca_totals["community_area"], errors="coerce"
    )
    ca_totals = (
        ca_totals.groupby("community_area", as_index=False)["trips"]
        .sum()
        .rename(columns={"trips": "total_trips"})
        .sort_values("community_area")
    )

    ca_totals.to_csv(out_path, index=False)
    print(f"Wrote {len(ca_totals)} rows -> {out_path}")


if __name__ == "__main__":
    main()
