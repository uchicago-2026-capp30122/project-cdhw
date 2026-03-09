"""
Creates visuals (choropleth).
"""

import pandas as pd
import plotly.express as px
import plotly.graph_objects as go

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

DISPLAY_NAMES = {
    "transportation_need_index_0_100": "Transportation Need Index (0-100)",
    "median_hh_income": "Low-Income Need Score (percentile, 0-100)",
    "pct_no_vehicle_hh": "No-Vehicle Household Need Score (percentile, 0-100)",
    "pct_disabled": "Disability Need Score (percentile, 0-100)",
    "pct_65_plus": "Older Adult Need Score (percentile, 0-100)",
}

def make_choropleth(
    df: pd.DataFrame, geojson: dict, id_col: str, id_prop: str, var_name: str
):
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
        dff[var_name] = pd.to_numeric(dff[var_name], errors="coerce")

    if color_col in dff.columns:
        dff[color_col] = pd.to_numeric(dff[color_col], errors="coerce")

    # Fix known sentinel (placeholder) income values
    if var_name == "median_hh_income":
        dff.loc[dff[var_name].isin(MISSING_SENTINELS), var_name] = pd.NA
        dff.loc[dff[var_name] <= 0, var_name] = pd.NA

    dff = dff.dropna(subset=[color_col])

    # legend title so users know this is a need-oriented scale.
    colorbar_title = DISPLAY_NAMES.get(var_name, var_name)

    # user-friendly label for the selected variable in hover
    display_name = DISPLAY_NAMES.get(var_name, var_name)

    # create a single hover-name column that works for both community areas and tracts.
    # For community areas, use community_area_name if present.
    # Otherwise, fall back to the ID value so hover still works cleanly.
    if "community_area_name" in dff.columns:
        dff["_hover_name"] = dff["community_area_name"].astype(str)
    else:
        dff["_hover_name"] = dff[id_col].astype(str)
    
    fig = px.choropleth_mapbox(
        dff,
        geojson = geojson,
        locations = id_col,
        featureidkey = f"properties.{id_prop}",
        color = color_col,
        color_continuous_scale = "Viridis_r",
        mapbox_style = "open-street-map",
        zoom = 9,
        center = {"lat": 41.88, "lon": -87.63},
        opacity = 0.65,
        custom_data=["_hover_name"],
        labels = DISPLAY_NAMES,
    )

    fig.update_traces(
        hovertemplate=(
            "<b>%{customdata[0]}</b><br>"
            + f"{display_name}: "
            + "%{z:.1f}<br>"
            + "<i>Higher = greater relative transportation need in Chicago</i>"
            + "<extra></extra>"
        )
    )
    
    fig.update_coloraxes(colorbar_title = colorbar_title)
    fig.update_layout(margin = {"r": 0, "t": 40, "l": 0, "b": 0})
    return fig

def _prep_point_df(df, lat_col, lon_col, size_col):
    if df is None or df.empty:
        return pd.DataFrame()

    dff = df.copy()
    dff[lat_col] = pd.to_numeric(dff[lat_col], errors="coerce")
    dff[lon_col] = pd.to_numeric(dff[lon_col], errors="coerce")
    dff[size_col] = pd.to_numeric(dff[size_col], errors="coerce")

    dff = dff.dropna(subset=[lat_col, lon_col, size_col])
    dff = dff[dff[size_col] > 0]

    return dff


def _sizeref(values, desired_max_px=30):
    max_val = values.max() if len(values) else 0
    if not max_val or pd.isna(max_val):
        return 1
    return 2.0 * max_val / (desired_max_px ** 2)


def add_point_overlay(
    fig,
    df,
    *,
    lat_col,
    lon_col,
    size_col,
    name,
    hover_name_col = None,
    extra_hover_cols = None,
    max_marker_px = 30,
    color = None,
):
    dff = _prep_point_df(df, lat_col, lon_col, size_col)
    if dff.empty:
        return fig

    extra_hover_cols = extra_hover_cols or []

    hover_text = None
    if hover_name_col and hover_name_col in dff.columns:
        hover_text = dff[hover_name_col].astype(str)

    customdata_cols = [c for c in extra_hover_cols if c in dff.columns]
    customdata = dff[customdata_cols].to_numpy() if customdata_cols else None

    hovertemplate_parts = []
    if hover_name_col and hover_name_col in dff.columns:
        hovertemplate_parts.append("<b>%{text}</b>")
    LABELS = {
        "total_trips": "Rideshare trips",
        "annual_total": "CTA rides",
    }

    label = LABELS.get(size_col, size_col)

    hovertemplate_parts.append(f"{label}: %{{marker.size:,}}")

    hovertemplate = "<br>".join(hovertemplate_parts) + "<extra></extra>"

    fig.add_trace(
        go.Scattermapbox(
            lat = dff[lat_col],
            lon = dff[lon_col],
            mode = "markers",
            name = name,
            text = hover_text,
            customdata = customdata,
            hovertemplate = hovertemplate,
            marker = dict(
                size = dff[size_col],
                sizemode = "area",
                sizeref = _sizeref(dff[size_col], desired_max_px = max_marker_px),
                sizemin = 4,
                opacity = 0.75,
                color = color,
            ),
        )
    )
    return fig


def add_selected_overlays(
    fig,
    overlays,
    *,
    cta_df = None,
    rideshare_df = None,
    cta_lat_col = "lat",
    cta_lon_col = "lon",
    cta_size_col = "annual_total",
    cta_name_col = "station_name",
    rideshare_lat_col = "centroid_lat",
    rideshare_lon_col = "centroid_lon",
    rideshare_size_col = "total_trips",
    rideshare_name_col = "community_area_name",
    cta_max_marker_px = 26,
    rideshare_max_marker_px = 34,
):
    overlays = set(overlays or [])

    if "cta" in overlays and cta_df is not None and not cta_df.empty:
        fig = add_point_overlay(
            fig,
            cta_df,
            lat_col = cta_lat_col,
            lon_col = cta_lon_col,
            size_col = cta_size_col,
            name = "CTA stations",
            hover_name_col = cta_name_col,
            extra_hover_cols = [cta_size_col],
            max_marker_px = cta_max_marker_px,
            color = "#d62728",
        )

    if "rideshare" in overlays and rideshare_df is not None and not rideshare_df.empty:
        fig = add_point_overlay(
            fig,
            rideshare_df,
            lat_col = rideshare_lat_col,
            lon_col = rideshare_lon_col,
            size_col = rideshare_size_col,
            name = "Rideshare totals",
            hover_name_col = rideshare_name_col,
            extra_hover_cols = [rideshare_size_col],
            max_marker_px = rideshare_max_marker_px,
            color = "#111111",
        )

    return fig
