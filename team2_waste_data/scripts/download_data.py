#!/usr/bin/env python3
"""Download the raw inputs for Team 2 (Smart Waste Analytics & Demographics).

Sources
-------
1. UNSD Environmental Indicators, Waste theme
   Landing page (the course URL redirects here):
   https://unstats.un.org/unsd/envstats/qindicators
2. UN Population Division Data Portal API
   https://population.un.org/dataportalapi/api/v1
   Metadata endpoints work without authentication.
   Data endpoints require a free bearer token:
     export TOKEN="your-token"          # or UNPOP_TOKEN / UN_API_TOKEN
   Request a token at:
     https://population.un.org/dataportalapi/token/index.html
   If TOKEN is missing or the data call returns 401, the script falls back to
   the official WPP 2024 bulk CSV files (recommended default).

Usage
-----
  python scripts/download_data.py
  TOKEN=... python scripts/download_data.py
"""

from __future__ import annotations

import gzip
import json
import os
import shutil
import sys
from pathlib import Path
from urllib.parse import quote, urlparse, unquote

import pandas as pd
import requests

ROOT = Path(__file__).resolve().parents[1]
RAW_UNSD = ROOT / "raw" / "unsd"
RAW_UNPOP = ROOT / "raw" / "unpop"
SOURCES = ROOT / "sources"

UNSD_LANDING = "https://unstats.un.org/unsd/envstats/qindicators"
UNSD_FILES = [
    # Official municipal waste generation/collection and management matrices
    # from the Waste theme on the Environmental Indicators page.
    "https://unstats.un.org/unsd/envstats/Questionnaires/2024/Tables/Municipal waste collected.xlsx",
    "https://unstats.un.org/unsd/envstats/Questionnaires/2022/Tables/Municipal waste collection (latest year).xlsx",
    "https://unstats.un.org/unsd/envstats/Questionnaires/2024/Tables/Municipal waste treatment (latest year).xlsx",
    "https://unstats.un.org/unsd/envstats/Questionnaires/2024/Tables/Percentage of municipal waste collected which is recycled.xlsx",
    "https://unstats.un.org/unsd/envstats/Questionnaires/2024/Tables/Total population served by municipal waste collection.xlsx",
    "https://unstats.un.org/unsd/envstats/Questionnaires/2024/Tables/Composition municipal waste (latest year).xlsx",
    "https://unstats.un.org/unsd/envstats/Questionnaires/2024/Tables/Municipal waste collection at city level in selected cities (latest year).xlsx",
    "https://unstats.un.org/unsd/envstats/Questionnaires/2024/Tables/Municipal waste treatment at city level in selected cities.xlsx",
]

API_BASE = "https://population.un.org/dataportalapi/api/v1"
API_TOKEN_PAGE = "https://population.un.org/dataportalapi/token/index.html"
# Indicator 49 = "Total population by sex" (mid-year, persons), WPP 1950-2100.
# defaultVariantId=4 and defaultSexId=3 are the API defaults (Both sexes;
# the API variant IDs are NOT the same as WPP VarID — WPP Medium is VarID 2).
API_INDICATOR_TOTAL_POP = 49
API_DEFAULT_VARIANT = 4
API_DEFAULT_SEX = 3
API_START_YEAR = 1950
API_END_YEAR = 2100

WPP_CSV_BASE = (
    "https://population.un.org/wpp/assets/Excel%20Files/"
    "1_Indicator%20(Standard)/CSV_FILES"
)
WPP_FILES = [
    f"{WPP_CSV_BASE}/WPP2024_TotalPopulationBySex.csv.gz",
    f"{WPP_CSV_BASE}/WPP2024_Demographic_Indicators_Medium.csv.gz",
]
WPP_RELEASE_NOTE = "https://population.un.org/wpp/assets/Files/WPP2024_Release-Note-rev1.pdf"

USER_AGENT = (
    "team2-waste-analytics/1.0 (university course project; "
    "requests + pandas download script)"
)
TIMEOUT = 180


def token_from_env() -> str | None:
    for key in ("TOKEN", "UNPOP_TOKEN", "UN_API_TOKEN"):
        value = os.environ.get(key, "").strip()
        if value:
            return value
    return None


def make_session(token: str | None = None) -> requests.Session:
    session = requests.Session()
    session.headers.update({"User-Agent": USER_AGENT, "Accept": "*/*"})
    if token:
        session.headers["Authorization"] = f"Bearer {token}"
    return session


def encode_url(url: str) -> str:
    """Percent-encode spaces and parentheses in the path (UNSD filenames)."""
    parts = urlparse(url)
    path = quote(unquote(parts.path), safe="/")
    return parts._replace(path=path).geturl()


def download_file(session: requests.Session, url: str, dest: Path) -> Path:
    dest.parent.mkdir(parents=True, exist_ok=True)
    encoded = encode_url(url)
    print(f"GET {encoded}")
    with session.get(encoded, stream=True, timeout=TIMEOUT) as response:
        response.raise_for_status()
        tmp = dest.with_suffix(dest.suffix + ".part")
        with tmp.open("wb") as handle:
            for chunk in response.iter_content(chunk_size=1024 * 128):
                if chunk:
                    handle.write(chunk)
        tmp.replace(dest)
        length = dest.stat().st_size
        last_mod = response.headers.get("Last-Modified", "")
        print(f"  saved {dest.name} ({length} bytes) Last-Modified={last_mod}")
    return dest


def gunzip_copy(src: Path) -> Path:
    dest = src.with_suffix("") if src.suffix == ".gz" else Path(str(src) + ".out")
    with gzip.open(src, "rb") as fin, dest.open("wb") as fout:
        shutil.copyfileobj(fin, fout)
    print(f"  decompressed -> {dest.name} ({dest.stat().st_size} bytes)")
    return dest


def download_unsd(session: requests.Session) -> None:
    RAW_UNSD.mkdir(parents=True, exist_ok=True)
    SOURCES.mkdir(parents=True, exist_ok=True)
    try:
        download_file(session, UNSD_LANDING, SOURCES / "unsd_qindicators_page.html")
    except requests.RequestException as exc:
        print(f"WARNING: could not snapshot the UNSD landing page: {exc}")
    for url in UNSD_FILES:
        name = unquote(urlparse(url).path.split("/")[-1])
        download_file(session, url, RAW_UNSD / name)


def paged_json(session: requests.Session, path: str, page_size: int = 100) -> list:
    url = f"{API_BASE}/{path}?pageNumber=1&pageSize={page_size}"
    rows: list = []
    while url:
        response = session.get(url, timeout=TIMEOUT, headers={"Accept": "application/json"})
        response.raise_for_status()
        payload = response.json()
        rows.extend(payload.get("data") or [])
        url = payload.get("nextPage")
    return rows


def download_api_metadata(session: requests.Session) -> list[dict]:
    """Metadata works without a token. Returns the location list."""
    RAW_UNPOP.mkdir(parents=True, exist_ok=True)
    indicators = paged_json(session, "indicators")
    locations = paged_json(session, "locations")
    (RAW_UNPOP / "unpop_api_indicators.json").write_text(
        json.dumps(indicators, indent=2, ensure_ascii=False), encoding="utf-8"
    )
    (RAW_UNPOP / "unpop_api_locations.json").write_text(
        json.dumps(locations, indent=2, ensure_ascii=False), encoding="utf-8"
    )
    print(f"API metadata: {len(indicators)} indicators, {len(locations)} locations")
    for path in ("topics", "sources"):
        try:
            rows = paged_json(session, path)
            (RAW_UNPOP / f"api_{path}.json").write_text(
                json.dumps(rows, indent=2, ensure_ascii=False), encoding="utf-8"
            )
        except requests.RequestException as exc:
            print(f"WARNING: API /{path} failed: {exc}")
    return locations


def try_api_population(session: requests.Session, token: str | None, locations: list[dict]) -> bool:
    """Return True if the API data download succeeded."""
    dest = RAW_UNPOP / "unpop_api_total_population.csv"
    # Country/area locations have a 3-letter ISO3 that is a real country code
    # in the WPP sense; the API does not expose LocTypeID. We still request
    # every location id (countries + aggregates) and let the caller filter.
    loc_ids = [str(item["id"]) for item in locations if item.get("id") is not None]
    if not loc_ids:
        print("API data: no locations to request")
        return False

    headers = {"Accept": "text/csv, application/json;q=0.9"}
    if token:
        headers["Authorization"] = f"Bearer {token}"

    # Probe a single country first so a missing token fails fast.
    probe_url = (
        f"{API_BASE}/data/indicators/{API_INDICATOR_TOTAL_POP}/locations/348"
        f"?startYear={API_START_YEAR}&endYear={API_END_YEAR}"
        f"&variants={API_DEFAULT_VARIANT}&sexes={API_DEFAULT_SEX}&format=csv"
    )
    print(f"API data probe: {probe_url}")
    probe = session.get(probe_url, timeout=TIMEOUT, headers=headers)
    if probe.status_code == 401:
        print(
            "API data endpoints returned 401 Unauthorized (WWW-Authenticate: Bearer). "
            f"Request a free token at {API_TOKEN_PAGE} and rerun with TOKEN=... "
            "Falling back to the official WPP 2024 bulk CSV."
        )
        return False
    if probe.status_code != 200:
        print(f"API data probe failed: HTTP {probe.status_code} {probe.text[:300]!r}")
        return False

    # Batch location IDs so the URL stays reasonably short.
    frames = []
    batch_size = 40
    for start in range(0, len(loc_ids), batch_size):
        batch = loc_ids[start : start + batch_size]
        url = (
            f"{API_BASE}/data/indicators/{API_INDICATOR_TOTAL_POP}/locations/"
            + ",".join(batch)
            + f"?startYear={API_START_YEAR}&endYear={API_END_YEAR}"
            + f"&variants={API_DEFAULT_VARIANT}&sexes={API_DEFAULT_SEX}"
            + "&pagingInHeader=false&format=csv"
        )
        print(f"  API data batch {start // batch_size + 1} ({len(batch)} locations)")
        response = session.get(url, timeout=TIMEOUT, headers=headers)
        response.raise_for_status()
        content_type = (response.headers.get("Content-Type") or "").lower()
        tmp = RAW_UNPOP / "_api_batch.csv"
        tmp.write_bytes(response.content)
        if "json" in content_type and "csv" not in content_type:
            payload = response.json()
            rows = payload.get("data", payload)
            if not isinstance(rows, list):
                raise RuntimeError(f"Unexpected API JSON payload keys: {payload.keys() if isinstance(payload, dict) else type(payload)}")
            # Paginate if needed
            while isinstance(payload, dict) and payload.get("nextPage"):
                nxt = session.get(payload["nextPage"], timeout=TIMEOUT, headers=headers)
                nxt.raise_for_status()
                payload = nxt.json()
                rows.extend(payload.get("data") or [])
            frames.append(pd.DataFrame(rows))
        else:
            frames.append(pd.read_csv(tmp))
        tmp.unlink(missing_ok=True)

    if not frames:
        print("API data: no rows returned")
        return False
    out = pd.concat(frames, ignore_index=True)
    out.to_csv(dest, index=False)
    print(f"API data saved {dest.name} shape={out.shape}")
    return True


def download_wpp_bulk(session: requests.Session) -> None:
    RAW_UNPOP.mkdir(parents=True, exist_ok=True)
    for url in WPP_FILES:
        name = unquote(urlparse(url).path.split("/")[-1])
        dest = download_file(session, url, RAW_UNPOP / name)
        gunzip_copy(dest)
    try:
        download_file(session, WPP_RELEASE_NOTE, RAW_UNPOP / "WPP2024_Release-Note-rev1.pdf")
    except requests.RequestException as exc:
        print(f"WARNING: could not download WPP release note: {exc}")


def _read_unsd_data(path: Path) -> pd.DataFrame:
    xl = pd.ExcelFile(path)
    sheet = next((s for s in xl.sheet_names if s.lower() == "data"), xl.sheet_names[-1])
    return pd.read_excel(path, sheet_name=sheet)


def sanity_check() -> None:
    print("\n======= Sanity check (pandas) =======")
    for path in sorted(RAW_UNSD.glob("*.xlsx")):
        df = _read_unsd_data(path)
        print(f"{path.name}: shape={df.shape} columns={list(df.columns)}")
    for path in [
        RAW_UNPOP / "WPP2024_TotalPopulationBySex.csv",
        RAW_UNPOP / "WPP2024_Demographic_Indicators_Medium.csv",
        RAW_UNPOP / "unpop_api_total_population.csv",
    ]:
        if not path.exists():
            continue
        df = pd.read_csv(path, encoding="utf-8-sig", nrows=0)
        # row count without loading everything twice
        with path.open("r", encoding="utf-8-sig", newline="") as handle:
            n_rows = sum(1 for _ in handle) - 1
        print(f"{path.name}: shape=({n_rows}, {len(df.columns)}) columns={list(df.columns)}")
    for path in [
        RAW_UNPOP / "unpop_api_locations.json",
        RAW_UNPOP / "unpop_api_indicators.json",
    ]:
        if path.exists():
            data = json.loads(path.read_text(encoding="utf-8"))
            print(f"{path.name}: {len(data)} records")


def main() -> int:
    token = token_from_env()
    print(f"Output root: {ROOT}")
    print(f"API token: {'provided via env' if token else 'not set (data endpoints will 401)'}")

    session = make_session(token)
    download_unsd(session)
    locations = download_api_metadata(session)
    api_ok = try_api_population(session, token, locations)
    # Always keep the official bulk CSV as well: it has all variants, ISO3/M49
    # codes, and does not depend on a token.
    download_wpp_bulk(session)
    if not api_ok:
        print(
            "Population time series used from WPP bulk CSV "
            "(WPP2024_TotalPopulationBySex.csv). "
            "Filter Variant == 'Medium' (VarID == 2) for the medium variant, "
            "and LocTypeID == 4 for countries/areas."
        )
    sanity_check()
    print("\nDone.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
