from pyvis.network import Network
from src.dash_app.config import CA_CSV
from process.rideshare_data.rideshare_data_loading import load_census_csv
from src.dash_app.graph_attributes import update_ca_data_colors_size


def make_pyvis(ride_nx):
    """
    This function takes the Networkx graph ride_nx and Census data and converts
    it into a PyVis graph for visualization.

    Inputs: ride_nx: DiGraph of rideshare data
            ca_csv: csv file with census data by community area, including
            transportation need index variable created by the team

    Output: ride_net: PyVis.Network class

    """
    census = load_census_csv(CA_CSV)

    node_colors, pop_lookup = update_ca_data_colors_size(ride_nx, census)

    # Update node data with population and color
    for node, data in ride_nx.nodes(data=True):
        pop = int(pop_lookup.get(data["ca_num"], 1000))
        trips = ride_nx.nodes[node].get("total_trips", 0)

        trips_per_capita = trips / pop

        # Node size is a reduced value of trips per capita
        ride_nx.nodes[node]["size"] = trips_per_capita

        # Node color is based off of transportation need index
        ride_nx.nodes[node]["color"] = node_colors.get(int(data["ca_num"]), "#cccccc")

        # Add title to node
        ride_nx.nodes[node]["title"] = f"""{node} 
            Total Trips: {trips:,}
            Total Trips Per Capita: {int(trips_per_capita):,}

            Most Rides To or From:
            {data["top_neighbors"]}
            Least Rides To or From:
            {data["least_neighbors"]}"""

    # Initialize PyVis Network
    ride_net = Network(
        cdn_resources="in_line", height="100vh", width="100%", select_menu=True
    )

    # Import Networkx graph to PyVis graph
    ride_net.from_nx(ride_nx)

    # Change highlight edge color to match node color
    for edge in ride_net.edges:
        pickup = edge["to"]
        node_color = ride_nx.nodes[pickup]["color"]

        edge["color"] = {"color": "#BCBFC2", "opacity": 0.8, "highlight": node_color}

    return ride_net
