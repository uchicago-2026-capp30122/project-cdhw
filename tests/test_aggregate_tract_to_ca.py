"""
Purpose: Validate the aggregation logic is consistent.

Two testing approaches:
A) Fast “file-based” sanity tests
- community_area_census.csv has 77 rows
- Key columns exist
- Aggregated percentages are in [0, 1] (or [0,100] depending on your convention)
- pop_total is positive

B) Small “toy example” unit test (if time)
- Create a tiny DataFrame with 2 tracts and a crosswalk splitting one tract across 2 CAs
- Verify weighted sums/means match hand-calculated results
"""
