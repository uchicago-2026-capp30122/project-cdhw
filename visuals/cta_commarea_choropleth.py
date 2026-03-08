from pathlib import Path
import json

import altair as alt
import polars as pl

PROCESSED_DIR = Path("data/processed")
GEOJSON_PATH = PROCESSED_DIR / "community_areas.pretty.geojson"
CTA_CA_MONTHLY = PROCESSED_DIR / "cta_commarea_monthly_2024.csv"


def load_geojson() -> dict:
    with open(GEOJSON_PATH, "r", encoding="utf-8") as f:
        return json.load(f)


def load_cta_ca_monthly() -> pl.DataFrame:
    df = pl.read_csv(CTA_CA_MONTHLY)
    return df


def build_cta_ca_annual(df: pl.DataFrame) -> pl.DataFrame:
    # 2024 total per community area
    out = (
        df.group_by(["community_area", "community"])
        .agg(pl.col("cta_month_total").sum().alias("cta_2024_total"))
        .sort("cta_2024_total", descending=True)
    )
    return out


def choropleth_cta_annual(ca_geojson: dict, ca_annual: pl.DataFrame) -> alt.Chart:
    # IMPORTANT: geojson feature property is "community_area" (numeric)
    # We match on that key via transform_lookup.

    data_rows = ca_annual.to_pandas()  # Altair expects pandas-friendly
    source = alt.Data(values=data_rows.to_dict(orient="records"))
    data_rows = ca_annual.to_pandas()

    # source = alt.Data(values=data_rows.to_dict(orient="records"))

    chart = (
        alt.Chart(alt.Data(values=ca_geojson["features"]))
        .mark_geoshape()
        .encode(
            color=alt.Color("cta_2024_total:Q", title="CTA entries (2024)"),
            tooltip=[
                alt.Tooltip("properties.community:N", title="Community"),
                alt.Tooltip("properties.community_area:Q", title="Area #"),
                alt.Tooltip("cta_2024_total:Q", title="CTA 2024 total", format=","),
            ],
        )
        .transform_lookup(
            lookup="properties.community_area",
            from_=alt.LookupData(source, "community_area", ["cta_2024_total"]),
        )
        .properties(
            width=700,
            height=500,
            title="CTA 'L' station entries by community area (2024)",
        )
    )

    return chart


def main() -> None:
    ca_geojson = load_geojson()
    ca_monthly = load_cta_ca_monthly()
    ca_annual = build_cta_ca_annual(ca_monthly)

    chart = choropleth_cta_annual(ca_geojson, ca_annual)
    out_html = Path("visuals/cta_commarea_2024_choropleth.html")
    chart.save(out_html)
    print(f"Wrote {out_html}")


if __name__ == "__main__":
    main()
