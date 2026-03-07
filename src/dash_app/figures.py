"""
Creates visuals (choropleth).
<<<<<<< Updated upstream

=======
>>>>>>> Stashed changes
"""


import pandas as pd
import plotly.express as px

# placeholder values that the Census uses, for tracts w/ no data:
MISSING_SENTINELS = {-666666666, -999999999, 666666666, 999999999}

# map user-facing/raw dropdown vars to the need-oriented score column.
NEED_COLOR_COLS = {
    "transportation_need_index_0_100": "transportation_need_index_0_100",
    "median_hh_income": "median_hh_income_need_0_100",
    "pct_no_vehicle_hh": "pct_no_vehicle_hh_need_0_100",
    "pct_disabled": "pct_disabled_need_0_100",
    "pct_65_plus": "pct_65_plus_need_0_100",
}

def make_choropleth(df: pd.DataFrame, geojson: dict, id_col: str, id_prop: str, var_name: str):
    if not var_name:
        return px.scatter(title="No variable selected.")

    dff = df.copy()

    # Ensure id formatting
    dff[id_col] = dff[id_col].astype(str)
    if id_col == "GEOID":
        dff[id_col] = dff[id_col].str.zfill(11)
        
    # determining which column should drive color. For component indicators, use the need-oriented score column.
    color_col = NEED_COLOR_COLS.get(var_name, var_name)

    # Coerce raw display vars & color vars to numeric if present.
    if var_name in dff.columns:
        dff[var_name] = pd.to_numeric(dff[var_name], errors = "coerce")
    
    if color_col in dff.columns:
        dff[color_col] = pd.to_numeric(dff[color_col], errors="coerce")

    # Fix known sentinel (placeholder) income values
    if var_name == "median_hh_income":
        dff.loc[dff[var_name].isin(MISSING_SENTINELS), var_name] = pd.NA
        dff.loc[dff[var_name] <= 0, var_name] = pd.NA

    # # clean impossible values in the need-color column if present as sentinels via pipeline issues.
    # if color_col in dff.columns:
    #     dff.loc[dff[color_col].isin(MISSING_SENTINELS), color_col] = pd.NA
        
    dff = dff.dropna(subset=[color_col])
    
    # legend title so users know this is a need-oriented scale.
    if var_name == "transportation_need_index_0_100":
        colorbar_title = "transportation_need_index_0_100"
    else:
        colorbar_title = f"{var_name}_need_0_100"

    # hover data
    hover_cols = [id_col]
    if var_name in dff.columns:
        hover_cols.append(var_name)
    if color_col != var_name and color_col in dff.columns:
        hover_cols.append(color_col)

    fig = px.choropleth_map(
        dff,
        geojson = geojson,
        locations = id_col,
        featureidkey = f"properties.{id_prop}",
        color = color_col,
        color_continuous_scale = "Viridis_r",
        map_style = "open-street-map",
        zoom = 9,
        center = {"lat": 41.88, "lon": -87.63},
        opacity = 0.65,
        hover_data = hover_cols,
    )
    fig.update_coloraxes(colorbar_title=colorbar_title)
    fig.update_layout(margin = {"r": 0, "t": 40, "l": 0, "b": 0})
    return fig