import os
import math
import sys
from pyvis.network import Network

# Ensure src can be imported if running this script directly
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
from src.api_client import get_community_areas, get_edges_grouped_by_ca, get_population_by_ca

# ----------------------------
# Configuration
# ----------------------------
OUTPUT_HTML = "rideshare_geo_layout.html"

# Edge styling
MIN_TRIPS = 25
EDGE_WIDTH_SCALE = 0.5

# Node styling
MIN_NODE_SIZE = 3
MAX_NODE_SIZE = 25

# VisJS Layout Config
CANVAS_W = 1600
CANVAS_H = 1000
CANVAS_PAD = 80

# Date filter
DATE_START = "2025-01-01T00:00:00"
DATE_END   = "2025-01-02T00:00:00"

# Areas to exclude from visualization
EXCLUDED_AREAS = [76]  # O'Hare

def lonlat_to_xy(areas, width=CANVAS_W, height=CANVAS_H, padding=CANVAS_PAD):
    """
    Maps geographic coordinates (lon/lat) to canvas x/y coordinates.
    Centers the result around (0,0) for the VisJS camera.
    """
    lons = [a["lon"] for a in areas.values()]
    lats = [a["lat"] for a in areas.values()]
    min_lon, max_lon = min(lons), max(lons)
    min_lat, max_lat = min(lats), max(lats)

    pos = {}
    for ca_id, a in areas.items():
        lon, lat = a["lon"], a["lat"]
        
        # Map to [0, width] / [0, height]
        x_raw = padding + (lon - min_lon) / (max_lon - min_lon) * (width - 2 * padding)
        y_raw = padding + (max_lat - lat) / (max_lat - min_lat) * (height - 2 * padding)
        
        # Shift to center around (0,0)
        x = x_raw - (width / 2)
        y = y_raw - (height / 2)
        
        pos[ca_id] = (x, y)
    return pos

# ----------------------------
# Main Execution
# ----------------------------

# 1. Fetch Data
areas = get_community_areas()
area_ids = sorted([ca_id for ca_id in areas.keys() if ca_id not in EXCLUDED_AREAS])
pos = lonlat_to_xy(areas)

raw_rows = get_edges_grouped_by_ca(DATE_START, DATE_END)
pop_map = get_population_by_ca()

# 2. Process Trip Data (Filter Excluded Areas)
rows = []
for r in raw_rows:
    if isinstance(r, dict):
        pickup = int(float(r["pickup_community_area"]))
        dropoff = int(float(r["dropoff_community_area"]))
    else:
        pickup = int(float(r[0]))
        dropoff = int(float(r[1]))
    
    if pickup not in EXCLUDED_AREAS and dropoff not in EXCLUDED_AREAS:
        rows.append(r)

# 3. Calculate Population Stats
pops = [v for v in pop_map.values() if isinstance(v, (int, float))]
if pops:
    MIN_POP, MAX_POP = min(pops), max(pops)
else:
    MIN_POP, MAX_POP = 0, 1

# 4. Calculate Connectivity Scores
trip_counts = {}
for r in rows:
    if isinstance(r, dict):
        pickup = int(float(r["pickup_community_area"]))
        dropoff = int(float(r["dropoff_community_area"]))
        count = int(r["trips"])
    else:
        pickup = int(float(r[0]))
        dropoff = int(float(r[1]))
        count = int(r[2])
    
    trip_counts[pickup] = trip_counts.get(pickup, 0) + count
    trip_counts[dropoff] = trip_counts.get(dropoff, 0) + count

conn_scores = {}
for ca_id in area_ids:
    # Resolve Population
    a = areas[ca_id]
    name = a["name"]
    pop = pop_map.get(name.strip())
    
    # Fallback lookup
    if pop is None and name:
         for k, v in pop_map.items():
            if k.strip().lower() == name.strip().lower():
                pop = v
                break
    
    # Calculate Score
    if pop and pop > 0:
        total = trip_counts.get(ca_id, 0)
        conn_scores[ca_id] = total / pop
    else:
        conn_scores[ca_id] = 0.0

# 5. Determine Score Range for Coloring
scores = [math.log1p(s) for s in conn_scores.values()]
if scores:
    scores.sort()
    # Clip to 10th-90th percentile
    n = len(scores)
    MIN_SCORE = scores[max(0, int(n * 0.10))]
    MAX_SCORE = scores[min(n - 1, int(n * 0.90))]
else:
    MIN_SCORE, MAX_SCORE = 0.0, 1.0

# ----------------------------
# Build Visualization
# ----------------------------
ride_net = Network(
    notebook=True,
    cdn_resources="in_line",
    directed=True,
    width="100%",
    height="100vh",
)

# Disable physics for static geographic layout
ride_net.toggle_physics(False)
ride_net.set_options("""
{
  "edges": {
    "smooth": { "type": "continuous" },
    "arrows": { "to": { "enabled": true, "scaleFactor": 0.6 } }
  },
  "interaction": {
    "hover": true,
    "navigationButtons": true,
    "dragNodes": true
  }
}
""")

# Add Nodes
for ca_id in area_ids:
    a = areas[ca_id]
    x, y = pos[ca_id]
    name = a["name"]
    
    # Determine Population for Size
    pop = pop_map.get(name.strip())  # Simplified lookup (assuming majority match)
    # Re-apply fallback if needed for display accuracy
    if pop is None and name:
         for k, v in pop_map.items():
            if k.strip().lower() == name.strip().lower():
                pop = v
                break

    # Tooltip
    title_lines = [f"{ca_id}: {name}" if name else f"Community Area {ca_id}"]
    if pop:
        title_lines.append(f"Pop: {pop:,}")
    score = conn_scores.get(ca_id, 0.0)
    title_lines.append(f"Score: {score:.4f}")
    title = "\n".join(title_lines)

    # Size Calculation
    size = MIN_NODE_SIZE
    if pop is not None and MAX_POP > MIN_POP:
        pct = (pop - MIN_POP) / (MAX_POP - MIN_POP)
        size = MIN_NODE_SIZE + pct * (MAX_NODE_SIZE - MIN_NODE_SIZE)

    # Color Calculation
    log_score = math.log1p(score)
    log_score = max(MIN_SCORE, min(MAX_SCORE, log_score)) # Clip
    
    if MAX_SCORE > MIN_SCORE:
        ratio = (log_score - MIN_SCORE) / (MAX_SCORE - MIN_SCORE)
    else:
        ratio = 0.0
    
    # Pastel Blue (Low) -> Pastel Red (High)
    start_r, start_g, start_b = (174, 198, 207)
    end_r, end_g, end_b = (255, 105, 97)
    
    r_val = int(start_r + ratio * (end_r - start_r))
    g_val = int(start_g + ratio * (end_g - start_g))
    b_val = int(start_b + ratio * (end_b - start_b))
    color_hex = f"#{r_val:02x}{g_val:02x}{b_val:02x}"

    ride_net.add_node(
        ca_id,
        label=str(ca_id),
        title=title,
        x=x,
        y=y,
        physics=False,
        size=size,
        color=color_hex
    )

# Add Edges
for r in rows:
    if isinstance(r, dict):
        pickup = int(float(r["pickup_community_area"]))
        dropoff = int(float(r["dropoff_community_area"]))
        trips = int(r["trips"])
    else:
        pickup = int(float(r[0]))
        dropoff = int(float(r[1]))
        trips = int(r[2])

    if trips < MIN_TRIPS:
        continue
    
    if pickup not in area_ids or dropoff not in area_ids:
        continue

    width = max(1.0, math.log1p(trips) * EDGE_WIDTH_SCALE)

    ride_net.add_edge(
        pickup,
        dropoff,
        arrows="to",
        value=trips,
        width=width,
        title=f"Trips: {trips:,}",
        color={
            "color": "rgba(0, 0, 0, 0.1)",        # Default faint black
            "hover": "rgba(0, 0, 0, 0.25)",       # Hover slightly darker
            "highlight": "rgba(0, 0, 0, 0.5)",    # Selected darker
            "inherit": False
        }
    )

file_path = os.path.abspath(OUTPUT_HTML)
ride_net.write_html(file_path)
print("Saved:", file_path)
