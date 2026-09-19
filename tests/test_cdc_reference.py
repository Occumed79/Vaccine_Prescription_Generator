import json

import pandas as pd

import cdc_reference


def test_content_sources_are_official_adult_schedule_items():
    ids = {item.media_id for item in cdc_reference.CDC_CONTENT_SOURCES}
    assert ids == {266010, 266012}


def test_iis_reference_registry_contains_core_code_sets():
    keys = {item.key for item in cdc_reference.CDC_IIS_TABLE_SOURCES}
    assert {"cvx", "mvx", "tradename", "cpt", "cvxvis", "vaccine-groups", "ndc", "respiratory"} <= keys


def test_fetch_content_api_html_accepts_results_string(monkeypatch):
    payload = {"meta": {"status": 200}, "results": "<div>Adult schedule</div>"}

    def fake_fetch_text(url, timeout=45):
        assert "/266012/content?" in url
        return json.dumps(payload)

    monkeypatch.setattr(cdc_reference, "fetch_text", fake_fetch_text)
    html = cdc_reference.fetch_content_api_html(266012)
    assert "Adult schedule" in html


def test_destination_parser_builds_country_links(monkeypatch):
    html = """
    <html><body>
      <a href="/travel/destinations/traveler/none/cuba">Cuba</a>
      <a href="/travel/destinations/traveler/none/china">China</a>
    </body></html>
    """

    monkeypatch.setattr(cdc_reference, "fetch_text", lambda url, timeout=45: html)
    destinations = cdc_reference.fetch_travel_destinations()
    assert destinations["Cuba"].endswith("/travel/destinations/traveler/none/cuba")
    assert destinations["China"].endswith("/travel/destinations/traveler/none/china")


def test_find_vaccine_table_prefers_recommendation_table():
    unrelated = pd.DataFrame({"A": [1]})
    vaccine = pd.DataFrame(
        {
            "Vaccines for disease": ["Typhoid"],
            "Recommendations": ["Recommended for most travelers."],
        }
    )
    found = cdc_reference.find_vaccine_table([unrelated, vaccine])
    assert found is vaccine


def test_import_queue_is_only_parked_adult_sources():
    areas = {item["vaccine_area"] for item in cdc_reference.PARKED_IMPORT_SOURCES}
    assert areas == {"Hepatitis A", "Hepatitis B", "HPV"}
