from __future__ import annotations

import json
import os
from dataclasses import dataclass
from typing import Any
from urllib.parse import urlencode
from urllib.request import Request, urlopen


SODA2_BASE = "https://data.cdc.gov/resource"


@dataclass(frozen=True)
class CdcSodaSource:
    dataset_id: str
    title: str
    category: str
    audience: str
    description: str

    @property
    def endpoint(self) -> str:
        return f"{SODA2_BASE}/{self.dataset_id}.json"


CDC_SODA2_SOURCES: tuple[CdcSodaSource, ...] = (
    CdcSodaSource(
        "aetd-68ew",
        "Adult vaccination coverage, age 18+",
        "Adult coverage",
        "adult",
        "AdultVaxView coverage source used for adult vaccines including Td/Tdap, pneumococcal, and shingles/zoster.",
    ),
    CdcSodaSource(
        "ksfb-ug5d",
        "Adult COVID-19 vaccination coverage",
        "COVID-19",
        "adult",
        "Coverage overall and by selected demographics and jurisdiction among adults 18 years and older.",
    ),
    CdcSodaSource(
        "eanj-9nie",
        "Adult COVID-19 jurisdiction and season comparison",
        "COVID-19",
        "adult",
        "Weekly cumulative adult COVID-19 vaccination coverage map and comparison across seasons.",
    ),
    CdcSodaSource(
        "8yup-c35n",
        "Adult COVID-19 demographic differences",
        "COVID-19",
        "adult",
        "Adult COVID-19 vaccination coverage differences by selected demographics and season.",
    ),
    CdcSodaSource(
        "iwxc-qftf",
        "Adult vaccination status and intent by demographics",
        "Adult behavior",
        "adult",
        "National Immunization Survey Adult COVID Module vaccination status and intent by demographics.",
    ),
    CdcSodaSource(
        "akkj-j5ru",
        "Adult vaccination status and intent trends",
        "Adult behavior",
        "adult",
        "Adult vaccination status and intent time-series data.",
    ),
    CdcSodaSource(
        "94wp-9pid",
        "Vaccination concerns, issues, and motivators",
        "Adult behavior",
        "adult",
        "RespVaxView vaccination concerns, issues, and motivators for adult respiratory vaccination.",
    ),
    CdcSodaSource(
        "ee83-ukst",
        "Fall respiratory virus vaccination survey",
        "Adult respiratory",
        "adult",
        "National Immunization Survey Fall Respiratory Virus Module adult vaccination data.",
    ),
    CdcSodaSource(
        "sw5n-wg2p",
        "Adult influenza coverage and intent",
        "Influenza",
        "adult",
        "Weekly influenza vaccination coverage and intent for adults.",
    ),
    CdcSodaSource(
        "rdng-ki53",
        "Adult influenza jurisdiction coverage",
        "Influenza",
        "adult",
        "Weekly cumulative influenza vaccination coverage and season comparison by jurisdiction for adults 18+.",
    ),
    CdcSodaSource(
        "4g6p-3ed6",
        "Adult influenza demographic differences",
        "Influenza",
        "adult",
        "Weekly adult influenza vaccination coverage differences by selected demographics.",
    ),
    CdcSodaSource(
        "ty79-wym3",
        "Adult influenza coverage by demographics",
        "Influenza",
        "adult",
        "Cumulative adult influenza vaccination coverage by age group, race/ethnicity, urbanicity, and jurisdiction.",
    ),
    CdcSodaSource(
        "b6uq-hdgz",
        "Adult influenza season comparison",
        "Influenza",
        "adult",
        "Adult cumulative influenza vaccination coverage with season-to-season comparison.",
    ),
    CdcSodaSource(
        "ysd3-txwj",
        "Adult influenza doses by pharmacies and medical offices",
        "Influenza",
        "adult",
        "Estimated adult influenza vaccinations administered through pharmacies and physician medical offices.",
    ),
    CdcSodaSource(
        "qeq7-f3ir",
        "Adult RSV coverage and intent",
        "RSV",
        "adult",
        "RSV vaccination coverage and intent among eligible older and high-risk adults.",
    ),
    CdcSodaSource(
        "2yum-eg9f",
        "Adult RSV jurisdiction coverage",
        "RSV",
        "adult",
        "Cumulative RSV vaccination coverage by jurisdiction among eligible adults.",
    ),
    CdcSodaSource(
        "scrf-8d7w",
        "Adult RSV uptake, age 60+",
        "RSV",
        "adult",
        "Historical cumulative RSV vaccination uptake by jurisdiction among adults 60 years and older.",
    ),
    CdcSodaSource(
        "qvzb-qs6p",
        "Invasive pneumococcal disease serotypes",
        "Pneumococcal",
        "all-age disease surveillance",
        "ABCs invasive pneumococcal disease serotype counts, including adult age bands 18-49, 50-64, and 65+.",
    ),
    CdcSodaSource(
        "3rge-nu2a",
        "COVID-19 outcomes by age and vaccination status",
        "COVID-19 outcomes",
        "adult-filterable",
        "COVID-19 case or death rates by age group and vaccination status; adult age groups can be selected.",
    ),
    CdcSodaSource(
        "d6p8-wqjm",
        "COVID-19 outcomes by age and booster status",
        "COVID-19 outcomes",
        "adult-filterable",
        "COVID-19 outcome rates by age and booster-dose status; adult age groups can be selected.",
    ),
    CdcSodaSource(
        "x9gk-5huc",
        "NNDSS weekly disease surveillance",
        "Vaccine-preventable disease surveillance",
        "all-age disease surveillance",
        "Current weekly NNDSS disease surveillance used as a broad vaccine-preventable disease activity source.",
    ),
    CdcSodaSource(
        "hjax-h34q",
        "Measles surveillance",
        "Vaccine-preventable disease surveillance",
        "all-age disease surveillance",
        "NNDSS measles surveillance table.",
    ),
    CdcSodaSource(
        "kxvg-q6s7",
        "Mumps surveillance",
        "Vaccine-preventable disease surveillance",
        "all-age disease surveillance",
        "NNDSS mumps surveillance table.",
    ),
    CdcSodaSource(
        "4qb4-rsd8",
        "Rubella surveillance",
        "Vaccine-preventable disease surveillance",
        "all-age disease surveillance",
        "NNDSS rubella surveillance table.",
    ),
    CdcSodaSource(
        "759d-qk63",
        "Varicella surveillance",
        "Vaccine-preventable disease surveillance",
        "all-age disease surveillance",
        "NNDSS varicella surveillance table.",
    ),
    CdcSodaSource(
        "cqcc-kwwr",
        "Poliomyelitis, paralytic surveillance",
        "Vaccine-preventable disease surveillance",
        "all-age disease surveillance",
        "NNDSS paralytic poliomyelitis surveillance table.",
    ),
    CdcSodaSource(
        "q9sm-44y3",
        "Poliovirus infection, nonparalytic surveillance",
        "Vaccine-preventable disease surveillance",
        "all-age disease surveillance",
        "NNDSS nonparalytic poliovirus infection surveillance table.",
    ),
    CdcSodaSource(
        "vxsn-2csw",
        "Acute hepatitis A and B surveillance",
        "Vaccine-preventable disease surveillance",
        "all-age disease surveillance",
        "NNDSS acute hepatitis A and B disease surveillance.",
    ),
)


def get_socrata_app_token() -> str:
    return os.getenv("SOCRATA_APP_TOKEN", "").strip()


def build_soda2_url(
    dataset_id: str,
    *,
    limit: int = 250,
    offset: int = 0,
    select: str | None = None,
    where: str | None = None,
    order: str | None = None,
) -> str:
    if not dataset_id or "/" in dataset_id:
        raise ValueError("A valid Socrata dataset ID is required.")
    if limit < 1 or limit > 50_000:
        raise ValueError("limit must be between 1 and 50,000.")
    if offset < 0:
        raise ValueError("offset cannot be negative.")

    params: dict[str, Any] = {"$limit": limit, "$offset": offset}
    if select:
        params["$select"] = select
    if where:
        params["$where"] = where
    if order:
        params["$order"] = order
    return f"{SODA2_BASE}/{dataset_id}.json?{urlencode(params)}"


def fetch_soda2_rows(
    dataset_id: str,
    *,
    limit: int = 250,
    offset: int = 0,
    select: str | None = None,
    where: str | None = None,
    order: str | None = None,
    timeout: int = 30,
) -> list[dict[str, Any]]:
    url = build_soda2_url(
        dataset_id,
        limit=limit,
        offset=offset,
        select=select,
        where=where,
        order=order,
    )
    headers = {
        "Accept": "application/json",
        "User-Agent": "Occu-Med-Vaccine-Prescription-Generator/1.0",
    }
    app_token = get_socrata_app_token()
    if app_token:
        headers["X-App-Token"] = app_token

    request = Request(url, headers=headers, method="GET")
    with urlopen(request, timeout=timeout) as response:
        payload = json.loads(response.read().decode("utf-8"))
    if not isinstance(payload, list):
        raise RuntimeError("CDC Socrata returned an unexpected response.")
    return payload


def source_categories() -> list[str]:
    return sorted({source.category for source in CDC_SODA2_SOURCES})


def sources_for_category(category: str | None = None) -> list[CdcSodaSource]:
    if not category or category == "All":
        return list(CDC_SODA2_SOURCES)
    return [source for source in CDC_SODA2_SOURCES if source.category == category]
