"""Ingest scaffold for arXiv:2603.24663.

This is a skill smoke-test script: publication ingest first, then source and
paper-specific measurement products.
"""

from __future__ import annotations

import csv
import logging
from pathlib import Path

from astrodb_utils import load_astrodb
from astrodb_utils.publications import ingest_publication
from astrodb_utils.sources import find_source_in_db, ingest_source

from simple import REFERENCE_TABLES

LOGGER = logging.getLogger("astrodb_utils.paper_ingest.2603_24663")
LOGGER.setLevel(logging.INFO)

SAVE_DB = True
RECREATE_DB = False
DB_PATH = "SIMPLE.sqlite"
SCHEMA_PATH = "simple/schema.yaml"
PAPER_SLUG = "2603_24663"
REFERENCE = "otoole26"


def load_db():
    return load_astrodb(
        DB_PATH,
        recreatedb=RECREATE_DB,
        reference_tables=REFERENCE_TABLES,
        felis_schema=SCHEMA_PATH,
    )


def read_rows(csv_path: Path):
    if not csv_path.exists():
        LOGGER.warning("Input file missing, skipping: %s", csv_path)
        return []
    with csv_path.open(newline="", encoding="utf-8") as handle:
        return list(csv.DictReader(handle))


def ensure_publication(db):
    """Publication ingest must run before all dependent table rows."""
    return ingest_publication(
        db,
        doi="10.48550/arXiv.2603.24663",
        bibcode="arXiv:2603.24663",
        arxiv="2603.24663",
    )


def ingest_sources_if_missing(db, rows):
    inserted, skipped, failed = 0, 0, 0
    for row in rows:
        source_name = (row.get("source") or "").strip()
        if not source_name:
            failed += 1
            LOGGER.error("Missing source in row: %s", row)
            continue
        try:
            if find_source_in_db(db, source_name):
                skipped += 1
                continue
            ingest_source(
                db,
                source=source_name,
                ra=row.get("ra"),
                dec=row.get("dec"),
                reference=REFERENCE,
                raise_error=True,
                search_db=True,
            )
            inserted += 1
        except Exception:
            failed += 1
            LOGGER.exception("Failed source ingest: %s", source_name)
    return inserted, skipped, failed


def ingest_variability_rows(db, rows):
    """Insert spectral/time-series variability metrics from publication tables.

    TODO: Replace this placeholder with the SIMPLE table-specific helper call.
    """
    inserted, skipped, failed = 0, 0, 0
    seen = set()
    for row in rows:
        key = (
            (row.get("source") or "").strip(),
            (row.get("metric") or "").strip(),
            (row.get("wavelength_um") or "").strip(),
            REFERENCE,
        )
        if not key[0] or not key[1]:
            failed += 1
            LOGGER.error("Missing required variability fields: %s", row)
            continue
        if key in seen:
            skipped += 1
            continue
        seen.add(key)

        # Placeholder: mark as skipped to keep reruns deterministic until the
        # final table helper call is selected.
        skipped += 1
    return inserted, skipped, failed


def ingest_modeled_param_rows(db, rows):
    """Insert modeled cloud/spot/aurora fit parameters.

    TODO: Replace this placeholder with modeled-parameter ingest helper calls.
    """
    inserted, skipped, failed = 0, 0, 0
    seen = set()
    for row in rows:
        key = (
            (row.get("source") or "").strip(),
            (row.get("parameter") or "").strip(),
            (row.get("value") or "").strip(),
            REFERENCE,
        )
        if not key[0] or not key[1]:
            failed += 1
            LOGGER.error("Missing modeled parameter fields: %s", row)
            continue
        if key in seen:
            skipped += 1
            continue
        seen.add(key)

        # Placeholder: mark as skipped to keep reruns deterministic until the
        # final table helper call is selected.
        skipped += 1
    return inserted, skipped, failed


def main():
    db = load_db()

    ensure_publication(db)

    base = Path(__file__).parent
    source_rows = read_rows(base / "source_rows.csv")
    variability_rows = read_rows(base / "variability_rows.csv")
    modeled_rows = read_rows(base / "modeled_param_rows.csv")

    s_i, s_s, s_f = ingest_sources_if_missing(db, source_rows)
    v_i, v_s, v_f = ingest_variability_rows(db, variability_rows)
    m_i, m_s, m_f = ingest_modeled_param_rows(db, modeled_rows)

    LOGGER.info(
        "%s summary | sources i/s/f=%d/%d/%d | variability i/s/f=%d/%d/%d | modeled i/s/f=%d/%d/%d",
        PAPER_SLUG,
        s_i,
        s_s,
        s_f,
        v_i,
        v_s,
        v_f,
        m_i,
        m_s,
        m_f,
    )

    if SAVE_DB:
        db.save_database(directory="data")


if __name__ == "__main__":
    main()
