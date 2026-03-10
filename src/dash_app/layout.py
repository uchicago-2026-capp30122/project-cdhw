"""
Defines single-page, scrollable Dash layout. 
"""

from dash import dcc, html
from src.dash_app.generate_rideshare_html import generate_html
from .figures import DISPLAY_NAMES


PAGE_STYLE = {
    "maxWidth": "1200px",
    "margin": "0 auto",
    "padding": "24px 24px 56px 24px",
    "fontFamily": "Arial, sans-serif",
    "backgroundColor": "#f8f9fb",
}

CARD_STYLE = {
    "backgroundColor": "white",
    "border": "1px solid #e3e7ee",
    "borderRadius": "12px",
    "padding": "22px",
    "marginBottom": "22px",
    "boxShadow": "0 1px 4px rgba(0,0,0,0.06)",
}

SECTION_HEADER_STYLE = {
    "fontSize": "30px",
    "fontWeight": "700",
    "marginBottom": "10px",
    "color": "#1f2a44",
}

SUBSECTION_HEADER_STYLE = {
    "fontSize": "24px",
    "fontWeight": "700",
    "marginTop": "0",
    "marginBottom": "10px",
    "color": "#24324a",
}

BODY_TEXT_STYLE = {
    "fontSize": "15px",
    "lineHeight": "1.7",
    "color": "#42506a",
    "marginBottom": "0",
}

LABEL_STYLE = {
    "fontWeight": "600",
    "marginBottom": "8px",
    "display": "block",
    "color": "#24324a",
}

HELP_TEXT_STYLE = {
    "fontSize": "14px",
    "color": "#6b7280",
    "marginTop": "8px",
    "lineHeight": "1.5",
}

SMALL_SECTION_KICKER = {
    "fontSize": "13px",
    "fontWeight": "700",
    "textTransform": "uppercase",
    "letterSpacing": "0.04em",
    "color": "#5b3cc4",
    "marginBottom": "8px",
}


def make_layout(map_vars):
    return html.Div(
        style=PAGE_STYLE,
        children=[
            # ---------- Hero ----------
            html.Div(
                style=CARD_STYLE,
                children=[
                    html.Div("Project overview", style=SMALL_SECTION_KICKER),
                    html.H1(
                        "Chicago Transportation Need and Mobility Patterns",
                        style={
                            "fontSize": "40px",
                            "fontWeight": "700",
                            "marginTop": "0",
                            "marginBottom": "14px",
                            "color": "#1f2a44",
                        },
                    ),
                    html.P(
                        "This dashboard examines mobility patterns across Chicago in 2024 by combining "
                        "public transit usage, rideshare activity, and neighborhood-level demographic "
                        "characteristics. It is designed to help users explore where transportation-related "
                        "need appears highest and how those patterns relate to CTA access and rideshare movement.",
                        style=BODY_TEXT_STYLE,
                    ),
                ],
            ),

            # ---------- Context ----------
            html.Div(
                style={
                    **CARD_STYLE,
                    "display": "grid",
                    "gridTemplateColumns": "1fr 1fr",
                    "gap": "24px",
                },
                children=[
                    html.Div(
                        children=[
                            html.H3("Why this topic?", style=SUBSECTION_HEADER_STYLE),
                            html.P(
                                "Transportation access shapes access to work, healthcare, education, and daily life. "
                                "Our goal was to document and explore how movement varies across Chicago and how it aligns "
                                "with neighborhood-level characteristics.",
                                style=BODY_TEXT_STYLE,
                            ),
                        ]
                    ),
                    html.Div(
                        children=[
                            html.H3("What the dashboard shows", style=SUBSECTION_HEADER_STYLE),
                            html.P(
                                "The dashboard combines a choropleth map of transportation need with optional overlays for "
                                "CTA station ridership and community-area rideshare totals. It also includes a network graph "
                                "showing rideshare connections between community areas.",
                                style=BODY_TEXT_STYLE,
                            ),
                        ]
                    ),
                ],
            ),

            # ---------- Inputs / sources ----------
            html.Div(
                style=CARD_STYLE,
                children=[
                    html.H3("Data integrated in this project", style=SUBSECTION_HEADER_STYLE),
                    html.Div(
                        style={
                            "display": "grid",
                            "gridTemplateColumns": "repeat(3, 1fr)",
                            "gap": "18px",
                        },
                        children=[
                            html.Div(
                                style={
                                    "backgroundColor": "#f8f9fb",
                                    "border": "1px solid #e6eaf0",
                                    "borderRadius": "10px",
                                    "padding": "16px",
                                },
                                children=[
                                    html.H4("CTA ridership", style={"marginTop": "0", "color": "#24324a"}),
                                    html.P(
                                        "Station-level ridership used to show public transit usage across the city.",
                                        style=BODY_TEXT_STYLE,
                                    ),
                                ],
                            ),
                            html.Div(
                                style={
                                    "backgroundColor": "#f8f9fb",
                                    "border": "1px solid #e6eaf0",
                                    "borderRadius": "10px",
                                    "padding": "16px",
                                },
                                children=[
                                    html.H4("Rideshare trips", style={"marginTop": "0", "color": "#24324a"}),
                                    html.P(
                                        "Community-area rideshare trip totals and connections used for overlays and the network view.",
                                        style=BODY_TEXT_STYLE,
                                    ),
                                ],
                            ),
                            html.Div(
                                style={
                                    "backgroundColor": "#f8f9fb",
                                    "border": "1px solid #e6eaf0",
                                    "borderRadius": "10px",
                                    "padding": "16px",
                                },
                                children=[
                                    html.H4("ACS indicators", style={"marginTop": "0", "color": "#24324a"}),
                                    html.P(
                                        "Neighborhood characteristics aligned to census tracts and community areas for comparison.",
                                        style=BODY_TEXT_STYLE,
                                    ),
                                ],
                            ),
                        ],
                    ),
                ],
            ),

            # ---------- How to use ----------
            html.Div(
                style=CARD_STYLE,
                children=[
                    html.H3("How to use the dashboard", style=SUBSECTION_HEADER_STYLE),
                    html.Ul(
                        [
                            html.Li("Switch between census tracts and community areas to compare patterns at different geographic levels."),
                            html.Li("Choose a need variable to view relative transportation need across Chicago."),
                            html.Li("Turn on CTA stations and rideshare totals to compare the need surface with mobility activity."),
                            html.Li("Scroll down to the rideshare network to inspect movement connections between community areas."),
                            html.Li("Use the methodology section at the end for data sources, workflow, and caveats."),
                        ],
                        style={"lineHeight": "1.9", "color": "#42506a", "marginBottom": "0"},
                    ),
                ],
            ),

            # ---------- Map section ----------
            html.Div(
                style=CARD_STYLE,
                children=[
                    html.Div("Interactive section 1", style=SMALL_SECTION_KICKER),
                    html.H2("Transportation Need Map", style=SECTION_HEADER_STYLE),
                    html.P(
                        "This map compares transportation-related need across Chicago geographies. "
                        "Overlay layers help place those patterns alongside public transit access and rideshare activity.",
                        style=BODY_TEXT_STYLE,
                    ),
                ],
            ),

            html.Div(
                style=CARD_STYLE,
                children=[
                    html.Div(
                        style={
                            "display": "grid",
                            "gridTemplateColumns": "1fr 1fr",
                            "gap": "24px",
                        },
                        children=[
                            html.Div(
                                [
                                    html.Label("Geography", style=LABEL_STYLE),
                                    dcc.RadioItems(
                                        id="geo-toggle",
                                        options=[
                                            {"label": " Census Tracts", "value": "tract"},
                                            {"label": " Community Areas", "value": "ca"},
                                        ],
                                        value="tract",
                                        inline=True,
                                        style={"color": "#24324a"},
                                        inputStyle={"marginRight": "6px", "marginLeft": "8px"},
                                    ),
                                ]
                            ),
                            html.Div(
                                [
                                    html.Label("Overlay layers", style=LABEL_STYLE),
                                    dcc.Checklist(
                                        id="overlay-toggle",
                                        options=[
                                            {"label": " CTA stations", "value": "cta"},
                                            {"label": " Rideshare totals", "value": "rideshare"},
                                        ],
                                        value=[],
                                        inline=True,
                                        style={"color": "#24324a"},
                                        inputStyle={"marginRight": "6px", "marginLeft": "8px"},
                                    ),
                                ]
                            ),
                        ],
                    ),
                    html.Div(
                        style={"marginTop": "20px"},
                        children=[
                            html.Label("Need variable", style=LABEL_STYLE),
                            dcc.Dropdown(
                                id="var-dropdown",
                                options=[{"label": DISPLAY_NAMES.get(v, v), "value": v} for v in map_vars],
                                value=map_vars[0] if map_vars else None,
                                clearable=False,
                                style={"borderRadius": "8px"},
                            ),
                            html.Div(
                                "Component variables are shown as percentile-based need scores from 0 to 100, "
                                "relative to other Chicago geographies. Higher values indicate greater relative need.",
                                style=HELP_TEXT_STYLE,
                            ),
                        ],
                    ),
                ],
            ),

            html.Div(
                style=CARD_STYLE,
                children=[
                    dcc.Graph(
                        id="choropleth",
                        style={"height": "60vh"},
                        config={
                        "displaylogo": False,
                        "scrollZoom": True,
                        }
                    )
                ],
            ),

            html.Div(
                style=CARD_STYLE,
                children=[
                    html.H3("How to interpret the map", style=SUBSECTION_HEADER_STYLE),
                    html.P(
                        "The choropleth uses relative scores rather than raw percentages. "
                        "A higher score means that a tract or community area ranks as having greater "
                        "transportation-related need compared with other Chicago geographies in the dataset. "
                        "CTA station markers reflect annual ridership, while rideshare markers reflect total trips.",
                        style=BODY_TEXT_STYLE,
                    ),
                ],
            ),

            # ---------- Network section ----------
            html.Div(
                style=CARD_STYLE,
                children=[
                    html.Div("Interactive section 2", style=SMALL_SECTION_KICKER),
                    html.H2("Rideshare Flow Network", style=SECTION_HEADER_STYLE),
                    html.P(
                        "This network shows rideshare connections between Chicago community areas. "
                        "Node size reflects total rideshare activity, while node color corresponds to transportation need.",
                        style=BODY_TEXT_STYLE,
                    ),
                ],
            ),

            html.Div(
                style=CARD_STYLE,
                children=[
                    html.Iframe(
                        srcDoc=generate_html(),
                        style={
                            "width": "100%",
                            "height": "760px",
                            "border": "none",
                            "borderRadius": "10px",
                        },
                    )
                ],
            ),

            html.Div(
                style=CARD_STYLE,
                children=[
                    html.H3("How to interpret the network", style=SUBSECTION_HEADER_STYLE),
                    html.P(
                        "The network provides a complementary view of Chicago mobility. "
                        "While the map emphasizes spatial distribution, the network emphasizes connection patterns "
                        "between community areas, helping show where rideshare activity is concentrated and how areas link together.",
                        style=BODY_TEXT_STYLE,
                    ),
                ],
            ),

            # ---------- Methods ----------
            html.Div(
                style=CARD_STYLE,
                children=[
                    html.Div("Methods and context", style=SMALL_SECTION_KICKER),
                    html.H2("Data and Methodology", style=SECTION_HEADER_STYLE),

                    html.H3("Data sources", style=SUBSECTION_HEADER_STYLE),
                    html.Ul(
                        [
                            html.Li("CTA rail ridership data and station locations"),
                            html.Li("Chicago rideshare trip data"),
                            html.Li("American Community Survey demographic indicators"),
                            html.Li("Census tract and community-area spatial boundaries"),
                        ],
                        style={"lineHeight": "1.9", "color": "#42506a"},
                    ),

                    html.H3("Method notes", style=SUBSECTION_HEADER_STYLE),
                    html.Ul(
                        [
                            html.Li("All data are aligned to census tracts and community areas for spatial comparison."),
                            html.Li("Component indicators are transformed into relative need scores."),
                            html.Li("The transportation need index combines multiple transportation-relevant measures."),
                            html.Li("CTA overlays are shown at station coordinates; rideshare overlays are shown at community-area centroids."),
                            html.Li("The rideshare graph summarizes movement between community areas using a PyVis network visualization."),
                        ],
                        style={"lineHeight": "1.9", "color": "#42506a"},
                    ),

                    html.H3("Caveats", style=SUBSECTION_HEADER_STYLE),
                    html.Ul(
                        [
                            html.Li("Percentile-based scores are comparative, not direct percentages."),
                            html.Li("CTA ridership and rideshare totals reflect different mobility systems and are not directly interchangeable."),
                            html.Li("Centroid-based overlays simplify within-area spatial variation."),
                            html.Li("The network graph highlights connection structure rather than geographic precision."),
                        ],
                        style={"lineHeight": "1.9", "color": "#42506a", "marginBottom": "0"},
                    ),
                ],
            ),

            # ---------- Workflow / diagrams ----------
            html.Div(
                style=CARD_STYLE,
                children=[
                    html.Div("Project workflow", style=SMALL_SECTION_KICKER),
                    html.H2("Workflow and Data Pipeline", style=SECTION_HEADER_STYLE),
                    html.P(
                        "These diagrams summarize how the project moves from raw source data to processed datasets and "
                        "then into the Dash dashboard and PyVis network graph.",
                        style=BODY_TEXT_STYLE,
                    ),

                    html.Div(
                        style={
                            "display": "grid",
                            "gridTemplateColumns": "1fr 1fr",
                            "gap": "24px",
                            "marginTop": "20px",
                        },
                        children=[
                            html.Div(
                                children=[
                                    html.H3("Project structure diagram", style=SUBSECTION_HEADER_STYLE),
                                    html.Img(
                                        src="/assets/project_structure_diagram.png",
                                        style={
                                            "width": "100%",
                                            "border": "1px solid #e6eaf0",
                                            "borderRadius": "10px",
                                        },
                                    ),
                                ]
                            ),
                            html.Div(
                                children=[
                                    html.H3("Data flow diagram", style=SUBSECTION_HEADER_STYLE),
                                    html.Img(
                                        src="/assets/data_flow_diagram.png",
                                        style={
                                            "width": "100%",
                                            "border": "1px solid #e6eaf0",
                                            "borderRadius": "10px",
                                        },
                                    ),
                                ]
                            ),
                        ],
                    ),
                ],
            ),
        ],
    )