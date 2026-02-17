import os
import requests
import math
from pyvis.network import Network

# --- Configuration ---
TNP_TRIPS_2025 = "6dvr-xwnh"
COMMUNITY_AREAS = "igwz-8jzy"
BASE_URL = f"https://data.cityofchicago.org/api/v3/views/{TNP_TRIPS_2025}/query.json"
APP_TOKEN = os.environ.get("SOCRATA_APP_TOKEN")


headers = {
    "Accept": "application/json"
}

if APP_TOKEN:
    headers["X-App-Token"] = APP_TOKEN
else:
    raise RuntimeError("SOCRATA_APP_TOKEN is not set.")

def set_payload():
    # --- SoQL Query  ---
    soql = """
    SELECT
    pickup_community_area,
    dropoff_community_area,
    count(*) AS trips
    WHERE
    pickup_community_area IS NOT NULL
    AND dropoff_community_area IS NOT NULL
    AND trip_start_timestamp >= '2025-01-01T00:00:00'
    AND trip_start_timestamp <  '2025-01-02T00:00:00'
    GROUP BY
    pickup_community_area,
    dropoff_community_area
    """

    payload = {
        "query": soql,
        "page": {"pageNumber": 1, "pageSize": 10000},
        "includeSynthetic": False
    }

def api_request():
# --- Make API Request ---
    resp = requests.post(BASE_URL, headers=headers, json=payload, timeout=(10, 300))

    if resp.status_code != 200:
        print("Status:", resp.status_code)
        print("Response text:", resp.text)
        resp.raise_for_status()

    out = resp.json()

# --- Handle possible response shapes ---
def extract_rows(out):
    if isinstance(out, list):
        return out
    if isinstance(out, dict):
        for key in ("results", "data", "rows"):
            if key in out and isinstance(out[key], list):
                return out[key]
        return []
    return []

rows = extract_rows(out)
print(f"Rows returned: {len(rows)}")

# --- Build Network ---
ride_net = Network(
    notebook=True,
    cdn_resources="in_line",
    directed=True,
    width="100%",
    height="100vh"
)

for row in rows:
    pickup = int(float(row["pickup_community_area"]))
    dropoff = int(float(row["dropoff_community_area"]))
    trips = int(row["trips"])

    ride_net.add_node(
        pickup,
        label=str(pickup),
        title=f"Chicago Community Area {pickup}"
    )

    ride_net.add_node(
        dropoff,
        label=str(dropoff),
        title=f"Chicago Community Area {dropoff}"
    )

    ride_net.add_edge(
        pickup,
        dropoff,
        arrows="to",
        value=trips,
        title=f"Trips: {trips:,}"
    )

n = 77
radius = 1000
angles = [2 * math.pi * i / n for i in range(n)]
unique_nodes = set(range(1, 78))
for i, node_id in enumerate(sorted(unique_nodes)):
    x = radius * math.cos(angles[i])
    y = radius * math.sin(angles[i])
    ride_net.add_node(node_id, x=x, y=y, physics=False)

ride_net.set_options("""
{
  "physics": { "enabled": false }
}
""")

# --- Save Output ---
file_path = os.path.abspath("rideshare_edges_aggregated.html")
ride_net.write_html(file_path)

print("Saved to:", file_path)
