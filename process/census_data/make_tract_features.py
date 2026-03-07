"""
Compute transportation need for eaech Census data variable, and add to 
Computes transport_need_index (percentile composite from census data)
Outputs new CSV: clean census data + a new column for "transportation need index"

Input: data/processed/acs5_2024_il_tract_clean.csv
Output: data/processed/tract_features.csv

Ensures GEOID is a zero-padded string
Computes quintiles/labels for map bins

"""
import numpy as np
import pandas as pd

# weight assigned to each variable, when constructing the transit need index.
DEFAULT_WEIGHTS = {
    "median_hh_income": 1.0,     # will be inverted
    "pct_no_vehicle_hh": 1.0,
    "pct_disabled": 1.0,
    "pct_65_plus": 1.0,
}

# variables where higher raw value = greater transit need
NEED_HIGH_VARS = {
    "pct_no_vehicle_hh",
    "pct_disabled",
    "pct_65_plus",
}

# variables where lower raw value = greater transit need
NEED_LOW_VARS = {
    "median_hh_income",
}

def add_need_component_scores(df: pd.DataFrame,
                              high_vars: set = None,
                              low_vars: set = None,
                              suffix: str = "_need_0_100",) -> pd.DataFrame:
    """
    Create a percentile-based need score on 0-100 for each component variable,
    in the transportation need index, where higher always = greater transportation need.
    """
    if high_vars is None:
        high_vars = NEED_HIGH_VARS
    if low_vars is None:
        low_vars = NEED_LOW_VARS

    dff = df.copy()

    vars_to_score = list(high_vars | low_vars)

    for col in vars_to_score:
        if col not in dff.columns:
            continue

        dff[col] = pd.to_numeric(dff[col], errors = "coerce")

        pct = dff[col].rank(pct = True, method = "average")

        if col in low_vars:
            pct = 1 - pct   # lower raw value = higher need

        dff[f"{col}{suffix}"] = (pct * 100).round(2)

    return dff


def add_need_index_percentile(df: pd.DataFrame,
                              weights: dict = None,
                              index_col: str = "transportation_need_index_0_100",
                              suffix: str = "_need_0_100") -> pd.DataFrame:
    """
    Builds a 0-100 'transportation need index' 
    where higher = greater need for accessible, external transportation options.

    Uses percentile ranks across rows for robustness.
    Inverts median_hh_income so lower income -> higher need.
    """
    if weights is None:
        weights = DEFAULT_WEIGHTS

    dff = df.copy()
    
    need_cols = []
    for raw_col, weight in weights.items():
        if weight == 0:
            continue
        need_col = f"{raw_col}{suffix}"
        if need_col in dff.columns:
            need_cols.append(need_col)
            
    
    # weighted average of each indicator (already on 0-100 need scale), no extra inversion needed.
    need_df = dff[need_cols]
    w_series = pd.Series(
        {f"{raw_col}{suffix}": weight for raw_col, weight in weights.items()
         if weight != 0 and f"{raw_col}{suffix}" in need_df.columns},
        dtype=float,
    )

    num = need_df.mul(w_series, axis=1).sum(axis=1, skipna=True)
    den = need_df.notna().mul(w_series, axis=1).sum(axis=1)
    dff[index_col] = (num / den).round(2)

    return dff

def main():
    df = pd.read_csv("data/processed/acs5_2024_il_tract_clean.csv", dtype={"GEOID": str})
    
    # If clean file already guarantees 11-digit GEOIDs, so shouldn't need to re-pad GEOID.
    # df["GEOID"] = df["GEOID"].astype(str).str.zfill(11)

    # First create per-variable need-oriented component scores.
    df = add_need_component_scores(df)
    
    # Build the composite index from the need-oriented component columns
    # instead of re-ranking and inverting the raw variables again.
    df = add_need_index_percentile(df)

    
    df["need_quintile"] = pd.qcut(
        df["transportation_need_index_0_100"],
        q = 5,
        labels = ["Very Low", "Low", "Moderate", "High", "Very High"])

    df.to_csv("data/processed/tract_features.csv", index=False)
    
if __name__ == "__main__":
    main()