from pyvis.network import Network
from src.dash_app.config import CA_CSV
from process.rideshare_data.rideshare_data_loading import load_census_csv
from src.dash_app.graph_attributes import update_ca_data_colors_size


def make_pyvis(ride_nx):
    census = load_census_csv(CA_CSV)

    node_colors, pop_lookup = update_ca_data_colors_size(ride_nx, census)
    # print(node_colors)
    for node, data in ride_nx.nodes(data=True):
        pop = int(pop_lookup.get(node, 1000))
        trips = ride_nx.nodes[node].get("total_trips", 0)

        trips_per_capita = trips / pop

        ride_nx.nodes[node]["size"] = trips_per_capita / 100
        ride_nx.nodes[node]["color"] = node_colors.get(int(data["ca_num"]), "#cccccc")

        ride_nx.nodes[node]["title"] = f"""{node} 
                                Total Trips Per Capita: {trips_per_capita}
                                Top Incoming Areas: 
                                {data["top_incoming"]} 
                                Top Outgoing Areas: 
                                {data["top_outgoing"]}
                                """
    # print(ride_nx.nodes(data = True))
    ride_net = Network(
        cdn_resources="in_line", height="100vh", width="100%", select_menu=True
    )

    ride_net.from_nx(ride_nx)

    for edge in ride_net.edges:
        pickup = edge["to"]
        node_color = ride_nx.nodes[pickup]["color"]

        edge["color"] = {"color": "#BCBFC2", "opacity": 0.8, "highlight": node_color}

    return ride_net
