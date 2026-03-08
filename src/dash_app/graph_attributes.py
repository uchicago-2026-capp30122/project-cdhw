import networkx as nx
import matplotlib.cm as cm
import matplotlib.colors as mcolors


def update_ca_data_colors_size(ride_nx, ca_csv):
    """
    This function serves two purposes:
        1. To update the community area census csv with
        a column for total trips, which is calculated when making the ride_nx graph.
        2. To pull in census data to be used as color (transportation need index) and
        size (population for trips per capita) values

        Inputs:
    """
    node_trips = nx.get_node_attributes(ride_nx, "total_trips")
    node_ids = nx.get_node_attributes(ride_nx, "ca_num")

    nodes = {id: node_trips[name] for name, id in node_ids.items()}

    ca_csv["total_trips"] = ca_csv["community_area"].map(nodes)

    t_index_lookup = dict(
        zip(ca_csv["community_area"], ca_csv["transportation_need_index_0_100"])
    )

    color_values = list(t_index_lookup.values())

    norm = mcolors.Normalize(vmin=min(color_values), vmax=max(color_values))
    cmap = cm.get_cmap("viridis_r")

    color_lookup = {}

    for node, val in t_index_lookup.items():
        rgba = cmap(norm(val))
        color_lookup[node] = mcolors.to_hex(rgba)

    pop_lookup = dict(zip(ca_csv["community_area"], ca_csv["pop_total"]))

    # # commented out, b/c it was overwriting the community_area_census.csv and erasing the values under total_trips
    # ca_csv.to_csv('data/processed/community_area_census.csv', index = False)

    return color_lookup, pop_lookup
