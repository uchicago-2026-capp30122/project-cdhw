from __future__ import annotations

from pathlib import Path

import pandas as pd

PROCESSED_DIR = Path("data/processed")
EXPLORE_DIR = PROCESSED_DIR / "cta_explore"


COMM_MONTHLY_PATH = PROCESSED_DIR / "cta_commarea_monthly_2024.csv"

OUT_ANNUAL_PATH = PROCESSED_DIR / "cta_commarea_annual_2024.csv"
OUT_TOP10_PATH = EXPLORE_DIR / "cta_commarea_top10_2024.csv"
OUT_BOTTOM10_PATH = EXPLORE_DIR / "cta_commarea_bottom10_2024.csv"


def ensure_dirs() -> None:
    EXPLORE_DIR.mkdir(parents=True, exist_ok=True)


def load_commarea_monthly() -> pd.DataFrame:
    """
    Expected columns:
      community_area, community, year, month, cta_month_total
    """
    df = pd.read_csv(COMM_MONTHLY_PATH)

    df["community_area"] = pd.to_numeric(df["community_area"], errors="coerce").astype("Int64")
    df["community"] = df["community"].astype(str)

    df["year"] = pd.to_numeric(df["year"], errors="coerce").astype("Int64")
    df["month"] = pd.to_numeric(df["month"], errors="coerce").astype("Int64")
    df["cta_month_total"] = pd.to_numeric(df["cta_month_total"], errors="coerce").fillna(0).astype(int)

    return df


def build_commarea_annual_2024(df_monthly: pd.DataFrame) -> pd.DataFrame:
    df = df_monthly.copy()

    df = df[df["year"] == 2024].copy()

    out = (
        df.groupby(["community_area", "community"], as_index=False)["cta_month_total"]
        .sum()
        .rename(columns={"cta_month_total": "cta_2024_total"})
        .sort_values("cta_2024_total", ascending=False)
        .reset_index(drop=True)
    )
    return out


def top_n(df_annual: pd.DataFrame, n: int = 10) -> pd.DataFrame:
    return df_annual.sort_values("cta_2024_total", ascending=False).head(n).reset_index(drop=True)


def bottom_n(df_annual: pd.DataFrame, n: int = 10) -> pd.DataFrame:
    return df_annual.sort_values("cta_2024_total", ascending=True).head(n).reset_index(drop=True)


def main() -> None:
    ensure_dirs()

    monthly = load_commarea_monthly()
    annual = build_commarea_annual_2024(monthly)

    annual.to_csv(OUT_ANNUAL_PATH, index=False)
    top_n(annual, 10).to_csv(OUT_TOP10_PATH, index=False)
    bottom_n(annual, 10).to_csv(OUT_BOTTOM10_PATH, index=False)

    print(f"Wrote {OUT_ANNUAL_PATH}")
    print(f"Wrote {OUT_TOP10_PATH}")
    print(f"Wrote {OUT_BOTTOM10_PATH}")
    print(f"Community areas: {annual['community_area'].nunique()}")
    print(f"Total CTA rides 2024 (sum): {annual['cta_2024_total'].sum()}")


if __name__ == "__main__":
    main()