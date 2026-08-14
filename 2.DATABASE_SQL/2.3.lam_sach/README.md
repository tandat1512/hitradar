# Cleaning implementation

The executable SQL cleaning checks and quality gates are the non-empty scripts
in this directory. Date normalization is implemented by the canonical Python
cleaning pipeline in `9.SCRIPTS/clean_raw_to_clean.py`; the former empty
`04_convert_dates.sql` placeholder has been removed.
