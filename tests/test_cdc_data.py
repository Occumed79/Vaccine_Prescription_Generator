import json

import cdc_data


def test_registry_has_expected_adult_sources():
    ids = {source.dataset_id for source in cdc_data.CDC_SODA2_SOURCES}
    assert "aetd-68ew" in ids
    assert "qvzb-qs6p" in ids
    assert "x9gk-5huc" in ids
    assert "cqcc-kwwr" in ids


def test_registry_does_not_include_explicit_child_pregnancy_or_medicare_sources():
    text = " ".join(
        f"{source.title} {source.description} {source.audience}".lower()
        for source in cdc_data.CDC_SODA2_SOURCES
    )
    assert "pregnan" not in text
    assert "medicare" not in text
    assert "child vaccination" not in text


def test_build_soda2_url_encodes_query_parameters():
    url = cdc_data.build_soda2_url(
        "aetd-68ew",
        limit=500,
        offset=10,
        where="year = '2025'",
        order="year DESC",
    )
    assert url.startswith("https://data.cdc.gov/resource/aetd-68ew.json?")
    assert "%24limit=500" in url
    assert "%24offset=10" in url
    assert "%24where=" in url
    assert "%24order=" in url


def test_fetch_soda2_rows_sends_app_token(monkeypatch):
    monkeypatch.setenv("SOCRATA_APP_TOKEN", "token-123")

    captured = {}

    class FakeResponse:
        def __enter__(self):
            return self

        def __exit__(self, *args):
            return False

        def read(self):
            return json.dumps([{"vaccine": "Tdap"}]).encode("utf-8")

    def fake_urlopen(request, timeout):
        captured["headers"] = dict(request.header_items())
        captured["timeout"] = timeout
        return FakeResponse()

    monkeypatch.setattr(cdc_data, "urlopen", fake_urlopen)
    rows = cdc_data.fetch_soda2_rows("aetd-68ew", limit=1)

    assert rows == [{"vaccine": "Tdap"}]
    assert captured["headers"]["X-app-token"] == "token-123"
    assert captured["timeout"] == 30
