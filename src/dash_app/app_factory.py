from dash import Dash, Input, Output

from .config import TRACT_CSV, TRACT_GEOJSON, CA_CSV, CA_GEOJSON, DROPDOWN_VARS
from .io import load_df, load_geojson
from .layout import make_layout
from .figures import make_choropleth

def create_app():
    # Load both datasets once
    tract_df = load_df(TRACT_CSV, id_col="GEOID")
    tract_geo = load_geojson(TRACT_GEOJSON)

    ca_df = load_df(CA_CSV, id_col="community_area")
    ca_geo = load_geojson(CA_GEOJSON)

    # What variables exist in BOTH (so the dropdown works no matter the toggle)
    tract_cols = set(tract_df.columns)
    ca_cols = set(ca_df.columns)
    map_vars = [v for v in DROPDOWN_VARS if (v in tract_cols and v in ca_cols)]

    app = Dash(__name__)
    app.layout = make_layout(map_vars)

    @app.callback(
        Output("choropleth", "figure"),
        Input("geo-toggle", "value"),
        Input("var-dropdown", "value"),
    )
    def update(geo_level, var_name):
        if geo_level == "ca":
            return make_choropleth(
                df=ca_df,
                geojson=ca_geo,
                id_col="community_area",
                id_prop="community_area",   # CHANGE if your geojson uses a different property name
                var_name=var_name,
            )

        # default: tract
        return make_choropleth(
            df=tract_df,
            geojson=tract_geo,
            id_col="GEOID",
            id_prop="GEOID",
            var_name=var_name,
        )

    return app