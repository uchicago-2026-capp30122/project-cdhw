from pyvis.network import Network
import networkx as nx
import json
import webbrowser
import os
from pathlib import Path
from visuals.network_analysis import comm_area_totals, get_top_incoming, get_top_outgoing

RIDESHARE_COMMUNITY_JSON = Path(__file__).parent.parent/'data/processed/rideshare_community_areas.json'

def build_rideshare_graph(path: Path): 
    """
    Create NetworkX graph using rideshare and community area data

    Inputs: JSON file with rides to and from Chicago community areas, including
    total trips between community areas

    Output: ride_nx: Digraph
    """
    ride_nx = nx.DiGraph()

    with open(path) as f:
            ride_data = json.load(f)

            #city_rides = sum(int(ride['trips']) for ride in ride_data)
            # print(city_rides)
            
            #Create dictionary to store nodes 
            nodes = {}

            for ride in ride_data:
                node = ride['pickup_name']
                if node not in nodes:
                    nodes[node] = {'Community Area': node}
                    nodes[node]['lat'] = ride['pickup_lat']
                    nodes[node]['lon'] = ride['pickup_lon']
                nodes[node]['total_trips'] = nodes[node].get('total_trips', 0) + int(ride['trips'])
                #city_rides += int(ride['trips'])
                ride_nx.add_edge(ride['pickup_name'], ride['dropoff_name'],
                                trips = int(ride['trips']), 
                                weight = (int(ride['trips'])/10000))
                
            for node, data in nodes.items():
                incoming = str(comm_area_totals(ride_nx, node)['total_incoming'])
                outgoing = str(comm_area_totals(ride_nx, node)['total_outgoing'])
                top_inc = get_top_incoming(ride_nx, node, 5) 
                top_out = get_top_outgoing(ride_nx, node, 5)

                top_inc_str = ""
                for area, percent in top_inc:
                    top_inc_str += f"{area}: {percent:.1%}\n"

                top_out_str = ""
                for area, percent in top_out:
                    top_out_str += f"{area}: {percent:.1%}\n"
                
                ride_nx.add_node(node, 
                                label = node,
                                x = data['lon'] * 10000,
                                y = data['lat'] * -10000,
                                size = data['total_trips']/100000,
                                title = (f"""{node} 
                                Total Incoming Trips: {incoming} 
                                Total Outgoing Trips: {outgoing}  
                                Top Incoming Areas: 
                                {top_inc_str} 
                                Top Outgoing Areas: 
                                {top_out_str}
                                """)
                )

    return ride_nx

def generate_rideshare_html():
    ride_nx = build_rideshare_graph(RIDESHARE_COMMUNITY_JSON)

    ride_net = Network(cdn_resources='in_line', height = '100vh', 
                       width = '100%', select_menu=True)
    ride_net.from_nx(ride_nx)

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
        "edges": {
            "color": {
                "color": "#BCBFC2",
                "opacity": 0.8,
                "highlight": "#FF0000" 
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
    
    #center graph on coordinates of Chicago
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