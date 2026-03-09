"""
Defines page layout w/ HTML.
Handles:
- dropdown for choropleth variables
- 

"""

from dash import dcc, html
from src.dash_app.generate_rideshare_html import generate_html
from .figures import DISPLAY_NAMES

def make_layout(map_vars):
    return html.Div(
        style={"maxWidth": "1100px", "margin": "0 auto", "padding": "16px"},
        
        children=[
            html.H2("Chicago-area Transportation Need Map (MVP)"),
            html.Label("Geography"),
            dcc.RadioItems(
                id="geo-toggle",
                options=[
                    {"label": "Census Tracts", "value": "tract"},
                    {"label": "Community Areas", "value": "ca"},
                ],
                value="tract",
                inline=True,
            ),

            # toggle for overlay (CTA ridership @station lat/lon & rideshare ridership at community area centroid)
            dcc.Checklist(
                id="overlay-toggle",
                options=[
                    {"label": "CTA stations", "value": "cta"},
                    {"label": "Rideshare totals", "value": "rideshare"},
                ],
                value=[],
                inline=True,
            ),
            
            html.Br(),
            html.Label("Variable"),
            dcc.Dropdown(
                id="var-dropdown",
                options=[{"label": DISPLAY_NAMES.get(v, v), "value": v} for v in map_vars],
                value=map_vars[0] if map_vars else None,
                clearable=False,
            ),
            html.Div(
            "Component variables are shown as percentile-based need scores (0-100), relative to other Chicago geographies.",
            style={"fontSize": "16px", "color": "#555", "marginTop": "6px", "marginBottom": "8px"},
            ),
            
            dcc.Graph(id="choropleth", style={"height": "75vh"}),

            # block for network analysis graph
            html.Div([
                html.H1(children = 'Rideshares to and from Chicago community areas (2025)'),

                html.Div([
                    html.Iframe(
                        srcDoc =  generate_html(),
                        style={"width": "100%", "height": "700px", "border": "none"}
                    )
                ])
            ])
        ],
    )
