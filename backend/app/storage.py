import json
import os
from pathlib import Path
from typing import Any, Dict, List


def _raw_dir() -> Path:
    base = Path(os.getenv("DATA_DIR", "data"))
    raw = base / "raw"
    raw.mkdir(parents=True, exist_ok=True)
    return raw


def list_docs() -> List[Dict[str, Any]]:
    raw = _raw_dir()
    docs: List[Dict[str, Any]] = []
    for p in sorted(raw.glob("*.json")):
        try:
            data = json.loads(p.read_text(encoding="utf-8"))
            # keep listing light
            docs.append(
                {
                    "doc_id": data.get("doc_id"),
                    "ticker": data.get("ticker"),
                    "form": data.get("form"),
                    "filing_date": data.get("filing_date"),
                    "accession_number": data.get("accession_number"),
                }
            )
        except Exception:
            continue
    return docs


def read_doc(doc_id: str) -> Dict[str, Any]:
    p = _raw_dir() / f"{doc_id}.json"
    if not p.exists():
        raise FileNotFoundError(doc_id)
    return json.loads(p.read_text(encoding="utf-8"))