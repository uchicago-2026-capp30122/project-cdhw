# Project Structure Report

The Chicago mobility project architecture is designed to transform complex, disparate urban transportation data into accessible, interactive visualizations. The workflow is organized into dedicated modules that handle the sequential flow of information. It begins with data acquisition and geographic aggregation from external sources. The resulting standardized dataset is then utilized by a web application for dynamic geospatial mapping, and by a separate visualization module to produce detailed network graphs.

## Data Processing and Aggregation

The data processing module serves as the functional core for the project. It is subdivided into specialized pipelines managing information from the American Community Survey, the Chicago Transit Authority, and the city's Transportation Urban Network Providers portal. 

The processing workflow progresses through three distinct phases:
*   **Data Extraction:** Scripts utilize the `httpx` and `urllib` libraries to execute HTTP GET requests against the external endpoints. Depending on the API, the responses are either parsed from JSON text into native Python dictionaries or read directly as streaming CSV text into `pandas` DataFrames.
*   **Data Cleaning:** Subsequent scripts standardize the retrieved data using `pandas`. This involves imputing missing `NaN` values, managing outliers, and computing derived indicators. For instance, the census cleaning phase algorithmically calculates a composite transportation need index from various underlying neighborhood socioeconomic metrics by computing weighted averages and percentiles across rows.
*   **Geographic Aggregation:** The raw datasets are originally structured around disparate spatial scales, requiring an alignment phase. The processing module utilizes `geopandas` to conduct spatial joins and geometric overlays, aggregating granular census tracts and specific transit Point geometries up to the uniform standard of Chicago's 77 official Community Area polygons. Finally, a single integration script joins these parallel pipelines to output a unified feature dataset as a CSV file for further analytical use.

## Interactive Web Application

The project's primary interface is an interactive web dashboard built using the `dash` framework to visualize the standardized community area data. This module is responsible for the user facing representation of the city's integrated mobility metrics.

The application utilizes interconnected submodules, including application configuration, data retrieval using `pandas`, coordinate plotting via `plotly`, and dynamic layout rendering using `dash` HTML components. The dashboard initializes a local WSGI server environment and parses the processed community area feature dataset. It constructs an interactive choropleth map that ties the socioeconomic indicators, like the calculated transportation need index, directly to the community area GeoJSON shapes, allowing users to query the underlying data structures.

## Visualizations and Network Maps

Operating parallel to the web dashboard, the visualization module is dedicated to generating static, detailed network maps based on the processed dataset. These tools focus specifically on spatial connectivity and movement corridors across the city.

The scripts within this module leverage the `networkx` library to convert the flow of rideshare trips and public transit ridership into interrelated node networks, representing communities as nodes and trips as weighted edges. The nodes and edges are then passed to the `pyvis` library, which renders the complex interactions and outputs standalone HTML files containing interactive JavaScript graphs. This component provides an alternative, non tabular perspective on mobility patterns that supplements the findings presented in the core dashboard.

## Testing

The testing module utilizes the `pytest` framework, ensuring the reliability of the data transformations. The automated tests validate the mathematical and structural logic inherent within the processing pipelines, verify that tracts correctly aggregate to community areas using test DataFrame fixtures, and confirm the integrity of the transportation need index numeric formulas.
