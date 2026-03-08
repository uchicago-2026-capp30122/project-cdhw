"""
Defines page layout w/ HTML.

"""


from dash import dcc, html
from src.dash_app.generate_rideshare_html import generate_html

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

            html.Br(),
            html.Label("Variable"),
            dcc.Dropdown(
                id="var-dropdown",
                options=[{"label": v, "value": v} for v in map_vars],
                value=map_vars[0] if map_vars else None,
                clearable=False,
            ),

            dcc.Graph(id="choropleth", style={"height": "75vh"}),

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