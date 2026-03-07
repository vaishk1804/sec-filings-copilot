from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, Field
from typing import Optional,Dict, Any
import os

from app.sec_client import fetch_and_store_filing
from app.storage import list_docs, read_doc

app = FastAPI(title="SEC Filings Copilot API", version="0.2.0")

app.add_middleware(
  CORSMiddleware,
  allow_origins=["*"],
  allow_credentials=True,
  allow_methods=["*"],
  allow_headers=["*"],
)

class FetchRequest(BaseModel):
    ticker: str = Field(..., examples=["AAPL"])
    form_type: str = Field(..., examples=["10-K"])
    year: Optional[int] = Field(default=None, examples=[2024])

@app.get("/health")
def health():
  return {"status":"ok"}
@app.get("/version")
def version():
    return {"app": "sec-filings-copilot", "version": "0.2.0", "env": os.getenv("ENV", "local")}

@app.post("/sec/fetch")
async def sec_fetch(req: FetchRequest) -> Dict[str, Any]:
    try:
        rec = await fetch_and_store_filing(req.ticker, req.form_type, req.year)
        # return metadata without dumping all text
        return {
            "doc_id": rec["doc_id"],
            "ticker": rec["ticker"],
            "form": rec["form"],
            "filing_date": rec["filing_date"],
            "accession_number": rec["accession_number"],
            "primary_document": rec["primary_document"],
        }
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))

@app.get("/documents")
def documents():
    return {"documents": list_docs()}

@app.get("/documents/{doc_id}")
def documents_read(doc_id: str):
    try:
        return read_doc(doc_id)
    except FileNotFoundError:
        raise HTTPException(status_code=404, detail="doc_id not found")