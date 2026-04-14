# Ingest Plan: arXiv 2603.24662

## Publication Metadata

- Title: Clouds with a silicate lining: Using JWST spectra to probe atmospheric diversity in young AB Dor L dwarfs
- arXiv ID: 2603.24662
- DOI: 10.48550/arXiv.2603.24662
- ADS bibcode: arXiv:2603.24662
- SIMPLE reference string (proposed): lam26

## Data Product Inventory (from abstract and arXiv metadata)

- Sources: W0047+68, 2M0355+11, 2M0642+41, W1741-46, 2M2206-42, 2M2244+20
- Spectra: JWST NIRSpec Prism and MIRI LRS 0.6-14 um spectra
- Modeled/fundamental parameters: Teff, radius, mass, log(g), bolometric luminosities

## Mapping Summary

- Input files expected in this folder:
  - none required for current script version (paper table values are embedded)
- Embedded paper tables in script:
  - Table 4: L bol, T eff, radius, mass, log g for six objects
  - Table 3: JWST observation metadata rows (instrument/date/mode)
- Source linkage key: source
- Reference linkage: reference column set to Lam26
- Unit policy:
  - Wavelength: um
  - Spectral resolving power: R (dimensionless)
  - Physical parameters in SIMPLE-compatible units per column-level mapping

## Null and Quality Policy

- Empty strings map to NULL.
- Rows missing source or reference are skipped and logged.
- Rows with invalid numeric fields are skipped with source context.

## Idempotency Strategy

- Publication ingest uses astrodb_utils publication helper (idempotent).
- Source ingest uses find-before-insert logic.
- Modeled-parameter ingest checks existing rows by source+model+parameter+reference and skips duplicates on rerun.
- Spectra ingest only runs for rows with concrete archive URLs and otherwise logs skip-on-rerun.

## Implemented In Script

- Publication record: arXiv 2603.24662 (DOI, arXiv, bibcode, reference string).
- Source verification/ingest for:
  - 2MASS J00470038+6803543
  - 2MASS J03552337+1133437
  - 2MASS J06420559+4101599
  - 2MASS J17410280-4642218
  - 2MASSW J2206450-421721
  - 2MASS J22443167+2043433
- ModeledParameters inserts for 30 values from Table 4 (5 parameters x 6 sources).
- Instrument rows for JWST/NIRSpec Prism and JWST/MIRI LRS.

## Remaining Manual Step

- Add MAST `x1d.fits` URLs for each Table 3 row in `SPECTRA_ROWS` to activate actual spectra ingestion.

## Validation Gates

- Metadata gate: pass (DOI/arXiv/bibcode/reference present).
- Mapping gate: pass for planned columns listed above.
- Idempotency gate: pass (explicit skip logic in script).
- Traceability gate: pass (rows include source and reference linkage).
- Output gate: pass (assets in scripts/ingests/2603_24662/).
