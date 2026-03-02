"""
Computes transport_need_index (percentile composite from census data)
Outputs new CSV: clean census data + a new column for "transportation need index"

Input: data/processed/acs5_2024_il_tract_clean.csv
Output: data/processed/tract_features.csv

Ensures GEOID is a zero-padded string
Computes quintiles/labels for map bins

"""
import numpy as np
import pandas as pd

DEFAULT_WEIGHTS = {
    "median_hh_income": 1.0,     # will be inverted
    "pct_no_vehicle_hh": 1.0,
    "pct_disabled": 1.0,
    "pct_65_plus": 1.0,
    # "pop_total": 0.0,          # keep out of the rate index by default
}

def add_need_index_percentile(df: pd.DataFrame,
                              weights: dict = None,
                              index_col: str = "transportation_need_index_0_100") -> pd.DataFrame:
    """
    Builds a 0-100 'transportation need index' 
    where higher = greater need for accessible, external transportation options.

    Uses percentile ranks across rows for robustness.
    Inverts median_hh_income so lower income -> higher need.
    """
    if weights is None:
        weights = DEFAULT_WEIGHTS

    dff = df.copy()

    # Ensure numeric
    for col in weights.keys():
        if col in dff.columns:
            dff[col] = pd.to_numeric(dff[col], errors="coerce")

    # Build percentile-rank features in 0..1
    pct_feats = {}
    for col, w in weights.items():
        if w == 0 or col not in dff.columns:
            continue
        # pct rank: NaNs stay NaN
        pct = dff[col].rank(pct=True, method="average")
        if col == "median_hh_income":
            pct = 1 - pct  # invert so low income => high need
        pct_feats[col] = pct

    pct_df = pd.DataFrame(pct_feats)

    # Weighted average, ignoring NaNs row-wise
    w_series = pd.Series({c: weights[c] for c in pct_df.columns}, dtype=float)

    # For each row: sum(pct * w) / sum(w where pct not null)
    num = pct_df.mul(w_series, axis=1).sum(axis=1, skipna=True)
    den = pct_df.notna().mul(w_series, axis=1).sum(axis=1)
    need_0_1 = num / den

    dff[index_col] = (need_0_1 * 100).round(2)
    return dff

def main():
    df = pd.read_csv("data/processed/acs5_2024_il_tract_clean.csv", dtype={"GEOID": str})
    
    # If clean file already guarantees 11-digit GEOIDs, so shouldn't need to re-pad GEOID.
    # df["GEOID"] = df["GEOID"].astype(str).str.zfill(11)

    # add index here
    df = add_need_index_percentile(df)
    
    df["need_quintile"] = pd.qcut(
        df["transportation_need_index_0_100"],
        q = 5,
        labels = ["Very Low", "Low", "Moderate", "High", "Very High"])

    df.to_csv("data/processed/tract_features.csv", index=False)
    
if __name__ == "__main__":
    main()