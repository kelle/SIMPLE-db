---
name: paper-to-simple-ingest
description: 'Read astronomy journal papers or arXiv articles, determine what new data belongs in the SIMPLE archive, and generate astrodb_utils ingest scripts. Use for publication ingest planning, table-to-schema mapping, and adding new publication-linked records (sources, names, photometry, spectra, astrometry, spectral types, modeled parameters, companions).'
argument-hint: 'Provide paper URL(s), e.g. https://arxiv.org/abs/2603.24663'
---

# Paper To SIMPLE Ingest

## What This Skill Produces
- A publication ingest plan with:
  - publication metadata required for SIMPLE
  - list of new and updated data records to ingest
  - mapping from paper columns to SIMPLE tables/fields
- A runnable ingest script in scripts/ingests/<paper_slug>/ using astrodb_utils.
- For multiple papers, one ingest folder per paper (never merge unrelated papers into one script).
- The script must ingest the publication record before ingesting dependent rows.

## When To Use
- New paper contains data not yet in SIMPLE.
- Existing SIMPLE records need updates from a publication.
- You need a repeatable ingest script tied to one publication.

## Scope
- This skill is workspace-scoped for SIMPLE-db conventions and paths.
- Output locations and checks are specific to this repository.

## Required Inputs
- One or more paper URLs (arXiv, journal landing page, or PDF link).
- If available: DOI and ADS bibcode.
- Preferred output directory name (optional).

## Workflow
1. Parse paper metadata and scope.
- Extract title, authors, year, DOI, bibcode, arXiv ID, and data product types.
- Build a quick inventory of what the paper provides:
  - sources or aliases
  - photometry
  - spectra
  - astrometry
  - spectral types
  - modeled parameters
  - companion records

2. Determine what is new vs already ingested.
- Search existing data and scripts for paper identifiers (DOI/bibcode/arXiv/author-year shorthand).
- If publication already exists in SIMPLE:
  - keep publication ingest idempotent in script
  - only add genuinely missing records.
- If publication does not exist:
  - ensure the script ingests publication metadata first.

3. Build table-to-schema mapping.
- For each paper table/appendix file:
  - map each useful column to SIMPLE table fields
  - document units and conversions
  - define null handling and quality filters.
- Record unresolved columns for user confirmation before final script generation.

4. Choose ingest strategy by data type.
- Source rows: use astrodb_utils source helpers (find before insert).
- Publication row: ingest with astrodb_utils publication helper.
- Measurements (photometry/astrometry/modeled params/spectral types): ingest to appropriate table with publication reference.
- Spectra: ingest instrument metadata first if needed, then spectrum records.
- Companion data: ingest host/companion linkage after source verification.

5. Generate ingest assets.
- Create scripts/ingests/<paper_slug>/.
- Add cleaned input files (CSV/FITS paths if needed).
- Generate ingest script from [template](./assets/ingest_publication_template.py).
- Ensure script supports safe reruns (skip or update logic, no blind duplicates).

6. Validate before handoff.
- Dry-run logic where possible.
- Confirm publication ingest is called.
- Confirm record counts printed by type.
- Confirm output save path is correct and consistent with repo conventions.

7. Apply validation gates.
- Gate 1: Metadata gate.
  - DOI, bibcode, arXiv ID, and SIMPLE reference string are present or explicitly flagged as missing.
- Gate 2: Mapping gate.
  - Every ingested field has source column, units, and conversion/null policy documented.
- Gate 3: Idempotency gate.
  - Rerun behavior is explicit (skip/update); duplicates are prevented.
- Gate 4: Traceability gate.
  - Each inserted row can be traced to publication and source row context.
- Gate 5: Output gate.
  - Script and helper files are placed in scripts/ingests/<paper_slug>/.

## Decision Points
- Missing DOI or bibcode:
  - continue with arXiv metadata and mark publication fields needing confirmation.
- Mixed new and existing sources:
  - prefer match-first logic and ingest only missing records.
- Units differ from SIMPLE conventions:
  - convert explicitly and document conversion in script comments.
- Paper has derived values only (no raw measurements):
  - ingest modeled parameters with clear provenance and method notes.

## Completion Checks
- Publication metadata captured and ingested in script.
- Every ingested row has reference/publication linkage.
- No duplicate-source inserts on rerun.
- Clear summary printed: attempted, inserted, skipped, failed.
- Script path and file naming follow repo style under scripts/ingests/.

## References
- [Data Mapping Checklist](./references/data_mapping_checklist.md)
- [Ingest Script Template](./assets/ingest_publication_template.py)
- [Test Cases](./references/test_cases.md)

## Example Invocation Inputs
- https://arxiv.org/abs/2603.24663
- https://arxiv.org/abs/2603.24662
