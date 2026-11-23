#!/usr/bin/env python3
"""Generate reproducible bibliography coverage, role mapping and QA reports."""
from __future__ import annotations
import argparse
import json
from collections import Counter, defaultdict
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
ESOT = ("esoteric", "historical-primary")
SCI = ("scientific", "peer-reviewed", "textbook", "mathematics", "medical", "standard")
def role(ref):
    typ = ref["source_type"].lower()
    domain = ref.get("domain", "").lower()
    if "esoteric" in typ or typ == "historical-primary":
        return "primary_text_not_empirical_proof"
    if "secondary" in typ or "history" in domain or typ.startswith("historical"):
        return "historical_context"
    if any(k in typ for k in SCI):
        return "scientific_method_or_comparison"
    return "thematic_context_unclassified"

def build():
    concepts=json.loads((ROOT/"data/catalog.json").read_text(encoding="utf-8"))
    refs=json.loads((ROOT/"data/references.json").read_text(encoding="utf-8"))
    lookup={r["id"]:r for r in refs["records"]}
    if len(lookup)!=len(refs["records"]): raise ValueError("Duplicate source IDs")
    if refs["count"]!=len(lookup): raise ValueError("Incorrect reference count")
    if len(concepts)!=581 or [x["id"] for x in concepts]!=list(range(1,582)):
        raise ValueError("Concept count or ordering differs from canonical registry")
    rows=[];categories=defaultdict(lambda:{"concepts":0,"links":0})
    for c in concepts:
        bib=c.get("bibliography",{})
        links=bib.get("reference_ids",[])
        if not links or len(set(links))!=len(links): raise ValueError(f"Missing/duplicate bibliography: {c['id']}")
        if any(x not in lookup for x in links): raise ValueError(f"Unknown reference: {c['id']}")
        counts=Counter(role(lookup[x]) for x in links)
        categories[c["category"]]["concepts"]+=1
        categories[c["category"]]["links"]+=len(links)
        rows.append({"id":c["id"],"name":c["name"],"category":c["category"],
                     "reference_ids":links,"roles":dict(counts),
                     "exact_primary_source_verified":bool(bib.get("primary_source_verified")),
                     "scientific_evidence_for_claim":bool(bib.get("scientific_evidence_for_claim")),
                     "source_page":bib.get("source_page")})
    return {"schema":"keum.bibliography.audit.v1","concept_count":len(rows),
            "reference_count":len(lookup),"link_count":sum(len(x["reference_ids"]) for x in rows),
            "exact_primary_sources_verified":sum(x["exact_primary_source_verified"] for x in rows),
            "scientific_claims_verified":sum(x["scientific_evidence_for_claim"] for x in rows),
            "categories":dict(sorted(categories.items())),
            "reference_role_counts":dict(Counter(role(r) for r in lookup.values())),
            "unverified_bibliographic_records":[r["id"] for r in refs["records"]
                 if r.get("verification") in ("bibliographic-search","doi-pointer","institution-homepage")],
            "concepts":rows}

def main():
    p=argparse.ArgumentParser()
    p.add_argument("--check",action="store_true",help="Validate existing generated report without modifying files")
    a=p.parse_args()
    audit=build()
    target=ROOT/"data/bibliography_audit.json"
    serialized=json.dumps(audit,ensure_ascii=False,indent=2)+"\n"
    if a.check:
        if not target.exists() or target.read_text(encoding="utf-8")!=serialized:
            raise SystemExit("Bibliography audit is stale; regenerate it")
    else:
        target.write_text(serialized,encoding="utf-8")
    print(json.dumps({k:v for k,v in audit.items() if k in ("concept_count","reference_count","link_count","exact_primary_sources_verified","scientific_claims_verified")},ensure_ascii=False))
if __name__=="__main__": main()
