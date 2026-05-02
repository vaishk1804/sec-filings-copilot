# backend/test/test_edgar_fetcher.py

import pytest
from app.pipeline.edgar_fetcher import get_cik, get_filings_list, fetch_filing

def test_get_cik_apple():
  cik=get_cik("AAPL")
  assert cik == "0000320193"

def test_get_filings_list():
  cik=get_cik("MSFT")
  filings= get_filings_list(cik,"10-K", max_results=3)
  assert len(filings)>=1
  assert filings[0]["form_type"] == "10-K"

def test_fetch_filing_aapl():
  result=fetch_filing("AAPL", "10-K", year=2023)
  assert result["ticker"]=="AAPL"
  assert len(result["raw_html"]) > 10000 # real filing data is huge
  print(f"\nFetched AAPL 10-K filed {result['filing_date']}, {len(result['raw_html']):,} chars")