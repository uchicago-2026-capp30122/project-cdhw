"""
For counts (like pop_total): weighted sum
For rates/percent: weighted average by population or households (we can pick a clean rule)
Computes CA-level transport_need_index (percentiles within CAs)

Input
- data/processed/acs5_2024_il_tract_clean.csv
- data/processed/tract_to_ca_crosswalk.csv

Output
- data/processed/community_area_census.csv


"""
