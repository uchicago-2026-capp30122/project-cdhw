# Data reconciliation and cleaning plan (draft)
Our project uses transportation statistics in Chicago for 2024, across 3 sources of data.

## Chicago Rideshare Data

This data will be used to create the **network visualization graph,** at the **community area level.** Though we originally intended to include tract-level rideshare data as well, we realized that approximately 1/3 of the rideshare data was missing census tract information; specifically, tracts with fewer than 2 rides in a 15-minute window were ommitted for privacy reasons. 

The raw data is 93.5 million rows of rideshare trip data in Chicago from 2024. 

We use the following variables: 
- Pickup Community Area
- Dropoff Community Area


The raw data will be aggregated into three **CSV files:**

- Rows of ordered pairs (A→B is different from B→A) (including self-pairs) of Chicago community areas (5,929 rows).  Each pair will have a single column with the total number of trips described by that pairing (pickup A → dropoff B)
- Rows of each Chicago community area (77 community areas) with 3 columns: total number of pickups in that area, total number of dropoffs in that area, and total number of pickups & dropoffs in that area
- Rows of each census tract (866 census tracts) with 3 columns: total number of pickups in that tract, total number of dropoffs in that tract, and total number of pickups & dropoffs in that tract

We will also derive a **JSON** file (storing edges only, i.e. the number of rides b/w each community area) from the CSVs, which is more compatible in creating the network analysis graph.




## CTA Ridership Data
We are interested in the total number of CTA L-station rides, across the 146 stations, in 2024. These will be included on the geospatial/choropleth map, as points.

We use the following variables: 

- station_id (number)
- stationname (text)
- date (floating timestamp)
- daytype (text)
- rides (number)



## Census data/ACS 5-yr estimates

We use the following variables: 
- Total households with no vehicle available
- Total households
- Median Household Income in the Past 12 Months
- Population w/ a disability (Total)
- Population 65 and older (Total)
- Total Population (for normalizing demographic statistics, from counts to % of population) & weighting aggregations to community areas.

We pull tract-level ACS variables from the Census API, clean and standardize them into a CSV keyed by GEOID, download tract boundary geometry from TIGER, convert it to GeoJSON, and then use Dash/Plotly to match each tract’s GEOID to its polygon and color it by variable. 

We also plan to aggregate the tract-level statistics up to the community area level, via spatial join. Since census tracts don't always fall cleanly within a single community area, for tracts that fall in multiple community areas, we will 

Next, we aggregate tract-level statistics up to community areas using spatial joins, weighted averaged, and area-weighted intersections (if 70% of a tract falls in area 1, then 70% of the tract's statistics will be assigned to area 1 in the community area-level visualization). We will also use an additional community-area GeoJSON for this higher-level visualization.