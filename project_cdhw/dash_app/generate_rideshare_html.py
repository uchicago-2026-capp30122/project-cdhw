from project_cdhw.dash_app.config import RIDESHARE_COMMUNITY_JSON
from project_cdhw.process.rideshare_data.rideshare_data_loading import (
    load_rideshare_json,
)
from project_cdhw.dash_app.graph_builder import build_rideshare_graph
from project_cdhw.visuals.graph_vis import make_pyvis
import webbrowser
import os


def generate_html():
    rideshare = load_rideshare_json(RIDESHARE_COMMUNITY_JSON)

    ride_nx = build_rideshare_graph(rideshare)

    ride_net = make_pyvis(ride_nx)

    ride_net.set_options("""
    {
        "physics": {
            "enabled": false
        },
        "nodes": {
            "font":{
                "size": 30
                         }
            },         
        "interaction": {
            "zoomView": true
        },
        "layout": {
            "improvedLayout": false
        }
    }
                         
    """)

    html = ride_net.generate_html()

    # center graph on coordinates of Chicago
    zoom_script = """
        <script>
        setTimeout(function() {
            network.moveTo({
                position: {x: -87.7 * 10000, y: -41.8 * 10000},
                scale: 0.15,
                animation: false
            });
        });
        </script>
        """
    html = html.replace("</body>", zoom_script + "</body>")

    return html


def display_rideshare_network(html):
    with open("network.html", "w") as f:
        f.write(html)

    file_path = os.path.abspath("network.html")

    webbrowser.open("file://" + file_path)
