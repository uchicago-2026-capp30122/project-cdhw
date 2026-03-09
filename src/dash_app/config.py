# for tract level data & geometries
TRACT_CSV = "data/processed/tract_features.csv"
TRACT_GEOJSON = "data/processed/tracts_chicago.geojson"

# for community area level data & geometries
CA_CSV = "data/processed/community_area_census.csv"
CA_GEOJSON = "data/processed/community_areas.geojson"

RIDESHARE_COMMUNITY_JSON = "data/processed/rideshare_community_areas.json"

# for CTA station points, located by lat/lon, sized by annual ridership.
# if there's a single joined CSV w/ station locations & ridership later, point the overlay loaders to that.
# expected columns for point overlays: lat, lon, annual_ridership, station_name
CTA_CSV = "data/processed/cta_station_monthly_yearly_2024_geo_commarea.csv"

# sizing Points (CTA stations, rideshare)
CTA_MAX_MARKER_PX = 26
RIDESHARE_MAX_MARKER_PX = 34

# Variables in dropdown (works for both census & community area visualization)
DROPDOWN_VARS = [
    "transportation_need_index_0_100",
    "median_hh_income",
    "pct_no_vehicle_hh",
    "pct_disabled",
    "pct_65_plus",
]
