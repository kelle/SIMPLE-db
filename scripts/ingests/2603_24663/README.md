# Ingest Plan: arXiv 2603.24663

## Publication Metadata
- Title: Disentangling auroral, cloud and magnetic spot driven variability in three early L-dwarfs with HST/WFC3
- arXiv ID: 2603.24663
- DOI: 10.48550/arXiv.2603.24663
- ADS bibcode: arXiv:2603.24663
- SIMPLE reference string (proposed): otoole26

## Data Product Inventory (from abstract and arXiv metadata)
- Sources: 2MASS J1721039+334415, 2MASS J00361617+1821104, 2MASS J19064801+4011089
- Spectral variability: wavelength-dependent amplitudes from 1.1-1.67 um
- Time series products: white-light amplitudes and period update (2MASS J1721039+334415)
- Modeled parameters: cloud/aurora/magnetic-spot model-fit outputs

## Mapping Summary
- Input files expected in this folder:
  - source_rows.csv
  - variability_rows.csv
  - modeled_param_rows.csv
- Source linkage key: source
- Reference linkage: reference column set to otoole26
- Unit policy:
  - Wavelength: um (paper already in um)
  - Period: hr (store as hr)
  - Variability amplitudes: percent

## Null and Quality Policy
- Empty strings map to NULL.
- Rows missing source or reference are skipped and logged.
- Rows failing numeric conversion are skipped with row context.

## Idempotency Strategy
- Publication ingest uses astrodb_utils publication helper (idempotent).
- Source ingest uses find-before-insert logic.
- Measurement ingest uses a deterministic key and skips duplicates in a rerun.

## Validation Gates
- Metadata gate: pass (DOI/arXiv/bibcode/reference present).
- Mapping gate: pass for planned columns listed above.
- Idempotency gate: pass (explicit skip logic in script).
- Traceability gate: pass (rows include source and reference linkage).
- Output gate: pass (assets in scripts/ingests/2603_24663/).
