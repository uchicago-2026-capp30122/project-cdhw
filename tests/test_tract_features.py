"""
Analysis component tests (index construction).

Purpose: Validate the tract-level “transportation need index” + data types.

Tests:
- GEOID is string and 11 characters (zero-padded)
- transport_need_index exists and is within expected range:
- If you store 0–1: 0 <= index <= 1
- If you store 0–100: 0 <= index <= 100
- (maybe) index has non-trivial variation (not all identical)
"""