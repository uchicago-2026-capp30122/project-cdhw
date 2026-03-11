# Clean the census data & determine percentages, after fetch_census_data has created a raw CSV.

from pathlib import Path
import pandas as pd

YEAR = 2024

AGE_65_VARS = [
    "B01001_020E",
    "B01001_021E",
    "B01001_022E",
    "B01001_023E",
    "B01001_024E",
    "B01001_025E",
    "B01001_044E",
    "B01001_045E",
    "B01001_046E",
    "B01001_047E",
    "B01001_048E",
    "B01001_049E",
]

# columns to cast to numeric (b/c Census API returns everything as strings)
NUMERIC_COLS = [
    "B01003_001E",  # total pop
    "B19013_001E",  # median income
    "B08201_001E",  # total households
    "B08201_002E",  # no vehicle households
    "C18108_001E",  # disability table total
    "C18108_002E",  # disability table with disability
    *AGE_65_VARS,
]


def clean_acs(in_path: Path) -> pd.DataFrame:
    """
    Read raw ACS CSV, cast numeric columns, compute derived indicators,
    rename columns, and return a cleaned DataFrame.
    """
    df = pd.read_csv(in_path, dtype=str)

    # Cast numeric columns
    for col in NUMERIC_COLS:
        if col in df.columns:
            df[col] = pd.to_numeric(df[col], errors="coerce")

    # Replace absurd Census sentinel values (for median income) with NaN
    MISSING_SENTINELS = {-666666666, -999999999, 666666666, 999999999}

    if "B19013_001E" in df.columns:
        df.loc[df["B19013_001E"].isin(MISSING_SENTINELS), "B19013_001E"] = pd.NA
        df.loc[df["B19013_001E"] <= 0, "B19013_001E"] = pd.NA  # income cannot be <= 0

    # Calculate: age 65+ count + percent
    df["age_65_plus"] = df[AGE_65_VARS].sum(axis=1, min_count=1)
    df["pct_65_plus"] = df["age_65_plus"] / df["B01003_001E"]

    # Calculate: percent of households with no vehicle
    df["pct_no_vehicle_hh"] = df["B08201_002E"] / df["B08201_001E"]

    # Calculate: percent disabled (based on C18108 total + with disability)
    df["pct_disabled"] = df["C18108_002E"] / df["C18108_001E"]

    # Keep a clean set of columns for downstream joins/viz
    keep = [
        "year",
        "GEOID",
        "NAME",
        "state",
        "county",
        "tract",
        "B01003_001E",
        "B19013_001E",
        "B08201_001E",
        "B08201_002E",
        "C18108_001E",
        "C18108_002E",
        "age_65_plus",
        "pct_65_plus",
        "pct_no_vehicle_hh",
        "pct_disabled",
    ]
    keep = [c for c in keep if c in df.columns]
    df = df[keep].copy()

    # Rename for readability in Dash dropdowns
    df = df.rename(
        columns={
            "B01003_001E": "pop_total",
            "B19013_001E": "median_hh_income",
            "B08201_001E": "hh_total",
            "B08201_002E": "hh_no_vehicle",
            "C18108_001E": "disability_total",
            "C18108_002E": "disability_with",
        }
    )

    return df


def main():
    # Repo root is two levels up from project_cdhw.process/census_data/
    ROOT = Path(__file__).resolve().parents[2]
    raw_path = ROOT / "data" / "raw" / f"acs5_{YEAR}_il_tract_raw.csv"
    out_path = ROOT / "data" / "processed" / f"acs5_{YEAR}_il_tract_clean.csv"
    out_path.parent.mkdir(parents=True, exist_ok=True)

    df_clean = clean_acs(raw_path)
    df_clean.to_csv(out_path, index=False)
    print(f"Wrote cleaned ACS tract data: {len(df_clean):,} rows -> {out_path}")


if __name__ == "__main__":
    main()
