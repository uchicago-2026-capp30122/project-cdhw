import os
import time
from pathlib import Path

import httpx
import pandas as pd


BASE_URL = "https://data.cityofchicago.org/resource"
REQUEST_DELAY = 0.1


def _get_headers():
    token = os.getenv("SOCRATA_APP_TOKEN")
    headers = {"Accept": "application/json"}
    if token:
        headers["X-App-Token"] = token
    return headers


def _fetch_all(dataset_id: str, where: str, select: str, order: str = None):
    """
    Generic Socrata fetch with pagination.
    Returns a list of dict rows.
    """
    url = f"{BASE_URL}/{dataset_id}.json"
    headers = _get_headers()

    all_rows = []
    limit = 50000
    offset = 0

    while True:
        time.sleep(REQUEST_DELAY)

        params = {
            "$limit": limit,
            "$offset": offset,
            "$where": where,
            "$select": select,
        }

        if order:
            params["$order"] = order

        resp = httpx.get(url, headers=headers, params=params, timeout=30.0)
        resp.raise_for_status()
        data = resp.json()

        if not data:
            break

        all_rows.extend(data)
        offset += limit

        if len(data) < limit:
            break

    return all_rows


def _where_2024(date_field: str) -> str:
    return (
        f"{date_field} >= '2024-01-01T00:00:00' "
        f"AND {date_field} < '2025-01-01T00:00:00'"
    )


def fetch_station_monthly_2024():
    """
    Fetch 2024 monthly station totals.
    Dataset: t2rn-p8d7
    """
    rows = _fetch_all(
        dataset_id="t2rn-p8d7",
        where=_where_2024("month_beginning"),
        select="station_id,stationame,month_beginning,monthtotal",
        order="month_beginning ASC",
    )

    df = pd.DataFrame(rows)
    return df


def fetch_systemwide_daily_2024():
    """
    Fetch 2024 systemwide daily ridership.
    """
    rows = _fetch_all(
        dataset_id="6iiy-9s97",
        where=_where_2024("service_date"),
        select="service_date,bus,rail_boardings,total_rides",
        order="service_date ASC",
    )

    df = pd.DataFrame(rows)
    return df


def main():
    raw_dir = Path("data/raw")
    raw_dir.mkdir(parents=True, exist_ok=True)

    station_df = fetch_station_monthly_2024()
    station_df.to_csv(raw_dir / "cta_station_monthly_2024_raw.csv", index=False)

    system_df = fetch_systemwide_daily_2024()
    system_df.to_csv(raw_dir / "cta_systemwide_daily_2024_raw.csv", index=False)

    print("CTA 2024 data successfully fetched.")


if __name__ == "__main__":
    main()
