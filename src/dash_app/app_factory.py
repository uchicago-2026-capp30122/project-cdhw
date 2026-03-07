"""

"""

from dash import Dash, Input, Output

from .config import TRACT_CSV, TRACT_GEOJSON, CA_CSV, CA_GEOJSON, DROPDOWN_VARS
from .io import load_df, load_geojson
from .layout import make_layout
from .figures import make_choropleth, NEED_COLOR_COLS

def create_app():
    # Load both datasets once
    tract_df = load_df(TRACT_CSV, id_col="GEOID")
    tract_geo = load_geojson(TRACT_GEOJSON)

    ca_df = load_df(CA_CSV, id_col="community_area")
    ca_geo = load_geojson(CA_GEOJSON)

    # filter dropdown variables to those present in both tract & CA data (so the dropdown works no matter the toggle)
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
    )
    def update(geo_level, var_name):
        if geo_level == "ca":
            return make_choropleth(
                df=ca_df,
                geojson=ca_geo,
                id_col="community_area",
                id_prop="community_area",
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