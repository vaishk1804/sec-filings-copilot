# backend/app/pipeline/edgar_fetcher.py
import time
import httpx
from typing import Optional
from app.config import settings

BASE_URL="https://data.sec.gov"
ARCHIVES_BASE_URL="https://www.sec.gov"
SEARCH_URL="https://efts.sec.gov/LATEST/search-index"

HEADERS = {
  "User-Agent": settings.edgar_user_agent,
  "Accept-Encoding": "gzip, deflate",
}

FORM_TYPES= {"10-K","10-Q"}

def get_cik(ticker: str) -> str:
  """ Resolve a ticker symbol to a zero-padded 10-digit CIK"""
  url="https://www.sec.gov/files/company_tickers.json"
  resp=httpx.get(url, headers=HEADERS, timeout=15)
  resp.raise_for_status()
  data=resp.json()
  ticker_upper = ticker.upper()
  for entry in data.values():
    if entry["ticker"] == ticker_upper:
      return str(entry["cik_str"]).zfill(10)
  raise ValueError(f"Ticker '{ticker}' not found in EDGAR company list")

def get_filings_list(cik:str, form_type: str, max_results: int=5) -> list[dict]:
  """Return a list of filing metadata dicts for a given CIK and form type"""
  assert form_type in FORM_TYPES, f"form_type must be one of {FORM_TYPES}"
  url=f"{BASE_URL}/submissions/CIK{cik}.json"
  resp=httpx.get(url, headers=HEADERS, timeout=15)
  resp.raise_for_status()
  data=resp.json()

  recent = data.get("filings",{}).get("recent",{})
  forms=recent.get("form",[])
  accessions=recent.get("accessionNumber",[])
  dates = recent.get("filingDate",[])
  primary_docs=recent.get("primaryDocument",[])

  results=[]
  for form,accession,date,doc in zip(forms,accessions,dates,primary_docs):
    if(form==form_type):
      results.append({
           "cik": cik,
                "form_type": form,
                "accession_number": accession,
                "filing_date": date,
                "primary_document": doc,
      })
      if len(results)>=max_results:
        break
  return results

def build_filing_url(cik:str, accession_number:str, primary_document:str) -> str:
  """Build the direct URL to the primary filing document"""
  acc_clean = accession_number.replace("-","")
  return f"{ARCHIVES_BASE_URL}/Archives/edgar/data/{int(cik)}/{acc_clean}/{primary_document}"

def fetch_filing_text(url:str) ->str:
  """Download the raw HTML/text of a filing. Respects EDGAR rate limit"""
  time.sleep(0.11) # EDGAR ToS: max 10 req/s
  resp=httpx.get(url, headers=HEADERS, timeout=30, follow_redirects=True)
  resp.raise_for_status()
  return resp.text

def fetch_filing(ticker:str, form_type: str,year:Optional[int]=None) -> dict:
  """
  High level function: given a ticker + form type (+ optional year), return the most recent matching filing as:
  {
  "ticker": ....,
  "form_type": ...,
  "filing_date": ...,
  "accession_number": ...,
  "raw_html": ...,
  }
  """
  cik=get_cik(ticker)
  filings=get_filings_list(cik,form_type,max_results=20)

  if not filings:
    raise ValueError(f"No {form_type} filings found for {ticker}")
  
  if year:
    filings = [f for f in filings if f["filing_date"].startswith(str(year))]
    if not filings:
      raise ValueError(f"No {form_type} filings found for {ticker} in {year}")
    
  filing = filings[0]
  url = build_filing_url(filing["cik"], filing["accession_number"], filing["primary_document"])
  raw_html=fetch_filing_text(url)

  return{
     "ticker": ticker.upper(),
        "form_type": form_type,
        "filing_date": filing["filing_date"],
        "accession_number": filing["accession_number"],
        "url": url,
        "raw_html": raw_html,
  }