"""
For counts (like pop_total): weighted sum
For rates/percent: weighted average by population or households (we can pick a clean rule)
Computes CA-level transport_need_index (percentiles within CAs)

Input
- data/processed/acs5_2024_il_tract_clean.csv
- data/processed/tract_to_ca_crosswalk.csv

Output
- data/processed/community_area_census.csv

"""

from pathlib import Path
import numpy as np
import pandas as pd
from process.census_data.make_tract_features import DEFAULT_WEIGHTS, NEED_HIGH_VARS, NEED_LOW_VARS, add_need_component_scores

# Copied from make_tract_features.py (to keep this script self-contained)
DEFAULT_WEIGHTS = {
    "median_hh_income": 1.0,     # inverted; negative relationship b/w median income & transport need
    "pct_no_vehicle_hh": 1.0,
    "pct_disabled": 1.0,
    "pct_65_plus": 1.0,
}

def add_need_component_scores(
    df: pd.DataFrame,
    high_vars: set = None,
    low_vars: set = None,
    suffix: str = "_need_0_100",
) -> pd.DataFrame:
    """
    Create a percentile-based need score on 0-100 for each component variable,
    where higher always = greater transportation need.
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

        dff[col] = pd.to_numeric(dff[col], errors="coerce")
        pct = dff[col].rank(pct=True, method="average")

        if col in low_vars:
            pct = 1 - pct  # lower raw value = higher need

        dff[f"{col}{suffix}"] = (pct * 100).round(2)

    return dff

def add_need_index_percentile(df: pd.DataFrame,
                              weights: dict = None,
                              index_col: str = "transportation_need_index_0_100",
                              suffix: str = "_need_0_100",) -> pd.DataFrame:
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

    need_df = dff[need_cols]

<<<<<<< Updated upstream
    num = pct_df.mul(w_series, axis = 1).sum(axis = 1, skipna = True)
    den = pct_df.notna().mul(w_series, axis = 1).sum(axis = 1)
    need_0_1 = num / den
=======
    w_series = pd.Series(
        {
            f"{raw_col}{suffix}": weight
            for raw_col, weight in weights.items()
            if weight != 0 and f"{raw_col}{suffix}" in need_df.columns
        },
        dtype=float,
    )

    # weighted average of already-aligned 0-100 need columns
    num = need_df.mul(w_series, axis=1).sum(axis=1, skipna=True)
    den = need_df.notna().mul(w_series, axis=1).sum(axis=1)
    dff[index_col] = (num / den).round(2)
>>>>>>> Stashed changes

    return dff


def _infer_crosswalk_cols(xwalk: pd.DataFrame):
    # Tract GEOID column
    geoid_col = "GEOID" if "GEOID" in xwalk.columns else None
    if geoid_col is None:
        raise ValueError("Crosswalk must have a GEOID column.")

    # Community area id column (common candidates)
    ca_candidates = [c for c in xwalk.columns if c.lower() in {"community_area", "ca", "ca_id", "area_numbe", "area_number", "communityarea"}]
    if not ca_candidates:
        # fallback: anything with "community" or "area" in name
        ca_candidates = [c for c in xwalk.columns if ("community" in c.lower()) or ("area" in c.lower())]
    if not ca_candidates:
        raise ValueError("Could not infer community area id column in crosswalk.")
    ca_col = ca_candidates[0]

    # Weight column
    w_candidates = [c for c in xwalk.columns if any(k in c.lower() for k in ["weight", "share", "pct", "proportion", "frac"])]
    w_col = w_candidates[0] if w_candidates else None

    return geoid_col, ca_col, w_col


def aggregate_to_ca(tract_df: pd.DataFrame, xwalk: pd.DataFrame) -> pd.DataFrame:
    geoid_col, ca_col, w_col = _infer_crosswalk_cols(xwalk)

    df = tract_df.copy()
    df["GEOID"] = df["GEOID"].astype(str).str.zfill(11)

    xw = xwalk.copy()
    xw[geoid_col] = xw[geoid_col].astype(str).str.zfill(11)

    if w_col is None:
        xw["_w"] = 1.0
        w_col = "_w"
    else:
        xw[w_col] = pd.to_numeric(xw[w_col], errors="coerce").fillna(0.0)

    merged = df.merge(xw[[geoid_col, ca_col, w_col]], left_on="GEOID", right_on=geoid_col, how="inner")

    # Weighted counts
    for c in ["pop_total", "hh_total", "hh_no_vehicle", "disability_total", "disability_with", "age_65_plus"]:
        if c in merged.columns:
            merged[c] = pd.to_numeric(merged[c], errors="coerce")
            merged[f"{c}_w"] = merged[c] * merged[w_col]

    group = merged.groupby(ca_col, dropna=False)

    out = pd.DataFrame({ca_col: group.size().index})

    # pop_total (sum of weighted pop)
    if "pop_total_w" in merged.columns:
        out["pop_total"] = group["pop_total_w"].sum().values

    # median_hh_income (weighted average; prefer hh_total if present, else pop_total)
    if "median_hh_income" in merged.columns:
        merged["median_hh_income"] = pd.to_numeric(merged["median_hh_income"], errors="coerce")
        if "hh_total_w" in merged.columns:
            num = group.apply(lambda g: (g["median_hh_income"] * g["hh_total_w"]).sum(skipna=True))
            den = group["hh_total_w"].sum()
        elif "pop_total_w" in merged.columns:
            num = group.apply(lambda g: (g["median_hh_income"] * g["pop_total_w"]).sum(skipna=True))
            den = group["pop_total_w"].sum()
        else:
            num = group["median_hh_income"].mean()
            den = 1.0
        out["median_hh_income"] = (num / den).values

    # Rates computed from summed numerators/denominators
    if "hh_no_vehicle_w" in merged.columns and "hh_total_w" in merged.columns:
        out["pct_no_vehicle_hh"] = (group["hh_no_vehicle_w"].sum() / group["hh_total_w"].sum()).values

    if "disability_with_w" in merged.columns and "disability_total_w" in merged.columns:
        out["pct_disabled"] = (group["disability_with_w"].sum() / group["disability_total_w"].sum()).values

    if "age_65_plus_w" in merged.columns and "pop_total_w" in merged.columns:
        out["pct_65_plus"] = (group["age_65_plus_w"].sum() / group["pop_total_w"].sum()).values

    # Rename CA id column to a consistent name for Dash
    out = out.rename(columns={ca_col: "community_area"})
    out["community_area"] = pd.to_numeric(out["community_area"], errors="coerce").astype("Int64")

    # create CA-level need-oriented component score columns
    # so the Dash dropdown variables can map to *_need_0_100 columns.
    out = add_need_component_scores(out)

    # compute CA-level composite index from those component need scores
    out = add_need_index_percentile(out, index_col="transportation_need_index_0_100")

<<<<<<< Updated upstream
    # Quintiles
=======
    # optional: quintiles
>>>>>>> Stashed changes
    out["need_quintile"] = pd.qcut(
        out["transportation_need_index_0_100"],
        q = 5,
        labels = ["Very Low", "Low", "Moderate", "High", "Very High"],
        duplicates = "drop",
    )

    return out


def main():
    ROOT = Path(__file__).resolve().parents[2]
    tract_path = ROOT / "data" / "processed" / "tract_features.csv"
    xwalk_path = ROOT / "data" / "processed" / "tract_to_ca_crosswalk.csv"
    out_path = ROOT / "data" / "processed" / "community_area_census.csv"

    tract_df = pd.read_csv(tract_path, dtype={"GEOID": str})
    xwalk = pd.read_csv(xwalk_path)

    ca_df = aggregate_to_ca(tract_df, xwalk)
    ca_df.to_csv(out_path, index=False)
    print(f"Wrote community area dataset: {len(ca_df):,} rows -> {out_path}")


if __name__ == "__main__":
    main()