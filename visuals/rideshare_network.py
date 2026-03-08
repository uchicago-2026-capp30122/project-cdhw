from pyvis.network import Network
import networkx as nx
import json
import webbrowser
import os
from pathlib import Path
import pandas as pd
import matplotlib.cm as cm
import matplotlib.colors as mcolors
from visuals.network_analysis import comm_area_totals, get_top_incoming, get_top_outgoing
from src.dash_app.config import RIDESHARE_COMMUNITY_JSON, CA_CSV
from src.dash_app.io import load_df

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
            
            #Create dictionary to store nodes 
            nodes = {}

            for ride in ride_data:
                #node = ride['pickup_name']
                node = ride['pickup_community_area']
                if node not in nodes:
                    nodes[node] = {'Community Area': node}
                    nodes[node]['name'] = ride['pickup_name']
                    #nodes[node]['ca_num'] = int(ride['pickup_community_area'])
                    nodes[node]['lat'] = ride['pickup_lat']
                    nodes[node]['lon'] = ride['pickup_lon']
                #nodes[node]['total_trips'] = nodes[node].get('total_trips', 0) + int(ride['trips'])
                #city_rides += int(ride['trips'])
                ride_nx.add_edge(ride['pickup_community_area'], ride['dropoff_community_area'],
                                trips = int(ride['trips']), 
                                weight = (int(ride['trips'])/10000))

            for node, data in nodes.items():
                incoming = comm_area_totals(ride_nx, node)['total_incoming']
                outgoing = comm_area_totals(ride_nx, node)['total_outgoing']
                top_inc = get_top_incoming(ride_nx, node, 5) 
                top_out = get_top_outgoing(ride_nx, node, 5)

                top_inc_str = ""
                for area, percent in top_inc:
                    top_inc_str += f"{area}: {percent:.1%}\n"

                top_out_str = ""
                for area, percent in top_out:
                    top_out_str += f"{area}: {percent:.1%}\n"
                
                ride_nx.add_node(node, 
                                label = data['name'],
                                x = data['lon'] * 10000,
                                y = data['lat'] * -10000,
                                total_trips = incoming + outgoing,
                                size = (incoming + outgoing)/100000,
                                title = (f"""{data['name']} 
                                Total Incoming Trips: {str(incoming)} 
                                Total Outgoing Trips: {str(outgoing)}  
                                Top Incoming Areas: 
                                {top_inc_str} 
                                Top Outgoing Areas: 
                                {top_out_str}
                                """)
                )

    return ride_nx

def update_ca_data_colors(ride_nx):
    ca_csv = load_df(CA_CSV, id_col="community_area")

    nodes = nx.get_node_attributes(ride_nx, 'total_trips')

    ca_csv['total_trips'] = ca_csv['community_area'].map(nodes)

    t_index_lookup = dict(zip(ca_csv['community_area'], ca_csv['transportation_need_index_0_100']))

    color_values = list(t_index_lookup.values())

    norm = mcolors.Normalize(vmin = min(color_values), vmax = max(color_values))
    cmap = cm.get_cmap('viridis')

    color_lookup = {}

    for node, val in t_index_lookup.items():
        rgba = cmap(norm(val))
        color_lookup[node] = mcolors.to_hex(rgba)

    ca_csv.to_csv('data/processed/community_area_census.csv', index = False)

    return color_lookup

    
def generate_rideshare_html():
    ride_nx = build_rideshare_graph(RIDESHARE_COMMUNITY_JSON)
    node_colors = update_ca_data_colors(ride_nx)

    for node in ride_nx.nodes():
        ride_nx.nodes[node]["color"] = node_colors.get(node, "#cccccc")

    ride_net = Network(cdn_resources='in_line', height = '100vh', 
                       width = '100%', select_menu=True)
    ride_net.from_nx(ride_nx)


        # color = node_colors.get(node, "#cccccc")
        # ride_net.add_node(node, color = color)
    
    #print(ride_net.nodes)

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