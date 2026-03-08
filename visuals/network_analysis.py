def comm_area_totals(graph, comm_area):
    """
    This function will return a dictionary with the number of incoming and outgoing rides 
    associated with the community area selected.

    Parameters:
        graph: NetworkX graph representing community area rideshares
        comm_area (str): Name of the community area

    Returns:
        Dictionary containing total_incoming and total_outgoing for the country
    """
    total_incoming = 0
    total_outgoing = 0

    #Add import value for each country exporting to selected country
    for data in graph.pred[comm_area].values():
        total_incoming += int(data['trips'])

    #Add export value for each country importing from selected country
    for data in graph.succ[comm_area].values():
        total_outgoing += int(data['trips'])

    return {'total_incoming': total_incoming, 'total_outgoing': total_outgoing}

def get_top_incoming(graph, comm_area, n: int) -> list[tuple[str, float]]:
    """
    Find the top n community areas pickups that get dropped off in the given community area.
    This is done by finding the total incoming rides for the given node, then 
    for each community area in the graph, calculating what percentage of the given node's
    total rides come from that community area. 

    Parameters:
        graph: NetworkX graph representing the trade network
        comm_area
        n (int): Number of top community areas to return

    Returns:
        List of tuples (community area, total_rides) 
    """
    comm_area_total_incoming = comm_area_totals(graph, comm_area)['total_incoming']

    incoming = []

    for node in graph.nodes():
        if graph.has_edge(node, comm_area):
            trips = graph.edges[node, comm_area]['trips']
            trip_percentage = trips/comm_area_total_incoming
            incoming.append((node, trip_percentage))

    #Sort community areas by percentage of rides 
    top_incoming = sorted(incoming, key = lambda x: x[1], reverse = True)

    return top_incoming[:n]


def get_top_outgoing(graph, comm_area, n: int) -> list[tuple[str, float]]:
    """
    Find the top n community areas pickups that the given community area takes rides to.
    This is done by finding the total incoming rides for the given node, then 
    for each community area in the graph, calculating what percentage of the given node's
    total rides dropoff in that community area. 

    Parameters:
        graph: NetworkX graph representing the trade network
        comm_area
        n (int): Number of top community areas to return

    Returns:
        List of tuples (community area, total_rides) 
    """
    comm_area_total_outgoing = comm_area_totals(graph, comm_area)['total_outgoing']

    outgoing = []

    for node in graph.nodes():
        if graph.has_edge(comm_area, node):
            trips = graph.edges[comm_area, node]['trips']
            trip_percentage = trips/comm_area_total_outgoing
        else:
            trip_percentage = 0
        outgoing.append((node, trip_percentage))

    #Sort community areas by percentage of rides 
    top_incoming = sorted(outgoing, key = lambda x: x[1], reverse = True)

    return top_incoming[:n]

