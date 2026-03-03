from pathlib import Path

import altair as alt
import pandas as pd


PROCESSED_DIR = Path("data/processed")
OUT_DIR = Path("visuals")


def load_commarea_annual() -> pd.DataFrame:
    """
    Loads annual CTA ridership totals by community area.
    Expected columns:
      community_area, community, cta_2024_total
    """
    path = PROCESSED_DIR / "cta_commarea_annual_2024.csv"
    df = pd.read_csv(path)

    df["community_area"] = pd.to_numeric(df["community_area"], errors="coerce").astype("Int64")
    df["cta_2024_total"] = pd.to_numeric(df["cta_2024_total"], errors="coerce").fillna(0).astype(int)
    df["community"] = df["community"].astype(str)

    return df


def make_top10_bar(df: pd.DataFrame) -> alt.Chart:
    """
    Returns an Altair bar chart of top 10 community areas by CTA ridership.
    """
    top10 = df.sort_values("cta_2024_total", ascending=False).head(10).copy()

    chart = (
        alt.Chart(top10)
        .mark_bar()
        .encode(
            x=alt.X("cta_2024_total:Q", title="CTA Rail Entries (2024)"),
            y=alt.Y("community:N", sort="-x", title="Community Area"),
            tooltip=[
                alt.Tooltip("community:N", title="Community Area"),
                alt.Tooltip("community_area:Q", title="CA #"),
                alt.Tooltip("cta_2024_total:Q", title="Total", format=","),
            ],
        )
        .properties(
            width=700,
            height=420,
            title="Top 10 Community Areas by CTA Rail Ridership (2024)",
        )
    )
    return chart


def main() -> None:
    OUT_DIR.mkdir(parents=True, exist_ok=True)

    df = load_commarea_annual()
    chart = make_top10_bar(df)

    out_path = OUT_DIR / "cta_top10_commareas_2024.html"
    chart.save(out_path)
    print(f"Wrote {out_path}")


if __name__ == "__main__":
    main()