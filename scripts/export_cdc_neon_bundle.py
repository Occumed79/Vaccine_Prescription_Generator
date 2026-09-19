from __future__ import annotations

import csv
import io
import json
import os
import time
import urllib.parse
import urllib.request
import zipfile
from datetime import datetime, timezone
from pathlib import Path

OUT = Path("cdc_neon_bundle")
SODA = OUT / "soda2"
NHIS = OUT / "nhis"
CONTENT = OUT / "content"
META = OUT / "metadata"

UA = "Occu-Med CDC adult-vaccine exporter/1.0"
TIMEOUT = 120

# Adult-focused CDC vaccination / vaccine-impact / vaccine-preventable-disease sources.
# Explicitly excludes child-, infant-, pregnancy-, and Medicare-specific feeds.
SODA_SOURCES = [
    ("aetd-68ew", "adult_coverage", "Adult vaccination coverage 18+ (Td/Tdap, pneumococcal, zoster and related adult coverage)"),
    ("ksfb-ug5d", "adult_covid", "Adult COVID-19 vaccination coverage"),
    ("eanj-9nie", "adult_covid", "Adult COVID-19 season/jurisdiction differences"),
    ("8yup-c35n", "adult_covid", "Adult COVID-19 demographic differences"),
    ("uc4z-hbsd", "adult_covid", "Archived adult COVID-19 NIS-ACM monthly data"),
    ("ee83-ukst", "adult_respiratory", "NIS Fall Respiratory Virus Module"),
    ("94wp-9pid", "adult_respiratory", "Vaccination concerns, issues and motivators"),
    ("iwxc-qftf", "adult_respiratory", "Adult vaccination status and intent by demographics"),
    ("akkj-j5ru", "adult_respiratory", "Adult vaccination status and intent trends"),
    ("sw5n-wg2p", "adult_flu", "Adult influenza vaccination coverage and intent"),
    ("rdng-ki53", "adult_flu", "Adult influenza coverage by jurisdiction"),
    ("4g6p-3ed6", "adult_flu", "Adult influenza demographic differences"),
    ("ty79-wym3", "adult_flu", "Adult influenza coverage by age/race/urbanicity/jurisdiction"),
    ("b6uq-hdgz", "adult_flu", "Adult influenza cumulative coverage / season comparison"),
    ("ysd3-txwj", "adult_flu", "Estimated adult influenza vaccinations in pharmacies and physician offices"),
    ("qeq7-f3ir", "adult_rsv", "Adult RSV vaccination coverage and intent"),
    ("2yum-eg9f", "adult_rsv", "Adult RSV coverage by jurisdiction"),
    ("scrf-8d7w", "adult_rsv", "Adult RSV uptake by jurisdiction"),
    ("qvzb-qs6p", "vaccine_impact", "Invasive pneumococcal disease serotype data by age/site/year"),
    ("3rge-nu2a", "vaccine_impact", "COVID-19 case/death rates by age and vaccination status"),
    ("d6p8-wqjm", "vaccine_impact", "COVID-19 case/death rates by age and booster status"),
    ("x9gk-5huc", "nndss", "NNDSS weekly notifiable disease surveillance"),
    ("hjax-h34q", "nndss", "NNDSS measles surveillance"),
    ("kxvg-q6s7", "nndss", "NNDSS mumps surveillance"),
    ("4qb4-rsd8", "nndss", "NNDSS rubella surveillance"),
    ("759d-qk63", "nndss", "NNDSS varicella surveillance"),
    ("cqcc-kwwr", "nndss", "NNDSS paralytic poliomyelitis surveillance"),
    ("q9sm-44y3", "nndss", "NNDSS nonparalytic poliovirus infection surveillance"),
    ("vxsn-2csw", "nndss", "NNDSS acute hepatitis A/B surveillance"),
]

NHIS_SOURCES = [
    (2022, "https://ftp.cdc.gov/pub/Health_Statistics/NCHS/Datasets/NHIS/2022/adult22csv.zip", "Adult NHIS microdata; includes adult HPV vaccination fields."),
    (2023, "https://ftp.cdc.gov/pub/health_statistics/nchs/Datasets/NHIS/2023/adult23csv.zip", "Adult NHIS microdata; includes hepatitis B vaccination field SHTHEPB1_A."),
    (2024, "https://ftp.cdc.gov/pub/health_Statistics/nchs/Datasets/NHIS/2024/adult24csv.zip", "Adult NHIS microdata; includes hepatitis A vaccination field SHTHEPA_A."),
]

CONTENT_SOURCES = [
    ("266012", "Adult Immunization Schedule by Age", "https://tools.cdc.gov/api/v2/resources/media/266012/noscript"),
    ("266010", "Vaccines Indicated for Adults Based on Medical and Other Indications", "https://tools.cdc.gov/api/v2/resources/media/266010/noscript"),
]

def stamp():
    return datetime.now(timezone.utc).isoformat()

def fetch(url: str, tries: int = 4) -> bytes:
    req = urllib.request.Request(url, headers={"User-Agent": UA, "Accept": "*/*"})
    err = None
    for i in range(tries):
        try:
            with urllib.request.urlopen(req, timeout=TIMEOUT) as r:
                b = r.read()
                if not b:
                    raise RuntimeError("empty response")
                low = b[:10000].lower()
                if b"site currently unavailable" in low or b"service unavailable" in low:
                    raise RuntimeError("upstream maintenance/unavailable response")
                return b
        except Exception as e:
            err = e
            if i + 1 < tries:
                time.sleep(min(30, 2 ** (i + 1)))
    raise RuntimeError(str(err))

def row_count_csv(data: bytes):
    try:
        text = data.decode("utf-8-sig", errors="replace")
        return max(0, sum(1 for _ in csv.reader(io.StringIO(text))) - 1)
    except Exception:
        return ""

def save(path: Path, data: bytes):
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_bytes(data)

def get_soda(dataset_id: str):
    urls = [
        f"https://data.cdc.gov/api/views/{dataset_id}/rows.csv?accessType=DOWNLOAD",
        f"https://data.cdc.gov/resource/{dataset_id}.csv?$limit=50000",
    ]
    last = None
    for u in urls:
        try:
            b = fetch(u)
            if b[:1] == b"<":
                raise RuntimeError("HTML received instead of CSV")
            return b, u
        except Exception as e:
            last = e
    raise RuntimeError(str(last))

def main():
    for p in [SODA, NHIS, CONTENT, META]:
        p.mkdir(parents=True, exist_ok=True)

    manifest = []
    failures = []

    for dataset_id, group, label in SODA_SOURCES:
        print("SODA2", dataset_id, label, flush=True)
        try:
            data, source_url = get_soda(dataset_id)
            csv_path = SODA / f"{dataset_id}.csv"
            save(csv_path, data)
            meta_url = f"https://data.cdc.gov/api/views/{dataset_id}"
            try:
                meta = fetch(meta_url)
                save(META / f"{dataset_id}.json", meta)
            except Exception as me:
                failures.append({"source_id": dataset_id, "type": "metadata", "error": str(me)})
            manifest.append({
                "source_type": "CDC SODA2",
                "source_id": dataset_id,
                "group": group,
                "label": label,
                "source_url": source_url,
                "local_file": str(csv_path.relative_to(OUT)),
                "row_count": row_count_csv(data),
                "downloaded_at_utc": stamp(),
                "status": "ok",
            })
        except Exception as e:
            failures.append({"source_id": dataset_id, "type": "SODA2", "error": str(e)})
            manifest.append({
                "source_type": "CDC SODA2",
                "source_id": dataset_id,
                "group": group,
                "label": label,
                "source_url": f"https://data.cdc.gov/resource/{dataset_id}.csv",
                "local_file": "",
                "row_count": "",
                "downloaded_at_utc": stamp(),
                "status": "failed",
            })

    for year, url, note in NHIS_SOURCES:
        print("NHIS", year, flush=True)
        try:
            data = fetch(url)
            zpath = NHIS / str(year) / Path(urllib.parse.urlparse(url).path).name
            save(zpath, data)
            extracted = []
            with zipfile.ZipFile(io.BytesIO(data)) as z:
                for member in z.infolist():
                    if member.is_dir():
                        continue
                    name = Path(member.filename).name
                    if not name:
                        continue
                    out = NHIS / str(year) / name
                    save(out, z.read(member))
                    extracted.append(str(out.relative_to(OUT)))
            manifest.append({
                "source_type": "CDC NHIS adult public-use microdata",
                "source_id": f"NHIS-{year}-adult",
                "group": "nhis_adult",
                "label": note,
                "source_url": url,
                "local_file": str(zpath.relative_to(OUT)),
                "row_count": "",
                "downloaded_at_utc": stamp(),
                "status": "ok",
            })
        except Exception as e:
            failures.append({"source_id": f"NHIS-{year}-adult", "type": "NHIS", "error": str(e)})

    for media_id, label, url in CONTENT_SOURCES:
        print("CONTENT", media_id, flush=True)
        try:
            data = fetch(url)
            path = CONTENT / f"{media_id}.html"
            save(path, data)
            manifest.append({
                "source_type": "CDC Content Syndication API",
                "source_id": media_id,
                "group": "adult_schedule",
                "label": label,
                "source_url": url,
                "local_file": str(path.relative_to(OUT)),
                "row_count": "",
                "downloaded_at_utc": stamp(),
                "status": "ok",
            })
        except Exception as e:
            failures.append({"source_id": media_id, "type": "CDC content", "error": str(e)})

    with (OUT / "sources_manifest.csv").open("w", newline="", encoding="utf-8") as f:
        fields = ["source_type","source_id","group","label","source_url","local_file","row_count","downloaded_at_utc","status"]
        w = csv.DictWriter(f, fieldnames=fields)
        w.writeheader()
        w.writerows(manifest)

    save(OUT / "failures.json", json.dumps(failures, indent=2).encode())
    save(OUT / "README.txt", (
        "CDC adult-vaccine data bundle for Neon import.\\n"
        "Scope excludes child-, infant-, pregnancy-, and Medicare-specific feeds.\\n"
        "SODA2 CSVs are under soda2/. NHIS adult public-use files are under nhis/.\\n"
        "sources_manifest.csv records provenance and download status.\\n"
        "failures.json lists any source unavailable during this run (for example during Socrata maintenance).\\n"
    ).encode())

    with zipfile.ZipFile("CDC_Adult_Vaccine_Data_for_Neon.zip", "w", zipfile.ZIP_DEFLATED, allowZip64=True) as z:
        for p in OUT.rglob("*"):
            if p.is_file():
                z.write(p, p.relative_to(OUT.parent))

    ok = sum(1 for r in manifest if r.get("status") == "ok")
    failed = len(failures)
    print(f"DONE ok={ok} failures={failed}", flush=True)

if __name__ == "__main__":
    main()
