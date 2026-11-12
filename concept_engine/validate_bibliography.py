#!/usr/bin/env python3
"""Check KEUM catalog bibliography integrity without conflating evidence types."""
from __future__ import annotations
import json
from pathlib import Path
from urllib.parse import urlparse

ROOT=Path(__file__).resolve().parents[1]

def validate(catalog,refs):
    if len(catalog)!=493:raise ValueError(f"expected 493 concepts, found {len(catalog)}")
    if len({x["id"] for x in catalog})!=493:raise ValueError("duplicate concept ID")
    ids=[x["id"] for x in catalog]
    if ids!=list(range(1,494)):raise ValueError("concept IDs must be contiguous")
    ref_ids=[r["id"] for r in refs["records"]]
    if len(ref_ids)!=len(set(ref_ids)):raise ValueError("duplicate bibliography ID")
    if refs["count"]!=len(ref_ids):raise ValueError("reference count mismatch")
    known=set(ref_ids)
    for ref in refs["records"]:
        u=urlparse(ref["url"])
        if u.scheme!="https" or not u.netloc:raise ValueError(f"invalid URL {ref['id']}")
        if not ref["source_type"] or not ref["verification"]:raise ValueError(f"unclassified {ref['id']}")
    links=0
    for concept in catalog:
        b=concept.get("bibliography")
        if not isinstance(b,dict):raise ValueError(f"missing bibliography {concept['id']}")
        if not b["reference_ids"]:raise ValueError(f"no references {concept['id']}")
        if len(set(b["reference_ids"]))!=len(b["reference_ids"]):raise ValueError(f"duplicate links {concept['id']}")
        missing=set(b["reference_ids"])-known
        if missing:raise ValueError(f"unknown refs for {concept['id']}: {missing}")
        if b["primary_source_verified"] or b["scientific_evidence_for_claim"]:
            raise ValueError(f"unsupported verified claim {concept['id']}")
        links+=len(b["reference_ids"])
    return {"concepts":len(catalog),"references":len(ref_ids),"thematic_links":links,"verified_claims":0}

def main():
    catalog=json.loads((ROOT/"data/catalog.json").read_text(encoding="utf-8"))
    refs=json.loads((ROOT/"data/references.json").read_text(encoding="utf-8"))
    print(json.dumps(validate(catalog,refs),ensure_ascii=False,indent=2))

if __name__=="__main__":main()
