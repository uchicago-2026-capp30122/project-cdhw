import networkx as nx
from project_cdhw.visuals.network_analysis import comm_area_totals, top_least_neighbors


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
            nodes[node] = {"ca_num": int(ride["pickup_community_area"])}
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
        top, least = top_least_neighbors(ride_nx, node, 5)

        # Convert dictionary outputs to strings so they can be easily
        # added to node title
        top_str = ""
        for area in top:
            top_str += f"{area['neighbor'].title()} ({area['total_rides']:,})\n"

        least_str = ""
        for area in least:
            least_str += f"{area['neighbor'].title()} ({area['total_rides']:,})\n"

        # Add nodes with data
        ride_nx.add_node(
            node,
            label=node,
            ca_num=data["ca_num"],
            x=data["lon"] * 10000,
            y=data["lat"] * -10000,
            total_trips=incoming + outgoing,
            top_neighbors=top_str,
            least_neighbors=least_str,
        )

        # Add nodes with data
        ride_nx.add_node(
            node,
            label=node,
            ca_num=data["ca_num"],
            x=data["lon"] * 10000,
            y=data["lat"] * -10000,
            total_trips=incoming + outgoing,
            top_incoming=top_str,
            top_outgoing=least_str,
        )

    return ride_nx
