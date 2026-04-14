# Data Mapping Checklist

Use this checklist before coding the ingest script.

## Publication Metadata
- DOI
- ADS bibcode
- arXiv ID
- Author-year shorthand used by SIMPLE references

## Data Product Inventory
- Sources and aliases
- Photometry
- Spectra and instruments
- Astrometry
- Spectral types
- Modeled parameters
- Companions

## Column Mapping Requirements
- Source column in paper
- Target SIMPLE table and field
- Units in paper
- Units expected by SIMPLE
- Conversion formula (if needed)
- Null or upper-limit handling
- Quality flags and exclusion rules

## Integrity Checks
- Reference linkage present for each ingest row
- Duplicate protection on rerun
- Inserted and skipped row counts printed
- Failure logs include source identifier and row context
