"""Template ingest script for a single publication in SIMPLE.

Copy this into scripts/ingests/<paper_slug>/ and replace TODOs.
"""

from pathlib import Path
import logging

from astrodb_utils import load_astrodb
from astrodb_utils.publications import ingest_publication
from astrodb_utils.sources import find_source_in_db, ingest_source

from simple import REFERENCE_TABLES

LOGGER = logging.getLogger("astrodb_utils.paper_ingest")
LOGGER.setLevel(logging.INFO)

SAVE_DB = True
RECREATE_DB = False
DB_PATH = "SIMPLE.sqlite"
SCHEMA_PATH = "simple/schema.yaml"
PAPER_SLUG = "todo_paper_slug"


def load_db():
    return load_astrodb(
        DB_PATH,
        recreatedb=RECREATE_DB,
        reference_tables=REFERENCE_TABLES,
        felis_schema=SCHEMA_PATH,
    )


def ensure_publication(db):
    """Ingest publication metadata first so downstream records can reference it."""
    # TODO: Replace these fields with verified metadata.
    doi = "TODO_DOI"
    bibcode = "TODO_BIBCODE"
    arxiv = "TODO_ARXIV_ID"

    # Keep this idempotent: astrodb_utils handles existing publications.
    return ingest_publication(db, doi=doi, bibcode=bibcode, arxiv=arxiv)


def ingest_sources(db, rows):
    inserted, skipped, failed = 0, 0, 0

    for row in rows:
        source_name = row["source"]
        reference = row["reference"]

        try:
            existing = find_source_in_db(db, source_name)
            if existing:
                skipped += 1
                continue

            ingest_source(
                db,
                source=source_name,
                ra=row.get("ra"),
                dec=row.get("dec"),
                reference=reference,
                raise_error=True,
                search_db=True,
            )
            inserted += 1
        except Exception:
            failed += 1
            LOGGER.exception("Failed to ingest source: %s", source_name)

    return inserted, skipped, failed


def main():
    db = load_db()

    ensure_publication(db)

    # TODO: Replace with parsed table rows from publication data files.
    source_rows = []

    inserted, skipped, failed = ingest_sources(db, source_rows)
    LOGGER.info(
        "Ingest summary for %s: inserted=%d skipped=%d failed=%d",
        PAPER_SLUG,
        inserted,
        skipped,
        failed,
    )

    if SAVE_DB:
        output_dir = Path("data")
        db.save_database(directory=str(output_dir))


if __name__ == "__main__":
    main()
