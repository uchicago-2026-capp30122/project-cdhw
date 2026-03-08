from pyvis.network import Network
import networkx as nx
import json
import webbrowser
import os
from pathlib import Path
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
            
            #Create dictionary to store nodes 
            nodes = {}

            #Iterate through community area pickup and dropoff pairs (each pickup-dropoff 
            #as a 'ride', with total trips from pickpu to dropoff)
            for ride in ride_data:
                node = ride['pickup_name']

                #Store node data in dictionary, with key as community area name
                if node not in nodes:
                    nodes[node] = {'ca_num': ride['pickup_community_area']}
                    nodes[node]['lat'] = ride['pickup_lat']
                    nodes[node]['lon'] = ride['pickup_lon']

                #Add edge of ride, with pickup as 'from' and dropoff as 'to'
                ride_nx.add_edge(ride['pickup_name'], ride['dropoff_name'],
                                trips = int(ride['trips']), 
                                weight = (int(ride['trips'])/10000))

            #Nodes are created when edges are added, but we need to assign more 
            #analysis to the node data and officially add them
            for node, data in nodes.items():

                #Functions from network_analysis.py
                comm_area_trips = comm_area_totals(ride_nx, node)
                incoming = comm_area_trips['total_incoming']
                outgoing = comm_area_trips['total_outgoing']
                top_inc = get_top_incoming(ride_nx, node, 5) 
                top_out = get_top_outgoing(ride_nx, node, 5)

                #Convert dictionary outputs to strings so they can be easily
                #added to node title 
                top_inc_str = ""
                for area, percent in top_inc:
                    top_inc_str += f"{area}: {percent:.1%}\n"

                top_out_str = ""
                for area, percent in top_out:
                    top_out_str += f"{area}: {percent:.1%}\n"
                
                #Add nodes with data
                ride_nx.add_node(node, 
                                label = node,
                                ca_num = data['ca_num'],
                                x = data['lon'] * 10000,
                                y = data['lat'] * -10000,
                                total_trips = incoming + outgoing,
                                top_incoming = top_inc_str,
                                top_outgoing = top_out_str)

    return ride_nx

def update_ca_data_colors_size(ride_nx, csv):
    """
    This function serves two purposes: 
        1. To update the community area census csv with
        a column for total trips, which is calculated when making the ride_nx graph.
        2. To pull in census data to be used as color (transportation need index) and
        size (population for trips per capita) values

        Inputs: 
    """
    ca_csv = load_df(CA_CSV, id_col="community_area")

    node_trips = nx.get_node_attributes(ride_nx, 'total_trips')
    node_ids = nx.get_node_attributes(ride_nx, 'ca_num')

    nodes = {id: node_trips[name] for name, id in node_ids.items()}

    ca_csv['total_trips'] = ca_csv['community_area'].map(nodes)

    t_index_lookup = dict(zip(ca_csv['community_area'],
                              ca_csv['transportation_need_index_0_100']))

    color_values = list(t_index_lookup.values())

    norm = mcolors.Normalize(vmin = min(color_values), vmax = max(color_values))
    cmap = cm.get_cmap('viridis_r')

    color_lookup = {}

    for node, val in t_index_lookup.items():
        rgba = cmap(norm(val))
        color_lookup[node] = mcolors.to_hex(rgba)

    pop_lookup = dict(zip(ca_csv['community_area'],ca_csv['pop_total']))

    ca_csv.to_csv('data/processed/community_area_census.csv', index = False)

    return color_lookup, pop_lookup

def make_pyvis():
    ride_nx = build_rideshare_graph(RIDESHARE_COMMUNITY_JSON)
    node_colors, pop_lookup = update_ca_data_colors_size(ride_nx)

    for node, data in ride_nx.nodes(data = True):
        pop = int(pop_lookup.get(node, 1000))
        trips = ride_nx.nodes[node].get("total_trips", 0)

        trips_per_capita = trips/pop

        ride_nx.nodes[node]['size'] = trips_per_capita/100
        ride_nx.nodes[node]["color"] = node_colors.get(data['ca_num'], "#cccccc")

        ride_nx.nodes[node]['title'] = (f"""{node} 
                                Total Trips Per Capita: {trips_per_capita}
                                Top Incoming Areas: 
                                {data['top_incoming']} 
                                Top Outgoing Areas: 
                                {data['top_outgoing']}
                                """)

    ride_net = Network(cdn_resources='in_line', height = '100vh', 
                       width = '100%',select_menu=True)
    
    ride_net.from_nx(ride_nx)

    for edge in ride_net.edges:
        pickup = edge['to']
        node_color = ride_nx.nodes[pickup]['color']

        edge["color"] = {
            "color": "#BCBFC2",
            "opacity": 0.8,
            "highlight": node_color
        }

    return ride_net

def generate_rideshare_html():
    ride_net = make_pyvis()

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