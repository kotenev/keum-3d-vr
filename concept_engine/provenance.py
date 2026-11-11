#!/usr/bin/env python3
"""Build a provenance ledger for every concept without fabricating citations."""
import json,argparse
from pathlib import Path
from runtime import catalog
from specializations import OVERRIDES

def ledger(items):
    return {
      "schema":"keum.provenance.v1",
      "concept_count":len(items),
      "status":"unverified until exact image region and original source citation supplied",
      "records":[{
        "id":item["id"],"name":item["name"],
        "source_hint":item.get("source"),
        "source_image_id":None,
        "source_page":None,
        "source_region":None,
        "source_url":None,
        "transcription_verified":False,
        "geometry_verified":False,
        "equations_verified":False,
        "reference_points":None,
        "model_points":None,
        "reviewer":None,
        "reviewed_at":None,
        "model_type":"specialized-interpretive" if item["id"] in OVERRIDES else "generic-family",
        "mathematical_law_status":"not established from primary source"
      } for item in items]
    }

def main():
    p=argparse.ArgumentParser()
    p.add_argument("--output",default="build/provenance_412.json")
    a=p.parse_args()
    out=Path(a.output);out.parent.mkdir(parents=True,exist_ok=True)
    out.write_text(json.dumps(ledger(catalog()),ensure_ascii=False,indent=2),encoding="utf-8")
    print(f"generated {len(catalog())} provenance records")

if __name__=="__main__":main()
