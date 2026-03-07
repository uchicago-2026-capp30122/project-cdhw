import pandas as pd


STATION_MONTHLY_PATH = "data/processed/cta_station_monthly_2024_clean.csv"
STATION_LOCATIONS_PATH = "data/processed/cta_station_locations_rail_clean.csv"
OUTPUT_PATH = "data/processed/cta_station_points_2024.csv"


def read_station_monthly():
    """
    Read station monthly ridership data.
    """
    return pd.read_csv(STATION_MONTHLY_PATH)


def read_station_locations():
    """
    Read station location data.
    """
    return pd.read_csv(STATION_LOCATIONS_PATH)


def make_station_annual_totals(station_monthly):
    """
    Sum monthly ridership into annual 2024 ridership for each station.
    """
    station_2024 = station_monthly[station_monthly["year"] == 2024].copy()

    annual_totals = (
        station_2024.groupby("station_id", as_index=False)["month_total"]
        .sum()
        .rename(columns={"month_total": "ridership_2024_total"})
    )

    return annual_totals


def clean_station_locations(station_locations):
    """
    Keep only the columns needed for the station points output
    and rename them clearly.
    """
    station_points = station_locations[
        ["STATION_ID", "LONGNAME", "LINES", "lat", "lon"]
    ].copy()

    station_points = station_points.rename(
        columns={
            "STATION_ID": "station_id",
            "LONGNAME": "station_name",
            "LINES": "line_name",
        }
    )

    return station_points


def build_station_points(station_locations, station_annual_totals):
    """
    Merge station locations with annual station ridership.
    """
    station_points = clean_station_locations(station_locations)

    merged = station_points.merge(
        station_annual_totals,
        on="station_id",
        how="left",
    )

    merged = merged[
        [
            "station_id",
            "station_name",
            "lat",
            "lon",
            "ridership_2024_total",
            "line_name",
        ]
    ].copy()

    merged = merged.sort_values(
        by=["ridership_2024_total", "station_name"],
        ascending=[False, True],
    )

    return merged


def main():
    """
    Build one row per CTA station with coordinates and annual 2024 ridership.
    """
    station_monthly = read_station_monthly()
    station_locations = read_station_locations()

    station_annual_totals = make_station_annual_totals(station_monthly)
    station_points = build_station_points(
        station_locations,
        station_annual_totals,
    )

    station_points.to_csv(OUTPUT_PATH, index=False)

    print(f"Wrote {OUTPUT_PATH}")
    print(station_points.head())
    print(f"Rows: {len(station_points)}")


if __name__ == "__main__":
    main()