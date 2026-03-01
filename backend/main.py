from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
import os

app = FastAPI(title="SEC Filings Copilot API", version="0.1.0")

app.add_middleware(
  CORSMiddleware,
  allow_origins=["*"],
  allow_credentials=True,
  allow_methods=["*"],
  allow_headers=["*"],
)

@app.get("/health")
def health():
  return {"status":"ok"}

@app.get("/version")
def version():
  return{
    "app":"sec-filings-copilot",
    "version": "0.1.0",
    "env": os.getenv("ENV","local"),
  }