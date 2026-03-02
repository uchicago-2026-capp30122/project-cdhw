import pandas as pd
import plotly.express as px

MISSING_SENTINELS = {-666666666, -999999999, 666666666, 999999999}

def make_choropleth(df: pd.DataFrame, geojson: dict, id_col: str, id_prop: str, var_name: str):
    if not var_name:
        return px.scatter(title="No variable selected.")

    dff = df.copy()

    # Ensure id formatting
    dff[id_col] = dff[id_col].astype(str)
    if id_col == "GEOID":
        dff[id_col] = dff[id_col].str.zfill(11)

    # Numeric var cleaning
    dff[var_name] = pd.to_numeric(dff[var_name], errors="coerce")

    # Fix known sentinel income codes
    if var_name == "median_hh_income":
        dff.loc[dff[var_name].isin(MISSING_SENTINELS), var_name] = pd.NA
        dff.loc[dff[var_name] <= 0, var_name] = pd.NA

    dff = dff.dropna(subset=[var_name])

    fig = px.choropleth_map(
        dff,
        geojson=geojson,
        locations=id_col,
        featureidkey=f"properties.{id_prop}",
        color=var_name,
        color_continuous_scale="Viridis",
        map_style="open-street-map",
        zoom=9,
        center={"lat": 41.88, "lon": -87.63},
        opacity=0.65,
        hover_data=[id_col, var_name],
    )
    fig.update_layout(margin={"r": 0, "t": 40, "l": 0, "b": 0})
    return fig