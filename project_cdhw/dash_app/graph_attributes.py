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

        Inputs: ride_nx: DiGraph of rideshare data
                ca_csv: csv file with census data by community area, including
                transportation need index variable created by the team

        Outputs: tuple(dicts) tuple of dictionaries for node color and size
    """

    # Create lookup from census data for transportation need index
    t_index_lookup = dict(
        zip(ca_csv["community_area"], ca_csv["transportation_need_index_0_100"])
    )

    # Since Pyvis does not automatically color scale, need to assign colors to
    # transportation_needindex
    color_values = list(t_index_lookup.values())

    # Normalize index values and get map for color scale
    norm = mcolors.Normalize(vmin=min(color_values), vmax=max(color_values))
    cmap = cm.get_cmap("viridis_r")

    color_lookup = {}

    # Assign color to node based on transportation need
    for node, val in t_index_lookup.items():
        rgba = cmap(norm(val))
        color_lookup[node] = mcolors.to_hex(rgba)

    # Get population from census data to use as size in PyVis graph
    pop_lookup = dict(zip(ca_csv["community_area"], ca_csv["pop_total"]))

    return color_lookup, pop_lookup
