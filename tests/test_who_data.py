import csv
import io

import who_data


def test_seed_bundle_contains_expected_tables():
    members = who_data._seed_members()
    manifest = __import__("json").loads(members["manifest.json"].decode("utf-8"))
    expected = {
        "who_vaccine_schedule_adult",
        "who_adult_coverage",
        "who_vpd_annual",
        "who_mr_annual",
        "who_mr_monthly",
        "who_mr_elimination",
        "who_program_indicators",
        "who_mr_sia_adult",
    }
    assert expected == set(manifest["tables"])


def test_seed_csv_row_counts_match_manifest():
    members = who_data._seed_members()
    manifest = __import__("json").loads(members["manifest.json"].decode("utf-8"))
    for table, spec in who_data.TABLE_SPECS.items():
        rows = list(csv.reader(io.StringIO(members[spec["file"]].decode("utf-8"))))
        assert len(rows) - 1 == manifest["tables"][table]


def test_scope_excludes_pediatric_only_source_files():
    members = who_data._seed_members()
    manifest = __import__("json").loads(members["manifest.json"].decode("utf-8"))
    excluded = manifest["excluded_files"]
    assert "coverage-survey-data.xlsx" in excluded
    assert "wuenic-input-to-pdf.xlsx" in excluded
