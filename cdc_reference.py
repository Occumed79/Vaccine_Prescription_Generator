from __future__ import annotations

import json
from dataclasses import dataclass
from html.parser import HTMLParser
from io import StringIO
from typing import Any
from urllib.parse import urlencode, urljoin
from urllib.request import Request, urlopen

import pandas as pd


USER_AGENT = "Occu-Med-Vaccine-Prescription-Generator/1.0"
CONTENT_API_BASE = "https://tools.cdc.gov/api/v2/resources/media"
TRAVEL_DESTINATIONS_URL = "https://wwwnc.cdc.gov/travel/destinations/list/"
IIS_RUNTIME_REST_URL = (
    "https://vaccinecodeset.cdc.gov/"
    "SymedicalCDCVCABPRODRuntimeRestService/swagger/ui/index"
)
IIS_ACCESS_OPTIONS_URL = "https://www.cdc.gov/iis/code-sets/viewpoint-rest.html"
YELLOW_BOOK_COUNTRY_URL = (
    "https://www.cdc.gov/yellow-book/hcp/preparing-international-travelers/"
    "yellow-fever-vaccine-and-malaria-prevention-information-by-country.html"
)


@dataclass(frozen=True)
class CdcContentSource:
    media_id: int
    title: str
    description: str


@dataclass(frozen=True)
class CdcReferenceTableSource:
    key: str
    title: str
    url: str
    description: str


CDC_CONTENT_SOURCES: tuple[CdcContentSource, ...] = (
    CdcContentSource(
        266012,
        "Adult Immunization Schedule by Age",
        "CDC official adult immunization schedule by age.",
    ),
    CdcContentSource(
        266010,
        "Adult Vaccines by Medical and Other Indications",
        "CDC official adult immunization schedule by medical and other indications.",
    ),
)


CDC_IIS_TABLE_SOURCES: tuple[CdcReferenceTableSource, ...] = (
    CdcReferenceTableSource(
        "cvx",
        "CVX — Vaccines Administered",
        "https://www2.cdc.gov/vaccines/iis/iisstandards/vaccines.asp?rpt=cvx",
        "Current CDC CVX vaccine-administered code table.",
    ),
    CdcReferenceTableSource(
        "mvx",
        "MVX — Vaccine Manufacturers",
        "https://www2.cdc.gov/vaccines/iis/iisstandards/vaccines.asp?rpt=mvx",
        "Current CDC MVX vaccine manufacturer code table.",
    ),
    CdcReferenceTableSource(
        "tradename",
        "Product Name → CVX / MVX",
        "https://www2.cdc.gov/vaccines/iis/iisstandards/vaccines.asp?rpt=tradename",
        "CDC product/tradename mappings to CVX and MVX.",
    ),
    CdcReferenceTableSource(
        "cpt",
        "CPT → CVX",
        "https://www2.cdc.gov/vaccines/iis/iisstandards/vaccines.asp?rpt=cpt",
        "CDC vaccine-related CPT to CVX crosswalk.",
    ),
    CdcReferenceTableSource(
        "cvxvis",
        "CVX → VIS",
        "https://www2.cdc.gov/vaccines/iis/iisstandards/vaccines.asp?rpt=cvxvis",
        "CDC mapping between CVX vaccine codes and Vaccine Information Statements.",
    ),
    CdcReferenceTableSource(
        "vaccine-groups",
        "CVX → Vaccine Groups",
        "https://www2.cdc.gov/vaccines/iis/iisstandards/vaccines.asp?rpt=vg",
        "CDC mapping between CVX codes and vaccine groups.",
    ),
    CdcReferenceTableSource(
        "ndc",
        "NDC Vaccine Crosswalk",
        "https://www2.cdc.gov/vaccines/iis/iisstandards/vaccines.asp?rpt=ndc",
        "CDC vaccine NDC relationships and CVX mapping.",
    ),
    CdcReferenceTableSource(
        "vis-url",
        "VIS → Current CDC URL",
        "https://www.cdc.gov/iis/code-sets/vis-url-table.html",
        "Current Vaccine Information Statement URLs.",
    ),
    CdcReferenceTableSource(
        "respiratory",
        "Current Respiratory Vaccine Codes",
        "https://www.cdc.gov/iis/code-sets/fall-season-respiratory-codes.html",
        "Current CDC RSV, COVID-19, and influenza code/crosswalk tables.",
    ),
)


PARKED_IMPORT_SOURCES: tuple[dict[str, str], ...] = (
    {
        "source": "NHIS 2024 Adult",
        "vaccine_area": "Hepatitis A",
        "status": "Parked for Data Importer",
        "note": "Use SHTHEPA_A plus adult demographics, risk/travel, and survey design/weight fields.",
    },
    {
        "source": "NHIS 2023 Adult",
        "vaccine_area": "Hepatitis B",
        "status": "Parked for Data Importer",
        "note": "Use SHTHEPB1_A plus adult demographics, risk/travel, and survey design/weight fields.",
    },
    {
        "source": "NHIS 2022 Adult",
        "vaccine_area": "HPV",
        "status": "Parked for Data Importer",
        "note": "Use adult HPV fields and restrict analysis to the applicable adult age range.",
    },
)


def _fetch_bytes(url: str, *, timeout: int = 45) -> bytes:
    request = Request(
        url,
        headers={
            "Accept": "*/*",
            "User-Agent": USER_AGENT,
        },
        method="GET",
    )
    with urlopen(request, timeout=timeout) as response:
        return response.read()


def fetch_text(url: str, *, timeout: int = 45) -> str:
    return _fetch_bytes(url, timeout=timeout).decode("utf-8", errors="replace")


def fetch_content_api_html(media_id: int, *, timeout: int = 45) -> str:
    if media_id <= 0:
        raise ValueError("media_id must be positive.")
    params = urlencode(
        {
            "stripScripts": "true",
            "stripAnchors": "false",
            "stripImages": "false",
            "stripComments": "true",
            "stripStyles": "false",
            "nw": "true",
        }
    )
    url = f"{CONTENT_API_BASE}/{media_id}/content?{params}"
    payload = json.loads(fetch_text(url, timeout=timeout))
    results = payload.get("results") if isinstance(payload, dict) else payload

    if isinstance(results, str):
        return results
    if isinstance(results, dict):
        content = results.get("content")
        if isinstance(content, str):
            return content
    raise RuntimeError("CDC Content Services returned an unexpected response.")


def _flatten_columns(frame: pd.DataFrame) -> pd.DataFrame:
    clean = frame.copy()
    if isinstance(clean.columns, pd.MultiIndex):
        clean.columns = [
            " | ".join(str(part) for part in col if str(part) != "nan").strip()
            for col in clean.columns
        ]
    else:
        clean.columns = [str(col).strip() for col in clean.columns]
    return clean


def fetch_html_tables(url: str, *, timeout: int = 45) -> list[pd.DataFrame]:
    html = fetch_text(url, timeout=timeout)
    tables = pd.read_html(StringIO(html))
    return [_flatten_columns(frame) for frame in tables]


def find_vaccine_table(tables: list[pd.DataFrame]) -> pd.DataFrame | None:
    for frame in tables:
        headers = " ".join(str(col).lower() for col in frame.columns)
        if "vaccines for disease" in headers or (
            "recommendations" in headers and "vaccine" in headers
        ):
            return frame
    return None


class _DestinationLinkParser(HTMLParser):
    def __init__(self) -> None:
        super().__init__()
        self._href: str | None = None
        self._text: list[str] = []
        self.links: list[tuple[str, str]] = []

    def handle_starttag(self, tag: str, attrs: list[tuple[str, str | None]]) -> None:
        if tag.lower() != "a":
            return
        href = dict(attrs).get("href")
        if href and "/travel/destinations/traveler/none/" in href.lower():
            self._href = href
            self._text = []

    def handle_data(self, data: str) -> None:
        if self._href is not None:
            self._text.append(data)

    def handle_endtag(self, tag: str) -> None:
        if tag.lower() != "a" or self._href is None:
            return
        label = " ".join("".join(self._text).split()).strip()
        if label:
            self.links.append((label, self._href))
        self._href = None
        self._text = []


def fetch_travel_destinations(*, timeout: int = 45) -> dict[str, str]:
    html = fetch_text(TRAVEL_DESTINATIONS_URL, timeout=timeout)
    parser = _DestinationLinkParser()
    parser.feed(html)
    destinations: dict[str, str] = {}
    for label, href in parser.links:
        destinations.setdefault(label, urljoin(TRAVEL_DESTINATIONS_URL, href))
    return dict(sorted(destinations.items(), key=lambda item: item[0].casefold()))


def fetch_travel_vaccine_table(url: str, *, timeout: int = 45) -> pd.DataFrame:
    tables = fetch_html_tables(url, timeout=timeout)
    frame = find_vaccine_table(tables)
    if frame is None:
        raise RuntimeError("CDC destination page did not expose a vaccine recommendations table.")
    return frame
