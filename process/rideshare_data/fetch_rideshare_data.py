from src.api_client import get_edges_grouped_by_ca, get_community_areas
import json

def compile_rideshare(start_date = "2025-01-01T00:00:00", end_date = "2025-02-01T00:00:00"):
    """
    Docstring for compile_rideshare
    
    :param start_date: Description
    :param end_date: Description
    """
    rideshare = get_edges_grouped_by_ca(start_date, end_date)

    community_areas = get_community_areas()

    merged = []

    for ride in rideshare:
        pickup_info = community_areas.get(int(ride["pickup_community_area"]))
        dropoff_info = community_areas.get(int(ride["dropoff_community_area"]))

        merged.append({
            **ride,
            "pickup_name": pickup_info["name"] if pickup_info else None,
            "pickup_lat": pickup_info["lat"] if pickup_info else None,
            "pickup_lon": pickup_info["lon"] if pickup_info else None,
            "dropoff_name": dropoff_info["name"] if dropoff_info else None,
            "dropoff_lat": dropoff_info["lat"] if dropoff_info else None,
            "dropoff_lon": dropoff_info["lon"] if dropoff_info else None,
        })

    with open('data/processed/rideshare_community_areas.json', 'w') as f:
        json.dump(merged, f)