import pytest
from project_cdhw.dash_app.config import RIDESHARE_COMMUNITY_JSON
from project_cdhw.dash_app.graph_builder import build_rideshare_graph
from project_cdhw.process.rideshare_data.rideshare_data_loading import (
    load_rideshare_json,
)
from project_cdhw.visuals.network_analysis import (
    comm_area_totals,
    top_least_neighbors,
    get_top_incoming,
)


def graph():
    rideshare = load_rideshare_json(RIDESHARE_COMMUNITY_JSON)
    return build_rideshare_graph(rideshare)


def test_nodes():
    g = graph()
    assert len(g.nodes()) == 77, "Expected 77 nodes"
    assert "ROGERS PARK" in g.nodes(), "Expecting Community Area names as nodes"
    assert "EDGEWATER" in g.nodes(), "Expecting Community Area names as nodes"
    assert g.nodes["LOGAN SQUARE"]["ca_num"] == 22
    assert g.nodes["SOUTH SHORE"]["x"] == pytest.approx(-87.57278271472944 * 10000)
    assert g.nodes["GREATER GRAND CROSSING"]["y"] == pytest.approx(
        41.763247073626026 * -10000
    )


def test_edges():
    g = graph()
    assert len(g.edges()) == 5924, "Expected 5924 edges"
    assert "trips" in g["ALBANY PARK"]["ROGERS PARK"], (
        "Expecting trips attribute on edge"
    )
    assert g["NORTH PARK"]["WEST ENGLEWOOD"]["trips"] == 82
    assert g["FOREST GLEN"]["CHICAGO LAWN"]["trips"] == 40


def test_comm_area_totals():
    g = graph()
    stats = comm_area_totals(g, "EDGEWATER")
    assert stats["total_incoming"] == 1168558
    assert stats["total_outgoing"] == 1213010


def test_get_top_incoming():
    g = graph()
    top_incoming = get_top_incoming(g, "WEST TOWN", 3)
    assert len(top_incoming) == 3
    assert top_incoming[0][0] == "NEAR NORTH SIDE"
    assert top_incoming[1][0] == "WEST TOWN"
    assert top_incoming[2][0] == "NEAR WEST SIDE"
    assert top_incoming[0][1] == pytest.approx(0.180021723646157)


def test_most_least_neighbors():
    g = graph()
    most, least = top_least_neighbors(g, "HUMBOLDT PARK", 5)
    assert len(most) == 5
    assert len(least) == 5
    assert most[0]["neighbor"] == "HUMBOLDT PARK"
    assert least[0]["neighbor"] == "MOUNT GREENWOOD"
    assert most[2]["total_rides"] == 137154
