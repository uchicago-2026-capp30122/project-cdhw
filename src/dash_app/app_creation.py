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

from dash import Dash, Input, Output
from .config import TRACT_CSV, TRACT_GEOJSON, CA_CSV, CA_GEOJSON, CTA_CSV, DROPDOWN_VARS
from .io import load_df, load_geojson
from .layout import make_layout
from .figures import make_choropleth, add_selected_overlays, NEED_COLOR_COLS


def create_app():
    # Load both datasets once
    tract_df = load_df(TRACT_CSV, id_col="GEOID")
    tract_geo = load_geojson(TRACT_GEOJSON)

    ca_df = load_df(CA_CSV, id_col="community_area")
    ca_geo = load_geojson(CA_GEOJSON)
    
    # cta_df = load_df(CTA_CSV, id_col = #tbd) # insert Ciara's CSV dataset here

    # What variables exist in both (so the dropdown works no matter the toggle)
    tract_cols = set(tract_df.columns)
    ca_cols = set(ca_df.columns)
    map_vars = []
    for v in DROPDOWN_VARS:
        color_col = NEED_COLOR_COLS.get(v, v)
        if color_col in tract_cols and color_col in ca_cols:
            map_vars.append(v)
            
    app = Dash(__name__)
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
            # cta_df=cta_df, # uncomment, once aggregated CSV dataset is complete.
            rideshare_df=ca_df,
        )
        return fig
    
    return app
