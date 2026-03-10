# Milestone 1 — Project Proposal

## Team Name
**CDHW**

## Members
- Wendy Wang — wendyhtwang@uchicago.edu, Simulation and Data Visualization
- Hannah Barton — hbarton1@uchicago.edu, Simulation and Data Visualization  
- David Houghton — dhoughton@uchicago.edu, Web scraping, data cleaning and reconcilation
- Ciara Staveley-O’Carroll — csoc@uchicago.edu, Web scraping, data cleaning and reconcilation

---

## Abstract

This project explores urban mobility patterns by analyzing public and private transportation usage across major U.S. cities, with an initial focus on Chicago. Using a combination of public transit ridership data and available private transportation datasets, we aim to identify which demographic groups and neighborhoods are over- or under-represented in transportation usage. Our guiding question is whether low observed ridership reflects reduced mobility, substitution toward other transportation modes (such as walking or biking), or structural factors including infrastructure quality and accessibility.

The project will integrate multiple data sources, including city transportation portals, GTFS transit data, and publicly available private transportation records. We plan to build an interactive data tool that visualizes mobility across neighborhoods and over time, allowing users to compare public versus private transportation patterns. While this proposal represents an initial scope that may evolve, the long-term goal is to develop a framework for identifying low-mobility areas and informing discussions around transportation access, equity, and related social outcomes.

---

## Goal

The goal of this project is to better understand **urban mobility and transportation usage** across different demographic groups and neighborhoods.

Key questions include:
- Which demographic groups or zip codes are **over-represented** or **under-represented** in transportation ridership data?
- Does under-representation in ridership indicate lower mobility, or substitution toward other transportation modes?
- How do public and private transportation patterns differ across neighborhoods?
- Should the analysis focus on a single snapshot in time or **longitudinal trends**, depending on data availability?
- How do these patterns compare across cities where comparable data is available (e.g., Chicago versus New York City)?

---

## Data Visualization Ideas

- Time-series visualizations of ridership trends by neighborhood or demographic group  
- Geographic maps of Chicago highlighting relative mobility by zip code or census tract  
- Side-by-side comparisons of public transit and private transportation usage  

---

## Preliminary Data Sources

### Data Source 1: City of Chicago Transportation Data
- **Summary:** Publicly available transportation datasets, including CTA ridership and related infrastructure data  
- **Publisher:** City of Chicago  
- **URLs:**  
  - https://data.cityofchicago.org/browse?category=Transportation  
  - https://www.transitchicago.com/ridership/  
- **Format:** Bulk data downloads and APIs  
- **Challenges:** Demographic linkage may be indirect; ridership does not always map cleanly to residential location, tricky to map on an indivdual basis or understand what path brought the rider here (if we want to 
know if individuals are leaving their home, etc.).

### Data Source 2: GTFS Transit Data
- **Summary:** General Transit Feed Specification (GTFS) data describing transit routes, stops, schedules, and service frequency  
- **Publisher:** Transit agencies (e.g., CTA)  
- **Format:** Structured text files (GTFS feeds)  
- **Notes:** GTFS enables analysis of transit availability and service coverage, which can be compared to observed ridership patterns  

### Potential Additional Sources (Pending Access)
- NORC transportation datasets (access and sharing constraints to be determined)  
- Uber API or other rideshare datasets (may limit open-sourcing of the final project)  
- Public transportation data from other U.S. cities for comparison  
- Demographic data (e.g., Census or ACS) to contextualize observed mobility patterns  

---

## Preliminary Project Plan

Anticipated project components include:
- Data ingestion from multiple public sources  
- Data cleaning, reconciliation, and geographic alignment  
- Exploratory and statistical analysis of mobility patterns  
- Visualization and interactive tool development  

**Tentative task areas:**
- Data ingestion and sourcing  
- Data cleaning and preparation  
- Visualization and tool development  

## Questions for James (many answered in 1/14 meeting)

1. Where does the course stand on the usage of Private Data? 
2. If we are unable to use the private daata, is it acceptable for this project to focus primarily on public transit and GTFS data, rather than incorporating private transportation datasets?
3. Are there recommended geographic units (e.g., zip code, census tract, community area) for urban mobility analysis?
4. Would a visualization- and exploration-focused project meet course expectations, or should we emphasize more formal statistical modeling?
5. Are cross-city comparisons encouraged, or is a single-city deep dive sufficient for this course?


