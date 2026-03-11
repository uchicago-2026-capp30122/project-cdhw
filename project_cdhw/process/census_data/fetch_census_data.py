# Fetch the census data, to create a raw CSV.

from pathlib import Path
import httpx
import pandas as pd
import time

# Fetch ACS 5-year tract data for IL (Cook + DuPage)
YEAR = 2024
STATE_FIPS = "17"  # Illinois
COUNTIES = {
    "cook": "031",
    "dupage": "043",
}

# Age 65+ bins from B01001 (Sex by Age) - need to sum for a single 65+ statistic
AGE_VARS = [
    # Males 65+
    "B01001_020E",
    "B01001_021E",
    "B01001_022E",
    "B01001_023E",
    "B01001_024E",
    "B01001_025E",
    # Females 65+
    "B01001_044E",
    "B01001_045E",
    "B01001_046E",
    "B01001_047E",
    "B01001_048E",
    "B01001_049E",
]

NON_AGE_VARS = [
    "B01003_001E",  # total population
    "B19013_001E",  # median household income
    "B08201_001E",  # total households
    "B08201_002E",  # households with no vehicle
    "C18108_001E",  # total (for disability table)
    "C18108_002E",  # with a disability (assumed row in C18108)
]

VARIABLES = NON_AGE_VARS + AGE_VARS


class FetchException(Exception):
    """Turn an httpx.Response into an exception."""

    def __init__(self, response: httpx.Response):
        super().__init__(
            f"{response.status_code} retrieving {response.url}: {response.text}"
        )


def fetch_county_tracts(
    year: int, state: str, county: str, variables: list[str]
) -> pd.DataFrame:
    """
    Fetch all tracts for the given state + county from ACS 5-year estimates.
    Returns: a DataFrame with one row per tract.
    """
    base_url = f"https://api.census.gov/data/{year}/acs/acs5"
    get_vars = ",".join(["NAME"] + variables)

    params = {
        "get": get_vars,
        "for": "tract:*",
        "in": f"state:{state} county:{county}",
    }

    time.sleep(0.5)
    resp = httpx.get(base_url, params=params, timeout=60.0, follow_redirects=True)
    if resp.status_code != 200:
        raise FetchException(resp)

    data = resp.json()
    header, rows = data[0], data[1:]
    df = pd.DataFrame(rows, columns=header)

    # Create GEOID (state + county + tract)
    df["year"] = str(year)
    df["GEOID"] = df["state"] + df["county"] + df["tract"]

    return df


def build_census_csv(year: int, output_filename: Path) -> pd.DataFrame:
    """
    Fetch Cook + DuPage tract data, combine, and write to CSV.
    """
    dfs = []

    for name, fips in COUNTIES.items():
        print(
            f"Fetching {name.title()} County (state = {STATE_FIPS}, county = {fips}) tracts..."
        )
        df_part = fetch_county_tracts(
            year=year, state=STATE_FIPS, county=fips, variables=VARIABLES
        )
        dfs.append(df_part)

    # Vertical stacking county dfs into 1 df & reset index values
    df = pd.concat(dfs, ignore_index=True)

    output_filename.parent.mkdir(parents=True, exist_ok=True)
    df.to_csv(output_filename, index=False)
    print(f"Wrote raw ACS tract data: {len(df):,} rows -> {output_filename}")

    return df


def main():
    # Repo root is two levels up from project_cdhw.process/census_data/
    ROOT = Path(__file__).resolve().parents[2]
    out_path = ROOT / "data" / "raw" / f"acs5_{YEAR}_il_tract_raw.csv"
    build_census_csv(YEAR, out_path)


if __name__ == "__main__":
    main()
