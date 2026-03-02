"""
- Left-joins whatever exists (so it won’t break if CTA isn’t ready)
- Produces a single CA table for the choropleth + hover data

joining the clean datasets into:
1. tract-level dataset (probably contains Census demographic data only)
2. community-area level dataset, containing:
    - aggregated Census demographic data, 
    - CTA L & bus line data, 
    - rideshare data,
    - walkability index
    
Input:
- data/processed/community_area_census.csv
- (later) data/processed/cta_ca_totals.csv
- (later) data/processed/rideshare_ca_totals.csv

Output:
- data/processed/community_area_features.csv



    
"""