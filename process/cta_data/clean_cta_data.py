from pathlib import Path

import pandas as pd


RAW_DIR = Path("data/raw")
OUT_DIR = Path("data/processed")


def _ensure_dirs() -> None:
    OUT_DIR.mkdir(parents=True, exist_ok=True)


def load_station_monthly_raw() -> pd.DataFrame:
    """
    Load raw CTA station monthly data (2024).

    Returns:
        DataFrame with columns:
            station_id (int)
            stationame (str)
            month_beginning (datetime64)
            monthtotal (int)
    """
    path = RAW_DIR / "cta_station_monthly_2024_raw.csv"
    df = pd.read_csv(path)

    df["station_id"] = df["station_id"].astype(int)
    df["stationame"] = df["stationame"].astype(str)
    df["month_beginning"] = pd.to_datetime(df["month_beginning"], errors="coerce")
    df["monthtotal"] = (
        pd.to_numeric(df["monthtotal"], errors="coerce").fillna(0).astype(int)
    )
    return df


def build_station_monthly_clean(df: pd.DataFrame) -> pd.DataFrame:
    """
    Add clean month fields and keep only needed columns.

    Returns:
        DataFrame with columns:
            station_id, station_name, year, month, month_total
    """
    df = df.copy()

    df["year"] = df["month_beginning"].dt.year.astype(int)
    df["month"] = df["month_beginning"].dt.month.astype(int)

    out = df.rename(
        columns={
            "stationame": "station_name",
            "monthtotal": "month_total",
        }
    )[["station_id", "station_name", "year", "month", "month_total"]]

    # Safety: restrict to 2024 only
    out = out[out["year"] == 2024].reset_index(drop=True)
    return out


def load_systemwide_daily_raw() -> pd.DataFrame:
    """
    Load raw CTA systemwide daily ridership (2024).

    Returns:
        DataFrame with columns:
            service_date (datetime64)
            bus (int)
            rail_boardings (int)
            total_rides (int)
    """
    path = RAW_DIR / "cta_systemwide_daily_2024_raw.csv"
    df = pd.read_csv(path)

    df["service_date"] = pd.to_datetime(df["service_date"], errors="coerce")
    df["bus"] = pd.to_numeric(df["bus"], errors="coerce").fillna(0).astype(int)
    df["rail_boardings"] = (
        pd.to_numeric(df["rail_boardings"], errors="coerce").fillna(0).astype(int)
    )
    df["total_rides"] = (
        pd.to_numeric(df["total_rides"], errors="coerce").fillna(0).astype(int)
    )
    return df


def build_systemwide_monthly(df: pd.DataFrame) -> pd.DataFrame:
    """
    Aggregate systemwide daily data to monthly totals for 2024.

    Returns:
        DataFrame with columns:
            year, month, bus, rail_boardings, total_rides
    """
    df = df.copy()

    df["year"] = df["service_date"].dt.year.astype(int)
    df["month"] = df["service_date"].dt.month.astype(int)

    out = (
        df[df["year"] == 2024]
        .groupby(["year", "month"], as_index=False)[
            ["bus", "rail_boardings", "total_rides"]
        ]
        .sum()
    )
    return out


def main() -> None:
    _ensure_dirs()

    # Station monthly (already monthly in source)
    station_raw = load_station_monthly_raw()
    station_clean = build_station_monthly_clean(station_raw)
    station_clean.to_csv(OUT_DIR / "cta_station_monthly_2024_clean.csv", index=False)

    # Systemwide monthly (aggregate from daily)
    sys_raw = load_systemwide_daily_raw()
    sys_monthly = build_systemwide_monthly(sys_raw)
    sys_monthly.to_csv(OUT_DIR / "cta_systemwide_monthly_2024_clean.csv", index=False)

    print("CTA 2024 data successfully cleaned and written to data/processed/.")


if __name__ == "__main__":
    main()
