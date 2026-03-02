from pathlib import Path
import pandas as pd

RAW_PATH = Path("data/raw/cta_station_monthly_2024_raw.csv")
OUT_PATH = Path("data/processed/cta_station_monthly_2024_clean.csv")


def main() -> None:
    df = pd.read_csv(RAW_PATH)

    df["station_id"] = pd.to_numeric(df["station_id"], errors="coerce").astype("Int64")
    df["stationame"] = df["stationame"].astype(str)
    df["month_beginning"] = pd.to_datetime(df["month_beginning"], errors="coerce")
    df["monthtotal"] = pd.to_numeric(df["monthtotal"], errors="coerce").fillna(0).astype(int)

    df["year"] = df["month_beginning"].dt.year.astype("Int64")
    df["month"] = df["month_beginning"].dt.month.astype("Int64")

    out = (
        df.rename(columns={"stationame": "station_name", "monthtotal": "month_total"})
        [["station_id", "station_name", "year", "month", "month_total"]]
        .query("year == 2024")
        .reset_index(drop=True)
    )
    out = out.drop_duplicates(subset=["station_id", "year", "month"])

    OUT_PATH.parent.mkdir(parents=True, exist_ok=True)
    out.to_csv(OUT_PATH, index=False)

    print(f"Wrote {OUT_PATH} ({len(out)} rows, {out['station_id'].nunique()} stations)")

if __name__ == "__main__":
    main()