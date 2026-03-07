import pandas as pd


INPUT_PATH = "data/processed/cta_station_monthly_2024_geo_commarea.csv"
OUTPUT_PATH = "data/processed/cta_station_points_2024.csv"


def read_station_monthly_with_commarea():
    """
    Read the station-monthly ridership file with station coordinates
    and community area information already attached.
    """
    return pd.read_csv(INPUT_PATH)


def keep_2024_rows(station_monthly):
    """
    Keep only 2024 rows.
    """
    return station_monthly[station_monthly["year"] == 2024].copy()


def make_station_points(station_monthly):
    """
    Collapse monthly station rows into one annual row per station.
    """
    station_points = (
        station_monthly.groupby(
            [
                "station_id",
                "station_name",
                "LINES",
                "lat",
                "lon",
                "community_area",
                "community",
            ],
            as_index=False,
        )["month_total"]
        .sum()
        .rename(
            columns={
                "LINES": "line_name",
                "month_total": "ridership_2024_total",
            }
        )
    )

    station_points = station_points[
        [
            "station_id",
            "station_name",
            "lat",
            "lon",
            "ridership_2024_total",
            "line_name",
            "community_area",
            "community",
        ]
    ].copy()

    station_points = station_points.sort_values(
        by=["ridership_2024_total", "station_name"],
        ascending=[False, True],
    )

    return station_points


def main():
    """
    Build one row per CTA station with annual 2024 ridership
    and station point coordinates.
    """
    station_monthly = read_station_monthly_with_commarea()
    station_2024 = keep_2024_rows(station_monthly)
    station_points = make_station_points(station_2024)

    station_points.to_csv(OUTPUT_PATH, index=False)

    print(f"Wrote {OUTPUT_PATH}")
    print(station_points.head())
    print(f"Rows: {len(station_points)}")


if __name__ == "__main__":
    main()