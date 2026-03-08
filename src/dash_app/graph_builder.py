import networkx as nx
from visuals.network_analysis import (
    comm_area_totals,
    get_top_incoming,
    get_top_outgoing,
)


def build_rideshare_graph(rideshare_data):
    """
    Create NetworkX graph using rideshare and community area data

    Inputs: JSON file with rides to and from Chicago community areas, including
    total trips between community areas

    Output: ride_nx: Digraph
    """
    ride_nx = nx.DiGraph()

    # Create dictionary to store nodes
    nodes = {}

    # Iterate through community area pickup and dropoff pairs (each pickup-dropoff
    # as a 'ride', with total trips from pickpu to dropoff)
    for ride in rideshare_data:
        node = ride["pickup_name"]

        # Store node data in dictionary, with key as community area name
        if node not in nodes:
            nodes[node] = {"ca_num": ride["pickup_community_area"]}
            nodes[node]["lat"] = ride["pickup_lat"]
            nodes[node]["lon"] = ride["pickup_lon"]

        # Add edge of ride, with pickup as 'from' and dropoff as 'to'
        ride_nx.add_edge(
            ride["pickup_name"],
            ride["dropoff_name"],
            trips=int(ride["trips"]),
            weight=(int(ride["trips"]) / 10000),
        )

    # Nodes are created when edges are added, but we need to assign more
    # analysis to the node data and officially add them
    for node, data in nodes.items():
        # Functions from network_analysis.py
        comm_area_trips = comm_area_totals(ride_nx, node)
        incoming = comm_area_trips["total_incoming"]
        outgoing = comm_area_trips["total_outgoing"]
        top_inc = get_top_incoming(ride_nx, node, 5)
        top_out = get_top_outgoing(ride_nx, node, 5)

        # Convert dictionary outputs to strings so they can be easily
        # added to node title
        top_inc_str = ""
        for area, percent in top_inc:
            top_inc_str += f"{area}: {percent:.1%}\n"

        top_out_str = ""
        for area, percent in top_out:
            top_out_str += f"{area}: {percent:.1%}\n"

        # Add nodes with data
        ride_nx.add_node(
            node,
            label=node,
            ca_num=data["ca_num"],
            x=data["lon"] * 10000,
            y=data["lat"] * -10000,
            total_trips=incoming + outgoing,
            top_incoming=top_inc_str,
            top_outgoing=top_out_str,
        )

    return ride_nx
