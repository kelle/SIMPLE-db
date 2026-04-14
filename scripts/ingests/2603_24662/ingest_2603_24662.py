"""Ingest script for arXiv:2603.24662.

Implemented data products:
- publication metadata (DOI, arXiv, bibcode)
- source verification/ingest for the six science targets
- modeled parameters from Table 4 (Lbol, Teff, radius, mass, log g)

Notes:
- The paper does not provide direct archive URLs for each final x1d product in
    the manuscript table. The JWST observation metadata rows are included below,
    and the script logs skipped spectrum rows until URLs are supplied.
"""

from __future__ import annotations

import logging

from astrodb_utils import load_astrodb
from astrodb_utils.instruments import ingest_instrument
from astrodb_utils.publications import find_publication, ingest_publication
from astrodb_utils.spectra import ingest_spectrum
from astrodb_utils.sources import find_source_in_db, ingest_source
from sqlalchemy import and_, select

from simple import REFERENCE_TABLES

LOGGER = logging.getLogger("astrodb_utils.paper_ingest.2603_24662")
LOGGER.setLevel(logging.INFO)

SAVE_DB = False
RECREATE_DB = False
DB_PATH = "SIMPLE.sqlite"
SCHEMA_PATH = "simple/schema.yaml"
PAPER_SLUG = "2603_24662"
REFERENCE = "Lam26"

SOURCE_ROWS = [
    {"source": "2MASS J00470038+6803543", "short": "W0047+68"},
    {"source": "2MASS J03552337+1133437", "short": "2M0355+11"},
    {"source": "2MASS J06420559+4101599", "short": "2M0642+41"},
    {"source": "2MASS J17410280-4642218", "short": "W1741-46"},
    {"source": "2MASSW J2206450-421721", "short": "2M2206-42"},
    {"source": "2MASS J22443167+2043433", "short": "2M2244+20"},
]

# Table 4 from Lam et al. 2026 (arXiv:2603.24662v1), values and uncertainties.
MODELED_PARAM_ROWS = [
    # W0047+68
    {"source": "2MASS J00470038+6803543", "parameter": "L bol", "value": -4.417, "upper_error": 0.018, "lower_error": 0.018, "unit": "dex"},
    {"source": "2MASS J00470038+6803543", "parameter": "T eff", "value": 1281.0, "upper_error": 17.0, "lower_error": 17.0, "unit": "K"},
    {"source": "2MASS J00470038+6803543", "parameter": "radius", "value": 1.22, "upper_error": 0.03, "lower_error": 0.03, "unit": "R_jup"},
    {"source": "2MASS J00470038+6803543", "parameter": "mass", "value": 17.2, "upper_error": 2.1, "lower_error": 2.1, "unit": "M_jup"},
    {"source": "2MASS J00470038+6803543", "parameter": "log g", "value": 4.46, "upper_error": 0.07, "lower_error": 0.08, "unit": "dex"},
    # 2M0355+11
    {"source": "2MASS J03552337+1133437", "parameter": "L bol", "value": -4.072, "upper_error": 0.006, "lower_error": 0.006, "unit": "dex"},
    {"source": "2MASS J03552337+1133437", "parameter": "T eff", "value": 1573.0, "upper_error": 51.0, "lower_error": 51.0, "unit": "K"},
    {"source": "2MASS J03552337+1133437", "parameter": "radius", "value": 1.21, "upper_error": 0.08, "lower_error": 0.08, "unit": "R_jup"},
    {"source": "2MASS J03552337+1133437", "parameter": "mass", "value": 30.3, "upper_error": 6.8, "lower_error": 6.8, "unit": "M_jup"},
    {"source": "2MASS J03552337+1133437", "parameter": "log g", "value": 4.71, "upper_error": 0.17, "lower_error": 0.17, "unit": "dex"},
    # 2M0642+41 (Oceanus age note in paper)
    {"source": "2MASS J06420559+4101599", "parameter": "L bol", "value": -4.687, "upper_error": 0.044, "lower_error": 0.044, "unit": "dex"},
    {"source": "2MASS J06420559+4101599", "parameter": "T eff", "value": 1183.0, "upper_error": 33.0, "lower_error": 33.0, "unit": "K"},
    {"source": "2MASS J06420559+4101599", "parameter": "radius", "value": 1.045, "upper_error": 0.03, "lower_error": 0.03, "unit": "R_jup"},
    {"source": "2MASS J06420559+4101599", "parameter": "mass", "value": 26.7, "upper_error": 2.8, "lower_error": 2.8, "unit": "M_jup"},
    {"source": "2MASS J06420559+4101599", "parameter": "log g", "value": 4.78, "upper_error": 0.06, "lower_error": 0.06, "unit": "dex"},
    # W1741-46
    {"source": "2MASS J17410280-4642218", "parameter": "L bol", "value": -4.201, "upper_error": 0.048, "lower_error": 0.048, "unit": "dex"},
    {"source": "2MASS J17410280-4642218", "parameter": "T eff", "value": 1456.0, "upper_error": 60.0, "lower_error": 60.0, "unit": "K"},
    {"source": "2MASS J17410280-4642218", "parameter": "radius", "value": 1.21, "upper_error": 0.08, "lower_error": 0.08, "unit": "R_jup"},
    {"source": "2MASS J17410280-4642218", "parameter": "mass", "value": 27.2, "upper_error": 6.8, "lower_error": 6.8, "unit": "M_jup"},
    {"source": "2MASS J17410280-4642218", "parameter": "log g", "value": 4.65, "upper_error": 0.18, "lower_error": 0.18, "unit": "dex"},
    # 2M2206-42
    {"source": "2MASSW J2206450-421721", "parameter": "L bol", "value": -3.957, "upper_error": 0.033, "lower_error": 0.033, "unit": "dex"},
    {"source": "2MASSW J2206450-421721", "parameter": "T eff", "value": 1682.0, "upper_error": 57.0, "lower_error": 57.0, "unit": "K"},
    {"source": "2MASSW J2206450-421721", "parameter": "radius", "value": 1.20, "upper_error": 0.07, "lower_error": 0.07, "unit": "R_jup"},
    {"source": "2MASSW J2206450-421721", "parameter": "mass", "value": 33.8, "upper_error": 6.8, "lower_error": 6.8, "unit": "M_jup"},
    {"source": "2MASSW J2206450-421721", "parameter": "log g", "value": 4.75, "upper_error": 0.16, "lower_error": 0.16, "unit": "dex"},
    # 2M2244+20
    {"source": "2MASS J22443167+2043433", "parameter": "L bol", "value": -4.478, "upper_error": 0.015, "lower_error": 0.015, "unit": "dex"},
    {"source": "2MASS J22443167+2043433", "parameter": "T eff", "value": 1245.0, "upper_error": 13.0, "lower_error": 19.0, "unit": "K"},
    {"source": "2MASS J22443167+2043433", "parameter": "radius", "value": 1.21, "upper_error": 0.02, "lower_error": 0.02, "unit": "R_jup"},
    {"source": "2MASS J22443167+2043433", "parameter": "mass", "value": 16.1, "upper_error": 1.5, "lower_error": 1.5, "unit": "M_jup"},
    {"source": "2MASS J22443167+2043433", "parameter": "log g", "value": 4.44, "upper_error": 0.05, "lower_error": 0.06, "unit": "dex"},
]

# Table 3 JWST observation metadata. Populate spectrum_url later with MAST URLs.
SPECTRA_ROWS = [
    {"source": "2MASS J00470038+6803543", "instrument": "MIRI", "mode": "LRS fixed slit", "regime": "mir", "obs_date": "2024-02-09", "spectrum_url": None},
    {"source": "2MASS J00470038+6803543", "instrument": "NIRSpec", "mode": "Prism/CLEAR S200A1", "regime": "nir", "obs_date": "2024-02-09", "spectrum_url": None},
    {"source": "2MASS J03552337+1133437", "instrument": "MIRI", "mode": "LRS fixed slit", "regime": "mir", "obs_date": "2024-02-17", "spectrum_url": None},
    {"source": "2MASS J03552337+1133437", "instrument": "NIRSpec", "mode": "Prism/CLEAR S200A1", "regime": "nir", "obs_date": "2024-02-17", "spectrum_url": None},
    {"source": "2MASS J06420559+4101599", "instrument": "MIRI", "mode": "LRS fixed slit", "regime": "mir", "obs_date": "2024-03-07", "spectrum_url": None},
    {"source": "2MASS J06420559+4101599", "instrument": "NIRSpec", "mode": "Prism/CLEAR S200A1", "regime": "nir", "obs_date": "2024-03-07", "spectrum_url": None},
    {"source": "2MASS J17410280-4642218", "instrument": "MIRI", "mode": "LRS fixed slit", "regime": "mir", "obs_date": "2024-04-05", "spectrum_url": None},
    {"source": "2MASS J17410280-4642218", "instrument": "NIRSpec", "mode": "Prism/CLEAR S200A1", "regime": "nir", "obs_date": "2024-04-05", "spectrum_url": None},
    {"source": "2MASSW J2206450-421721", "instrument": "MIRI", "mode": "LRS fixed slit", "regime": "mir", "obs_date": "2024-06-09", "spectrum_url": None},
    {"source": "2MASSW J2206450-421721", "instrument": "NIRSpec", "mode": "Prism/CLEAR S200A1", "regime": "nir", "obs_date": "2024-06-09", "spectrum_url": None},
    {"source": "2MASS J22443167+2043433", "instrument": "MIRI", "mode": "LRS fixed slit", "regime": "mir", "obs_date": "2024-06-21", "spectrum_url": None},
    {"source": "2MASS J22443167+2043433", "instrument": "NIRSpec", "mode": "Prism/CLEAR S200A1", "regime": "nir", "obs_date": "2024-06-21", "spectrum_url": None},
]


def load_db():
    return load_astrodb(
        DB_PATH,
        recreatedb=RECREATE_DB,
        reference_tables=REFERENCE_TABLES,
        felis_schema=SCHEMA_PATH,
    )


def _canonical_source_name(db, source_name):
    found = find_source_in_db(db, source_name)
    if not found:
        return None
    if isinstance(found, str):
        return found
    if isinstance(found, list) and found and isinstance(found[0], (tuple, list)):
        return found[0][0]
    if isinstance(found, list) and found and isinstance(found[0], str):
        return found[0]
    return source_name


def ensure_publication(db):
    """Publication ingest must run before all dependent table rows."""
    existing = (
        find_publication(db, reference=REFERENCE)
        or find_publication(db, doi="10.48550/arXiv.2603.24662")
        or find_publication(db, bibcode="2026arXiv260324662L")
        or find_publication(db, bibcode="arXiv:2603.24662")
    )
    if existing:
        LOGGER.info("Publication already present for %s; skipping insert", REFERENCE)
        return existing

    return ingest_publication(
        db,
        doi="10.48550/arXiv.2603.24662",
        bibcode="arXiv:2603.24662",
        reference=REFERENCE,
        description=(
            "Clouds with a silicate lining: Using JWST spectra to probe "
            "atmospheric diversity in young AB Dor L dwarfs"
        ),
    )


def ingest_source_rows(db, rows):
    inserted, skipped, failed = 0, 0, 0
    for row in rows:
        source_name = (row.get("source") or "").strip()
        short_name = (row.get("short") or "").strip()
        if not source_name:
            failed += 1
            LOGGER.error("Missing source in row: %s", row)
            continue
        try:
            if find_source_in_db(db, source_name) or (short_name and find_source_in_db(db, short_name)):
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


def ensure_instruments(db):
    ingest_instrument(db, telescope="JWST", instrument="NIRSpec", mode="Prism/CLEAR S200A1")
    ingest_instrument(db, telescope="JWST", instrument="MIRI", mode="LRS fixed slit")


def ingest_spectra_rows(db, rows):
    """Insert spectra rows when archive URLs are available."""
    inserted, skipped, failed = 0, 0, 0
    seen = set()
    for row in rows:
        source_name = (row.get("source") or "").strip()
        instrument = (row.get("instrument") or "").strip()
        regime = (row.get("regime") or "").strip()
        mode = (row.get("mode") or "").strip()
        obs_date = (row.get("obs_date") or "").strip()
        spectrum_url = row.get("spectrum_url")
        key = (
            source_name,
            instrument,
            obs_date,
            REFERENCE,
        )
        if not source_name or not instrument or not regime or not mode:
            failed += 1
            LOGGER.error("Missing required spectrum fields: %s", row)
            continue
        if key in seen:
            skipped += 1
            continue
        seen.add(key)

        db_source = _canonical_source_name(db, source_name)
        if not db_source:
            failed += 1
            LOGGER.error("Cannot ingest spectrum, source not found: %s", source_name)
            continue

        # We require a concrete archive URL (MAST/S3/local) for traceable ingest.
        if not spectrum_url:
            skipped += 1
            LOGGER.info(
                "Skipping spectrum row without URL for %s (%s %s)",
                db_source,
                instrument,
                obs_date,
            )
            continue

        try:
            ingest_spectrum(
                db,
                source=db_source,
                spectrum=spectrum_url,
                regime=regime,
                telescope="JWST",
                instrument=instrument,
                mode=mode,
                obs_date=obs_date,
                reference=REFERENCE,
            )
            inserted += 1
        except Exception:
            failed += 1
            LOGGER.exception("Failed spectrum ingest for %s (%s)", db_source, spectrum_url)
    return inserted, skipped, failed


def ingest_modeled_param_rows(db, rows):
    """Insert Table 4 modeled parameters with duplicate protection."""
    inserted, skipped, failed = 0, 0, 0
    seen = set()
    for row in rows:
        source_name = (row.get("source") or "").strip()
        parameter = (row.get("parameter") or "").strip()
        value = row.get("value")
        key = (
            source_name,
            parameter,
            value,
            REFERENCE,
        )
        if not source_name or not parameter or value is None:
            failed += 1
            LOGGER.error("Missing modeled parameter fields: %s", row)
            continue
        if key in seen:
            skipped += 1
            continue
        seen.add(key)

        db_source = _canonical_source_name(db, source_name)
        if not db_source:
            failed += 1
            LOGGER.error("Cannot ingest modeled parameter, source not found: %s", source_name)
            continue

        try:
            with db.engine.connect() as conn:
                existing = conn.execute(
                    select(db.ModeledParameters).where(
                        and_(
                            db.ModeledParameters.c.source == db_source,
                            db.ModeledParameters.c.parameter == parameter,
                            db.ModeledParameters.c.reference == REFERENCE,
                        )
                    )
                ).first()

                if existing is not None:
                    skipped += 1
                    continue

                upper = row.get("upper_error")
                lower = row.get("lower_error")
                value_error = None
                if upper is not None and lower is not None:
                    try:
                        value_error = max(abs(float(upper)), abs(float(lower)))
                    except Exception:
                        value_error = None
                elif upper is not None:
                    value_error = upper
                elif lower is not None:
                    value_error = lower

                conn.execute(
                    db.ModeledParameters.insert().values(
                        {
                            "source": db_source,
                            "parameter": parameter,
                            "value": value,
                            "value_error": value_error,
                            "unit": row.get("unit"),
                            "reference": REFERENCE,
                            "comments": "Lam et al. 2026, Table 4",
                        }
                    )
                )
                conn.commit()
            inserted += 1
        except Exception:
            failed += 1
            LOGGER.exception(
                "Failed modeled parameter ingest for %s (%s)", db_source, parameter
            )
    return inserted, skipped, failed


def main():
    db = load_db()

    ensure_publication(db)

    ensure_instruments(db)

    s_i, s_s, s_f = ingest_source_rows(db, SOURCE_ROWS)
    sp_i, sp_s, sp_f = ingest_spectra_rows(db, SPECTRA_ROWS)
    m_i, m_s, m_f = ingest_modeled_param_rows(db, MODELED_PARAM_ROWS)

    LOGGER.info(
        "%s summary | sources i/s/f=%d/%d/%d | spectra i/s/f=%d/%d/%d | modeled i/s/f=%d/%d/%d",
        PAPER_SLUG,
        s_i,
        s_s,
        s_f,
        sp_i,
        sp_s,
        sp_f,
        m_i,
        m_s,
        m_f,
    )

    if SAVE_DB:
        db.save_database(directory="data")


if __name__ == "__main__":
    main()
