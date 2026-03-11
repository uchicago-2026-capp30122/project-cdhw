"""
Creates Dash app/dashboard, via callback

This module defines `create_app()`, which assembles the Dash application:
- Loads tract-level and community-area-level datasets (CSV + GeoJSON) once at startup
- Computes the set of variables shared across both datasets so the dropdown works for either geography
- Constructs the layout (toggle + dropdown + map)
- Registers the callback that switches between tract vs. community area mapping

Design:
- Keep this file focused on wiring (app creation + callbacks).
- Keep layout generation in `layout.py`, plotting in `figures.py`, and data loading in `io.py`.
"""

from pathlib import Path
from dash import Dash, Input, Output
from .config import TRACT_CSV, TRACT_GEOJSON, CA_CSV, CA_GEOJSON, CTA_CSV, DROPDOWN_VARS
from .io import load_df, load_geojson
from .layout import make_layout
from .figures import make_choropleth, add_selected_overlays, NEED_COLOR_COLS

ROOT_DIR = Path(__file__).resolve().parents[2]
ASSETS_DIR = ROOT_DIR / "docs" / "assets"


def create_app():
    # Load both datasets once
    tract_df = load_df(TRACT_CSV, id_col="GEOID")
    tract_geo = load_geojson(TRACT_GEOJSON)

    ca_df = load_df(CA_CSV, id_col="community_area")
    ca_geo = load_geojson(CA_GEOJSON)

    cta_df = load_df(CTA_CSV, id_col="station_id")

    # de-duplicating rows in CTA data, to use only 1 row (total annual rides) per station, instead of 12 monthly rows.
    cta_df = cta_df.sort_values(["station_id", "year", "month"]).drop_duplicates(
        subset=["station_id"], keep="last"
    )

    # What variables exist in both (so the dropdown works no matter the toggle)
    tract_cols = set(tract_df.columns)
    ca_cols = set(ca_df.columns)
    map_vars = []
    for v in DROPDOWN_VARS:
        color_col = NEED_COLOR_COLS.get(v, v)
        if color_col in tract_cols and color_col in ca_cols:
            map_vars.append(v)

    app = Dash(
        __name__,
        assets_folder=str(ASSETS_DIR),
    )
    app.layout = make_layout(map_vars)

    @app.callback(
        Output("choropleth", "figure"),
        Input("geo-toggle", "value"),
        Input("var-dropdown", "value"),
        Input("overlay-toggle", "value"),
    )
    def update(geo_level, var_name, overlays):
        if geo_level == "ca":
            fig = make_choropleth(
                df=ca_df,
                geojson=ca_geo,
                id_col="community_area",
                id_prop="community_area",
                var_name=var_name,
            )
        else:
            fig = make_choropleth(
                df=tract_df,
                geojson=tract_geo,
                id_col="GEOID",
                id_prop="GEOID",
                var_name=var_name,
            )

        fig = add_selected_overlays(
            fig,
            overlays,
            cta_df=cta_df,
            rideshare_df=ca_df,
            cta_lat_col="lat",
            cta_lon_col="lon",
            cta_size_col="annual_total",
            cta_name_col="station_name",
        )
        return fig

    return app
