import os
import sys
import math
import pydeck as pdk

# Ensure src can be imported
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
from src.api_client import get_community_areas, get_edges_grouped_by_ca, get_population_by_ca

# ----------------------------
# Configuration
# ----------------------------
OUTPUT_HTML = "rideshare_3d_map.html"
DATE_START = "2025-01-01T00:00:00"
DATE_END   = "2025-01-02T00:00:00"
EXCLUDED_AREAS = [76]  # O'Hare

# Pastel Colors (RGB)
COLOR_LOW_RGB  = [174, 198, 207]  # Pastel Blue
COLOR_HIGH_RGB = [255, 105, 97]   # Pastel Red

# ----------------------------
# Data Processing
# ----------------------------
def get_pastel_color(ratio):
    r = int(COLOR_LOW_RGB[0] + ratio * (COLOR_HIGH_RGB[0] - COLOR_LOW_RGB[0]))
    g = int(COLOR_LOW_RGB[1] + ratio * (COLOR_HIGH_RGB[1] - COLOR_LOW_RGB[1]))
    b = int(COLOR_LOW_RGB[2] + ratio * (COLOR_HIGH_RGB[2] - COLOR_LOW_RGB[2]))
    return [r, g, b, 255]  # RGBA

def main():
    print("Fetching data...")
    areas = get_community_areas()
    raw_rows = get_edges_grouped_by_ca(DATE_START, DATE_END)
    pop_map = get_population_by_ca()
    
    # Filter Areas
    area_ids = sorted([aid for aid in areas.keys() if aid not in EXCLUDED_AREAS])
    
    # Filter Edges
    rows = []
    for r in raw_rows:
        if isinstance(r, dict):
            pickup = int(float(r["pickup_community_area"]))
            dropoff = int(float(r["dropoff_community_area"]))
            trips = int(r["trips"])
        else:
            pickup = int(float(r[0]))
            dropoff = int(float(r[1]))
            trips = int(r[2])
        
        if pickup not in EXCLUDED_AREAS and dropoff not in EXCLUDED_AREAS:
            if trips >= 25: # Min trips filter
                rows.append({"source": pickup, "target": dropoff, "trips": trips})

    # Calculate Scores
    trip_counts = {}
    for r in rows:
        trip_counts[r["source"]] = trip_counts.get(r["source"], 0) + r["trips"]
        trip_counts[r["target"]] = trip_counts.get(r["target"], 0) + r["trips"]

    # Build Node Data
    node_data = []
    conn_scores = {}
    
    for ca_id in area_ids:
        a = areas[ca_id]
        name = a["name"]
        
        # Population Lookup
        pop = pop_map.get(name.strip())
        if pop is None and name:
             for k, v in pop_map.items():
                if k.strip().lower() == name.strip().lower():
                    pop = v
                    break
        
        if pop and pop > 0:
            score = trip_counts.get(ca_id, 0) / pop
        else:
            score = 0.0
        
        conn_scores[ca_id] = score
        
        node_data.append({
            "id": ca_id,
            "name": name,
            "population": pop if pop else 0,
            "coordinates": [a["lon"], a["lat"]], # [lon, lat]
            "score": score
        })

    # Color Scaling (Log + Percentile)
    scores_log = [math.log1p(s["score"]) for s in node_data]
    if scores_log:
        scores_log.sort()
        n = len(scores_log)
        min_log = scores_log[max(0, int(n * 0.10))]
        max_log = scores_log[min(n - 1, int(n * 0.90))]
    else:
        min_log, max_log = 0.0, 1.0

    # Apply Colors and Elevation to Nodes
    for n in node_data:
        log_val = math.log1p(n["score"])
        log_val = max(min_log, min(max_log, log_val))
        
        if max_log > min_log:
            ratio = (log_val - min_log) / (max_log - min_log)
        else:
            ratio = 0.0
            
        n["color"] = get_pastel_color(ratio)
        n["elevation"] = n["score"] * 100 # scaling factor for height
        n["radius"] = 200 + (n["population"] / 200) # scaling for width

    # Build Edge Data
    edge_data = []
    # Helper to find node color
    color_lookup = {n["id"]: n["color"] for n in node_data}
    coord_lookup = {n["id"]: n["coordinates"] for n in node_data}

    for r in rows:
        src, tgt = r["source"], r["target"]
        if src in coord_lookup and tgt in coord_lookup:
            edge_data.append({
                "source": coord_lookup[src],
                "target": coord_lookup[tgt],
                "trips": r["trips"],
                "width": max(1, math.log1p(r["trips"]) * 2),
                "source_color": color_lookup.get(src, [0,0,0,255]),
                "target_color": color_lookup.get(tgt, [0,0,0,255])
            })

    # ----------------------------
    # PyDeck Layers
    # ----------------------------
    
    # 3D Columns (Nodes)
    column_layer = pdk.Layer(
        "ColumnLayer",
        data=node_data,
        get_position="coordinates",
        get_elevation="elevation",
        elevation_scale=1,
        radius=200,
        get_fill_color="color",
        pickable=True,
        auto_highlight=True,
        extruded=True,
    )

    # 3D Arcs (Edges)
    arc_layer = pdk.Layer(
        "ArcLayer",
        data=edge_data,
        get_source_position="source",
        get_target_position="target",
        get_source_color="source_color",
        get_target_color="target_color",
        get_width="width",
        pickable=True,
        auto_highlight=True,
    )

    # View State (Chicago)
    view_state = pdk.ViewState(
        latitude=41.8781,
        longitude=-87.6298,
        zoom=10,
        pitch=45,
        bearing=0
    )

    # Tooltip
    tooltip = {
        "html": "<b>{name}</b><br>Pop: {population}<br>Score: {score:.4f}",
        "style": {"color": "white", "backgroundColor": "#333"}
    }

    # Render
    r = pdk.Deck(
        layers=[column_layer, arc_layer],
        initial_view_state=view_state,
        tooltip=tooltip,
        map_style="mapbox://styles/mapbox/dark-v10" # Dark mode
    )
    
    file_path = os.path.abspath(OUTPUT_HTML)
    r.to_html(file_path)
    print(f"Saved PyDeck map to: {file_path}")

if __name__ == "__main__":
    main()
