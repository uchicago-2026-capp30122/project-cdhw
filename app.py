import json
import pandas as pd
import plotly.express as px

from dash import Dash, dcc, html, Input, Output

DATA_CSV = "data/processed/tract_features.csv"
TRACTS_GEOJSON = "data/processed/tracts_chicago.geojson"

def load_data():
    df = pd.read_csv(DATA_CSV, dtype = {"GEOID": str})

    #only showing Cook county, might include DuPage later.
    if "county" in df.columns:
        df = df[df["county"] == 31].copy()  # Cook County numeric FIPS in the CSV

    return df

def load_geojson():
    with open(TRACTS_GEOJSON, "r") as f:
        return json.load(f)

df = load_data()
geojson = load_geojson()

# numeric columns to map
DROPDOWN_VARS = [
    "transportation_need_index_0_100",
    "median_hh_income",
    "pct_no_vehicle_hh",
    "pct_disabled",
    "pct_65_plus",
    "pop_total",
]

# keep only the ones that actually exist in the df
MAP_VARS = [c for c in DROPDOWN_VARS if c in df.columns]

def create_app(df, geojson):
    app = Dash(__name__)

    MAP_VARS = [c for c in DROPDOWN_VARS if c in df.columns]

    app.layout = html.Div(
        style = {"maxWidth": "1100px", "margin": "0 auto", "padding": "16px"},
        children = [
            html.H2("Chicago-area Census Tract Map (MVP)"),
            html.Label("Variable"),
            dcc.Dropdown(
                options = [{"label": v, "value": v} for v in MAP_VARS],
                value = MAP_VARS[0] if MAP_VARS else None,
                clearable = False,
                id = "var-dropdown",
            ),
            dcc.Graph(id = "tract-map", style = {"height": "75vh"}),
        ],
    )

    @app.callback(
        Output("tract-map", "figure"),
        Input("var-dropdown", "value"),
    )
    def update_map(var_name):
        try:
            if not var_name:
                return px.scatter(title="No variable selected.")

            dff = df.copy()

            # Ensure GEOID formatting is consistent
            dff["GEOID"] = dff["GEOID"].astype(str).str.zfill(11)

            # Ensure numeric for data
            dff[var_name] = pd.to_numeric(dff[var_name], errors = "coerce")

            # Drop rows where the variable is missing
            dff = dff.dropna(subset=[var_name])

            fig = px.choropleth_map(
                dff,
                geojson = geojson,
                locations = "GEOID",
                featureidkey = "properties.GEOID",
                color = var_name,
                color_continuous_scale="Viridis",  # or "Plasma", "Inferno"; darker = hotter/greater need
                map_style = "open-street-map",
                zoom = 9,
                center = {"lat": 41.88, "lon": -87.63},
                opacity = 0.65,
            )
            fig.update_layout(margin = {"r": 0, "t": 40, "l": 0, "b": 0})
            return fig

        except Exception as e:
            return px.scatter(title = f"Callback failed for {var_name}: {type(e).__name__}: {e}")
    
    return app


def main():
    df = load_data()
    geojson = load_geojson()
    app = create_app(df, geojson)
    app.run(debug = True)


if __name__ == "__main__":
    main()