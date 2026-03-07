import json
import os
import re
from dataclasses import dataclass
from datetime import datetime
from pathlib import Path
from typing import Any, Dict, Optional, Tuple, List

import httpx
from bs4 import BeautifulSoup

SEC_FILES_TICKERS_URL = "https://www.sec.gov/files/company_tickers.json"
SEC_SUBMISSIONS_URL = "https://data.sec.gov/submissions/CIK{cik10}.json"
SEC_ARCHIVES_BASE = "https://www.sec.gov/Archives/edgar/data"


def _sec_headers() -> Dict[str, str]:
    ua = os.getenv("SEC_USER_AGENT", "").strip()
    if not ua:
        raise RuntimeError(
            "SEC_USER_AGENT is required. Set it to something like "
            "'YourName YourApp your.email@example.com'."
        )
    return {
        "User-Agent": ua,
        "Accept-Encoding": "gzip, deflate",
        "Host": "www.sec.gov",
    }


def _data_dirs() -> Tuple[Path, Path]:
    base = Path(os.getenv("DATA_DIR", "data"))
    cache = base / "cache"
    raw = base / "raw"
    cache.mkdir(parents=True, exist_ok=True)
    raw.mkdir(parents=True, exist_ok=True)
    return cache, raw


def _normalize_whitespace(text: str) -> str:
    text = re.sub(r"\u00a0", " ", text)
    text = re.sub(r"[ \t]+", " ", text)
    text = re.sub(r"\n{3,}", "\n\n", text)
    return text.strip()


def html_to_text(html: str) -> str:
    soup = BeautifulSoup(html, "lxml")
    # Remove scripts/styles
    for tag in soup(["script", "style", "noscript"]):
        tag.decompose()
    text = soup.get_text("\n")
    return _normalize_whitespace(text)


async def get_ticker_to_cik_map(client: httpx.AsyncClient) -> Dict[str, str]:
    """
    Returns: { "AAPL": "0000320193", ... } (CIK padded to 10 digits)
    Cached to disk for speed.
    """
    cache_dir, _ = _data_dirs()
    cache_path = cache_dir / "company_tickers.json"

    if cache_path.exists():
        data = json.loads(cache_path.read_text(encoding="utf-8"))
    else:
        r = await client.get(SEC_FILES_TICKERS_URL, headers=_sec_headers(), timeout=30)
        r.raise_for_status()
        data = r.json()
        cache_path.write_text(json.dumps(data), encoding="utf-8")

    # company_tickers.json is dict keyed by numbers -> entries
    mapping: Dict[str, str] = {}
    for _, entry in data.items():
        ticker = str(entry.get("ticker", "")).upper()
        cik = str(entry.get("cik_str", "")).strip()
        if ticker and cik.isdigit():
            mapping[ticker] = cik.zfill(10)
    return mapping


async def fetch_submissions(client: httpx.AsyncClient, cik10: str) -> Dict[str, Any]:
    url = SEC_SUBMISSIONS_URL.format(cik10=cik10)
    r = await client.get(url, headers=_sec_headers(), timeout=30)
    r.raise_for_status()
    return r.json()


def pick_filing(
    submissions: Dict[str, Any],
    form_type: str,
    year: Optional[int] = None,
) -> Dict[str, str]:
    """
    Picks a filing from submissions['filings']['recent'].
    Returns dict with accessionNumber, primaryDocument, filingDate, form.
    """
    recent = submissions.get("filings", {}).get("recent", {})
    forms = recent.get("form", [])
    accession = recent.get("accessionNumber", [])
    primary_doc = recent.get("primaryDocument", [])
    filing_dates = recent.get("filingDate", [])

    form_type = form_type.upper().strip()
    candidates: List[Tuple[int, Dict[str, str]]] = []

    for i, f in enumerate(forms):
        if str(f).upper() != form_type:
            continue
        date_str = str(filing_dates[i]) if i < len(filing_dates) else ""
        if year is not None:
            try:
                if int(date_str[:4]) != int(year):
                    continue
            except Exception:
                continue

        acc = str(accession[i]) if i < len(accession) else ""
        doc = str(primary_doc[i]) if i < len(primary_doc) else ""
        if acc and doc and date_str:
            candidates.append(
                (
                    i,
                    {
                        "form": form_type,
                        "filingDate": date_str,
                        "accessionNumber": acc,
                        "primaryDocument": doc,
                    },
                )
            )

    if not candidates:
        hint = f"form={form_type}" + (f", year={year}" if year else "")
        raise ValueError(f"No filing found for {hint} in recent submissions.")

    # recent list is already newest-first typically; take first candidate
    return candidates[0][1]


def build_primary_doc_url(cik10: str, accession_number: str, primary_document: str) -> str:
    """
    SEC Archives pattern:
    https://www.sec.gov/Archives/edgar/data/{cik_no_leading_zeros}/{accession_no_dashes}/{primaryDocument}
    :contentReference[oaicite:3]{index=3}
    """
    cik_nozeros = str(int(cik10))  # drop leading zeros
    acc_nodashes = accession_number.replace("-", "")
    return f"{SEC_ARCHIVES_BASE}/{cik_nozeros}/{acc_nodashes}/{primary_document}"


async def download_primary_document(client: httpx.AsyncClient, url: str) -> str:
    r = await client.get(url, headers=_sec_headers(), timeout=60)
    r.raise_for_status()
    return r.text


def persist_raw_doc(
    ticker: str,
    cik10: str,
    filing_meta: Dict[str, str],
    text: str,
) -> Dict[str, Any]:
    _, raw_dir = _data_dirs()

    doc_id = f"{ticker.upper()}-{filing_meta['form']}-{filing_meta['filingDate']}-{filing_meta['accessionNumber'].replace('-', '')}"
    record = {
        "doc_id": doc_id,
        "ticker": ticker.upper(),
        "cik": cik10,
        "form": filing_meta["form"],
        "filing_date": filing_meta["filingDate"],
        "accession_number": filing_meta["accessionNumber"],
        "primary_document": filing_meta["primaryDocument"],
        "fetched_at_utc": datetime.utcnow().isoformat() + "Z",
        "text": text,
    }

    out_path = raw_dir / f"{doc_id}.json"
    out_path.write_text(json.dumps(record, ensure_ascii=False), encoding="utf-8")
    return record


async def fetch_and_store_filing(
    ticker: str,
    form_type: str,
    year: Optional[int] = None,
) -> Dict[str, Any]:
    async with httpx.AsyncClient() as client:
        mapping = await get_ticker_to_cik_map(client)
        t = ticker.upper().strip()
        if t not in mapping:
            raise ValueError(f"Ticker not found: {t}")

        cik10 = mapping[t]
        submissions = await fetch_submissions(client, cik10)
        filing = pick_filing(submissions, form_type=form_type, year=year)

        url = build_primary_doc_url(
            cik10=cik10,
            accession_number=filing["accessionNumber"],
            primary_document=filing["primaryDocument"],
        )

        html = await download_primary_document(client, url)
        text = html_to_text(html)

        return persist_raw_doc(ticker=t, cik10=cik10, filing_meta=filing, text=text)