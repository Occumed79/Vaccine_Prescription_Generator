from __future__ import annotations

import csv
import io
import json
import os
import tarfile
from pathlib import Path
from typing import Any

import psycopg
from psycopg.rows import dict_row


SEED_VERSION = "who-2026-09-20-v1"
SEED_DIR = Path(__file__).resolve().parent / "data" / "who_seed"
SEED_PART_PREFIX = "who_seed_bundle.tar.gz.part"


TABLE_SPECS: dict[str, dict[str, Any]] = {
    "who_vaccine_schedule_adult": {
        "file": "who_vaccine_schedule_adult.csv",
        "columns": [
            "iso_3_code", "countryname", "who_region", "year", "vaccinecode",
            "vaccine_description", "schedulerounds", "targetpop",
            "targetpop_description", "geoarea", "ageadministered",
            "sourcecomment", "source_file",
        ],
        "ddl": """
            CREATE TABLE IF NOT EXISTS who_vaccine_schedule_adult (
                iso_3_code TEXT,
                countryname TEXT,
                who_region TEXT,
                year TEXT,
                vaccinecode TEXT,
                vaccine_description TEXT,
                schedulerounds TEXT,
                targetpop TEXT,
                targetpop_description TEXT,
                geoarea TEXT,
                ageadministered TEXT,
                sourcecomment TEXT,
                source_file TEXT
            );
        """,
        "indexes": [
            "CREATE INDEX IF NOT EXISTS idx_who_sched_country ON who_vaccine_schedule_adult (iso_3_code, year);",
            "CREATE INDEX IF NOT EXISTS idx_who_sched_vaccine ON who_vaccine_schedule_adult (vaccinecode);",
        ],
    },
    "who_adult_coverage": {
        "file": "who_adult_coverage.csv",
        "columns": [
            "group_name", "code", "name", "year", "antigen", "antigen_description",
            "coverage_category", "coverage_category_description", "target_number",
            "doses", "coverage", "source_file",
        ],
        "ddl": """
            CREATE TABLE IF NOT EXISTS who_adult_coverage (
                group_name TEXT,
                code TEXT,
                name TEXT,
                year TEXT,
                antigen TEXT,
                antigen_description TEXT,
                coverage_category TEXT,
                coverage_category_description TEXT,
                target_number TEXT,
                doses TEXT,
                coverage TEXT,
                source_file TEXT
            );
        """,
        "indexes": [
            "CREATE INDEX IF NOT EXISTS idx_who_coverage_country ON who_adult_coverage (code, year);",
            "CREATE INDEX IF NOT EXISTS idx_who_coverage_antigen ON who_adult_coverage (antigen);",
        ],
    },
    "who_vpd_annual": {
        "file": "who_vpd_annual.csv",
        "columns": [
            "group_name", "code", "name", "year", "disease", "disease_description",
            "metric", "value", "denominator", "source_file",
        ],
        "ddl": """
            CREATE TABLE IF NOT EXISTS who_vpd_annual (
                group_name TEXT,
                code TEXT,
                name TEXT,
                year TEXT,
                disease TEXT,
                disease_description TEXT,
                metric TEXT,
                value TEXT,
                denominator TEXT,
                source_file TEXT
            );
        """,
        "indexes": [
            "CREATE INDEX IF NOT EXISTS idx_who_vpd_country ON who_vpd_annual (code, year);",
            "CREATE INDEX IF NOT EXISTS idx_who_vpd_disease ON who_vpd_annual (disease, metric, year);",
        ],
    },
    "who_mr_annual": {
        "file": "who_mr_annual.csv",
        "columns": [
            "region", "member_state", "iso3", "year", "total_population",
            "annualized_population", "total_suspected_mr_cases", "measles_total",
            "measles_lab", "measles_epi_linked", "measles_clinical",
            "measles_incidence_per_million", "rubella_total", "rubella_lab",
            "rubella_epi_linked", "rubella_clinical",
            "rubella_incidence_per_million", "discarded_cases",
            "discarded_non_mr_per_100k", "source_file",
        ],
        "ddl": """
            CREATE TABLE IF NOT EXISTS who_mr_annual (
                region TEXT,
                member_state TEXT,
                iso3 TEXT,
                year TEXT,
                total_population TEXT,
                annualized_population TEXT,
                total_suspected_mr_cases TEXT,
                measles_total TEXT,
                measles_lab TEXT,
                measles_epi_linked TEXT,
                measles_clinical TEXT,
                measles_incidence_per_million TEXT,
                rubella_total TEXT,
                rubella_lab TEXT,
                rubella_epi_linked TEXT,
                rubella_clinical TEXT,
                rubella_incidence_per_million TEXT,
                discarded_cases TEXT,
                discarded_non_mr_per_100k TEXT,
                source_file TEXT
            );
        """,
        "indexes": [
            "CREATE INDEX IF NOT EXISTS idx_who_mr_annual_country ON who_mr_annual (iso3, year);",
        ],
    },
    "who_mr_monthly": {
        "file": "who_mr_monthly.csv",
        "columns": [
            "region", "country", "iso3", "year", "month", "measles_suspect",
            "measles_clinical", "measles_epi_linked", "measles_lab_confirmed",
            "measles_total", "rubella_clinical", "rubella_epi_linked",
            "rubella_lab_confirmed", "rubella_total", "discarded", "source_file",
        ],
        "ddl": """
            CREATE TABLE IF NOT EXISTS who_mr_monthly (
                region TEXT,
                country TEXT,
                iso3 TEXT,
                year TEXT,
                month TEXT,
                measles_suspect TEXT,
                measles_clinical TEXT,
                measles_epi_linked TEXT,
                measles_lab_confirmed TEXT,
                measles_total TEXT,
                rubella_clinical TEXT,
                rubella_epi_linked TEXT,
                rubella_lab_confirmed TEXT,
                rubella_total TEXT,
                discarded TEXT,
                source_file TEXT
            );
        """,
        "indexes": [
            "CREATE INDEX IF NOT EXISTS idx_who_mr_monthly_country ON who_mr_monthly (iso3, year, month);",
        ],
    },
    "who_mr_elimination": {
        "file": "who_mr_elimination.csv",
        "columns": [
            "disease", "who_region", "iso3", "country", "year", "status", "source_file",
        ],
        "ddl": """
            CREATE TABLE IF NOT EXISTS who_mr_elimination (
                disease TEXT,
                who_region TEXT,
                iso3 TEXT,
                country TEXT,
                year TEXT,
                status TEXT,
                source_file TEXT
            );
        """,
        "indexes": [
            "CREATE INDEX IF NOT EXISTS idx_who_mr_elim_country ON who_mr_elimination (iso3, disease, year);",
        ],
    },
    "who_program_indicators": {
        "file": "who_program_indicators.csv",
        "columns": [
            "iso3", "country", "who_region", "year", "indicator_code",
            "description", "category_code", "category_description", "sort_order",
            "value", "source_file", "snapshot_date",
        ],
        "ddl": """
            CREATE TABLE IF NOT EXISTS who_program_indicators (
                iso3 TEXT,
                country TEXT,
                who_region TEXT,
                year TEXT,
                indicator_code TEXT,
                description TEXT,
                category_code TEXT,
                category_description TEXT,
                sort_order TEXT,
                value TEXT,
                source_file TEXT,
                snapshot_date TEXT
            );
        """,
        "indexes": [
            "CREATE INDEX IF NOT EXISTS idx_who_program_country ON who_program_indicators (iso3, category_code, year);",
            "CREATE INDEX IF NOT EXISTS idx_who_program_indicator ON who_program_indicators (indicator_code);",
        ],
    },
    "who_mr_sia_adult": {
        "file": "who_mr_sia_adult.csv",
        "columns": [
            "country", "country_name", "who_region", "year", "activity_type",
            "intervention", "start_date", "end_date", "agegroup", "extent",
            "status", "target", "doses", "admin_coverage", "other_intervention",
            "coverage_survey_done", "survey_result", "survey_report_received",
            "technical_report_received", "activity_areas_comment", "data_as_at",
            "source_file",
        ],
        "ddl": """
            CREATE TABLE IF NOT EXISTS who_mr_sia_adult (
                country TEXT,
                country_name TEXT,
                who_region TEXT,
                year TEXT,
                activity_type TEXT,
                intervention TEXT,
                start_date TEXT,
                end_date TEXT,
                agegroup TEXT,
                extent TEXT,
                status TEXT,
                target TEXT,
                doses TEXT,
                admin_coverage TEXT,
                other_intervention TEXT,
                coverage_survey_done TEXT,
                survey_result TEXT,
                survey_report_received TEXT,
                technical_report_received TEXT,
                activity_areas_comment TEXT,
                data_as_at TEXT,
                source_file TEXT
            );
        """,
        "indexes": [
            "CREATE INDEX IF NOT EXISTS idx_who_sia_country ON who_mr_sia_adult (country, year);",
        ],
    },
}


def database_url() -> str:
    return os.getenv("DATABASE_URL", "").strip()


def _seed_bundle_bytes() -> bytes:
    parts = sorted(SEED_DIR.glob(f"{SEED_PART_PREFIX}*"))
    if not parts:
        raise RuntimeError("WHO seed bundle parts are missing from the deployment.")
    return b"".join(path.read_bytes() for path in parts)


def _seed_members() -> dict[str, bytes]:
    bundle = io.BytesIO(_seed_bundle_bytes())
    result: dict[str, bytes] = {}
    with tarfile.open(fileobj=bundle, mode="r:gz") as archive:
        for member in archive.getmembers():
            if not member.isfile():
                continue
            if "/" in member.name or "\\" in member.name:
                raise RuntimeError("Unexpected path in WHO seed bundle.")
            extracted = archive.extractfile(member)
            if extracted is not None:
                result[member.name] = extracted.read()
    return result


def _copy_csv(conn, table: str, columns: list[str], payload: bytes) -> None:
    quoted = ", ".join(f'"{column}"' for column in columns)
    sql = f'COPY "{table}" ({quoted}) FROM STDIN WITH (FORMAT CSV, HEADER TRUE)'
    text_stream = io.StringIO(payload.decode("utf-8"))
    with conn.cursor() as cur:
        with cur.copy(sql) as copy:
            while True:
                chunk = text_stream.read(1024 * 1024)
                if not chunk:
                    break
                copy.write(chunk)


def ensure_who_seed_data() -> dict[str, Any]:
    url = database_url()
    if not url:
        return {"configured": False, "loaded": False, "message": "DATABASE_URL is not configured."}

    with psycopg.connect(url, row_factory=dict_row) as conn:
        with conn.cursor() as cur:
            cur.execute(
                """
                CREATE TABLE IF NOT EXISTS who_source_imports (
                    import_key TEXT PRIMARY KEY,
                    imported_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
                    manifest JSONB NOT NULL DEFAULT '{}'::jsonb
                );
                """
            )
            cur.execute("SELECT pg_advisory_lock(hashtext(%s));", (SEED_VERSION,))
            try:
                cur.execute(
                    "SELECT manifest, imported_at FROM who_source_imports WHERE import_key = %s;",
                    (SEED_VERSION,),
                )
                existing = cur.fetchone()
                if existing:
                    conn.commit()
                    return {
                        "configured": True,
                        "loaded": True,
                        "message": "WHO data already loaded.",
                        "manifest": existing["manifest"],
                        "imported_at": existing["imported_at"],
                    }

                members = _seed_members()
                manifest = json.loads(members["manifest.json"].decode("utf-8"))

                for table, spec in TABLE_SPECS.items():
                    cur.execute(spec["ddl"])
                    cur.execute(f'DELETE FROM "{table}";')

                conn.commit()

                for table, spec in TABLE_SPECS.items():
                    payload = members.get(spec["file"])
                    if payload is None:
                        raise RuntimeError(f'Missing WHO seed file: {spec["file"]}')
                    _copy_csv(conn, table, spec["columns"], payload)
                    conn.commit()

                with conn.cursor() as index_cur:
                    for spec in TABLE_SPECS.values():
                        for sql in spec["indexes"]:
                            index_cur.execute(sql)
                    index_cur.execute(
                        """
                        INSERT INTO who_source_imports (import_key, manifest)
                        VALUES (%s, %s::jsonb)
                        ON CONFLICT (import_key)
                        DO UPDATE SET imported_at = NOW(), manifest = EXCLUDED.manifest;
                        """,
                        (SEED_VERSION, json.dumps(manifest)),
                    )
                conn.commit()

                return {
                    "configured": True,
                    "loaded": True,
                    "message": "WHO data loaded into Neon.",
                    "manifest": manifest,
                }
            finally:
                with conn.cursor() as cur:
                    cur.execute("SELECT pg_advisory_unlock(hashtext(%s));", (SEED_VERSION,))
                conn.commit()


def query_who(sql: str, params: tuple[Any, ...] = ()) -> list[dict[str, Any]]:
    url = database_url()
    if not url:
        return []
    with psycopg.connect(url, row_factory=dict_row) as conn:
        with conn.cursor() as cur:
            cur.execute(sql, params)
            return list(cur.fetchall())


def who_table_counts() -> dict[str, int]:
    counts: dict[str, int] = {}
    url = database_url()
    if not url:
        return counts
    with psycopg.connect(url) as conn:
        with conn.cursor() as cur:
            for table in TABLE_SPECS:
                cur.execute(f'SELECT COUNT(*) FROM "{table}";')
                counts[table] = int(cur.fetchone()[0])
    return counts
