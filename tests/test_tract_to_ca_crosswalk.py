"""
Purpose: Validate the reconciliation output is sane.

Tests:
- Columns exist: GEOID, community_area, weight
- All weights are > 0 and <= 1
- For a sample of GEOIDs, sum of weights ≈ 1.0 (tolerance like 0.98–1.02)
- community_area values in 1–77

If crosswalk script is slow, don’t recompute crosswalk in tests;
just test the existing data/processed/tract_to_ca_crosswalk.csv.
"""
