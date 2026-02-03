# CDHW

## Abstract

Transportation and urban mobility play a central role in how people access social, economic, and civic life. Prior research and policy discussions have linked limited mobility to increased risks of loneliness, social isolation, and estrangement, particularly for populations constrained by income, age, disability, or neighborhood-level infrastructure. When individuals are unable to move easily through their city, opportunities for work, social connection, and community participation can narrow in ways that are unevenly distributed across space and demographics. Understanding how mobility patterns vary by geographic location and population characteristics is therefore a critical step toward identifying which communities may be most vulnerable to the social consequences of low mobility.

Within this context, this project examines changes in urban mobility in Chicago over the last seven years, with particular attention to differences across neighborhoods and demographic groups. Using public transit ridership data, rideshare data, and demographic information from the American Community Survey (ACS), the analysis is guided by three interrelated questions: **(1)** how urban mobility patterns in Chicago evolved from 2019 to 2025, particularly before and after the COVID-19 pandemic; **(2)** whether public transit and rideshare usage exhibit persistent geographic disparities, with certain neighborhoods consistently over- or under-represented in observed mobility; and **(3)** how these spatial patterns of mobility align with neighborhood-level demographic characteristics. The analysis is descriptive and exploratory rather than causal, and does not directly measure loneliness or social isolation, but instead treats mobility as a structural condition that may shape access to social and economic life.

We analyze how public and private transportation usage varies geographically and over time, and assess the extent to which observed mobility patterns differ across neighborhoods and demographic contexts. The project integrates multiple large public datasets and produces visual tools—including maps and network graphs—that allow users to explore trends across space and time. The long-term goal is to provide a clear, data-driven account of how urban mobility in Chicago changed between 2019 and 2025, and to support future research and policy discussions concerning social isolation, mobility inequality, and urban accessibility.

---

## Data Sources

Each dataset serves a different purpose: CTA data captures systemwide public transit usage over time, rideshare data provides neighborhood-level movement patterns, and ACS data supplies demographic context needed to interpret observed mobility patterns.

---

### Data Reconciliation Plan

We will connect the datasets using **time** and **geography**. All three sources include date information, which allows us to group data by year or month. Transportation data will also be grouped into a single geographic unit that we are still deciding on. CTA systemwide data will be used for time trend analysis, while station-level CTA data will be aggregated to geographic units to support spatial analysis and integration with demographic data. Possible options include census tracts, community areas, or Public Use Microdata Areas (PUMAs).

Our planned steps are:
- Group CTA ridership data by time period
- Group rideshare pickup and dropoff locations into the same geographic unit
- Join the transportation data to ACS demographic data using matching geographic identifiers
- Limit all datasets to the same time range, focusing mainly on 2019–2025 where data is available (with ACS data extending through 2024 due to reporting lag)

The final geographic unit will be chosen based on data availability, privacy-related suppression, and interpretability of results. This choice is analytically important, as it affects how mobility patterns are observed, compared, and contextualized across neighborhoods.

---

### Data Source 1: CTA Ridership Data (Systemwide and Station-Level)

- **Source type:** Bulk data downloads and APIs  
- **Primary URLs:**  
  - https://www.transitchicago.com/ridership/  
  - https://data.cityofchicago.org/Transportation/CTA-Ridership-L-Station-Entries-Daily-Totals/  
  - https://data.cityofchicago.org/dataset/CTA-L-Rail-Stations-Shapefile/vmyy-m9qj/about_data  

#### Description

This project uses three complementary CTA ridership datasets. Together, they capture both overall public transit trends and spatial variation in ridership across Chicago.

The first dataset provides **systemwide daily ridership totals** for CTA bus and rail services. It includes daily observations with counts for bus boardings, rail boardings, and total rides. This dataset is used to analyze overall changes in public transit usage over time, particularly before and after the COVID-19 pandemic.

The second dataset contains **daily ‘L’ station entry totals** for each CTA rail station. It includes station identifiers, station names, dates, day types, and daily entry counts. This dataset provides the spatial detail needed to examine how ridership varies across neighborhoods and to support geographic analysis.

The third dataset contains **point data representing the locations of CTA rail stations**, which will be used to support geographic visualization and spatial aggregation of station-level ridership data.

#### Challenges and uncertainty

Systemwide ridership data does not include geographic detail beyond the transit mode, so it cannot be used for neighborhood-level analysis on its own. Station-level data includes spatial structure but is much larger and requires filtering and aggregation to be manageable. Neither dataset captures riders’ home locations, so all geographic analysis is conducted at an aggregate level and reflects usage patterns rather than individual behavior.

#### Records and properties

The systemwide dataset contains approximately 3,600 daily records across the selected analysis window, with fields for date, day type, bus boardings, rail boardings, and total rides.

The station-level dataset contains approximately 1.3 million rows and five main columns: station ID, station name, date, day type, and daily rides. For analysis, the data will be filtered to the years 2019–2025 and aggregated as needed to reduce size.

#### Exploration notes

Initial exploration shows that the systemwide dataset is well suited for analyzing overall ridership trends over time but does not support detailed spatial analysis.

The station-level dataset can be aggregated to neighborhood-level geographic units and provides the spatial detail needed for mapping and comparison across areas. Cleaning and aggregation of this dataset will be completed before it is joined with geographic or demographic data.

---

### Data Source 2: Chicago Rideshare Data

- **Source type:** API  
- **URLs:**  
  - https://data.cityofchicago.org/Transportation/Transportation-Network-Providers-Trips-2025-/6dvr-xwnh/about_data  
  - https://data.cityofchicago.org/Transportation/Transportation-Network-Providers-Trips-2023-2024-/n26f-ihde/about_data  
  - https://data.cityofchicago.org/Transportation/Transportation-Network-Providers-Trips-2018-2022-/m6dm-c72p/about_data  

- **Description:**  
  All trips, from November 2018 to December 2025, reported by Transportation Network Providers (rideshare companies) to the City of Chicago as part of routine reporting required by ordinance.

- **Challenges and uncertainty:**  
  The dataset is very large and requires filtering and aggregation. Census tract identifiers are suppressed for some records, and timestamps are rounded. Not all trips are reported, though coverage is believed to be high.

- **Records and properties:**  
  The full dataset contains tens of millions of rows. For analysis, we will limit the data to selected years and aggregate trips to reduce size. Each record includes time, location, and trip-related fields.

- **Exploration notes:**  
  Initial exploration shows that pickup and dropoff locations can be grouped into neighborhood-level units. Rideshare flows will also be used to construct network visualizations, treating geographic areas as nodes and trips between them as edges. We will begin by prototyping with a snapshot of 2025 data before expanding to additional years.

---

### Data Source 3: American Community Survey (ACS)

- **Source type:** API  
- **URL:**  
  - https://www.census.gov/data/developers/data-sets/acs-5year.html  

- **Challenges and uncertainty:**  
  The main open questions are which geographic level to use and which ACS variables to include, given the large number of available indicators and the need to balance interpretability with coverage.

- **Records and properties:**  
  The number of records depends on the geographic unit chosen. Using Chicago census tracts across 2019–2024 would result in several thousand rows. The number of variables will depend on the final set of indicators selected.

- **Exploration notes:**  
  We plan to use ACS data from 2019–2024 to match the time span and quality of the transportation data. Likely variables include age, disability status, household structure, vehicle access, and income. Final variable selection will be made after further exploration.

---

## Project Plan

### Core Project Components

The project will include:
- Importing data from CTA, rideshare, and ACS sources  
- Cleaning and aggregating each dataset  
- Aligning datasets by geography and time  
- Exploring and summarizing mobility trends over time  
- Building visual outputs, including maps (to show spatial distribution) and network graphs (to represent movement relationships between areas)

---

### Timeline

The team meets weekly on Fridays from 12:30–1:30pm to review progress and coordinate next steps.

**By end of Week 5 (2/7):**
- Decide on the geographic unit used across datasets  
- Finalize the main variables of interest from each source  

**By end of Week 6 (2/14):**
- Wendy will complete import code for ACS data  

**By end of Week 7 (2/21) and Milestone 3 (2/22):**
- Repository organized with an appropriate project structure  
- Initial README draft  
- Project check-in with TAs  
- Hannah will have a working prototype of the rideshare network visualization  
- Wendy will have a draft geospatial visualization  
- David will have an initial version of the data cleaning and reconciliation pipeline  

**By end of Week 9 (3/7):**
- Hannah will complete the final rideshare network visualization using the full dataset  

**Project Fair:** 3/9

---

### Team Responsibilities

- **Wendy:**  
  Clean and prepare ACS data, and build GIS-based maps showing neighborhood-level mobility patterns.

- **David:**  
  Build ERD, clean rideshare data, and handle data reconciliation across all sources.

- **Ciara:**  
  Clean and prepare CTA ridership data, including both systemwide daily totals and station-level ‘L’ entry data, and produce analysis-ready datasets for time trend and spatial analysis.

- **Hannah:**  
  Build network visualizations of rideshare pickup and dropoff patterns using PyVis.
