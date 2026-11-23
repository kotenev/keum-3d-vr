#!/usr/bin/env python3
"""KEUM automated bibliographic reconciliation (stdlib only).

Queries Crossref for DOI-bearing records and Open Library for books.
Candidate matches are *suggestions*, never evidence that a KEUM claim is true.
No external data changes the canonical registry automatically.
"""
from __future__ import annotations
import argparse
import difflib
import json
import re
import time
import urllib.error
import urllib.parse
import urllib.request
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
USER_AGENT = "KEUM-Bibliography-Audit/1.0 (research; github.com/kotenev/keum-3d-vr)"
DOI_RE = re.compile(r"10\.\d{4,9}/[^\s]+", re.I)

def norm(s):
    return " ".join(re.findall(r"[a-z0-9]+", str(s).lower()))

def similarity(a, b):
    return round(difflib.SequenceMatcher(None, norm(a), norm(b)).ratio(), 4)

def get_json(url, timeout=18, retries=2):
    req = urllib.request.Request(url, headers={"User-Agent": USER_AGENT, "Accept": "application/json"})
    for attempt in range(retries + 1):
        try:
            with urllib.request.urlopen(req, timeout=timeout) as res:
                return json.load(res)
        except (urllib.error.HTTPError, urllib.error.URLError, TimeoutError, ValueError) as e:
            if attempt == retries or isinstance(e, urllib.error.HTTPError) and e.code in (400, 401, 403, 404):
                return {"_error": str(e)}
            time.sleep(1.5 * (attempt + 1))
    return {"_error": "unknown"}

def year_from_crossref(msg):
    for key in ("published", "issued", "created"):
        try:
            return str(msg[key]["date-parts"][0][0])
        except (KeyError, IndexError, TypeError): pass
    return ""

def candidates(ref, timeout):
    title, author = ref["title"], ref.get("author", "")
    url = ref.get("url", "")
    doi = DOI_RE.search(urllib.parse.unquote(url)) if "doi.org" in url else None
    if doi:
        data = get_json("https://api.crossref.org/works/" + urllib.parse.quote(doi.group(0), safe="/"), timeout)
        msg = data.get("message")
        if isinstance(msg, dict):
            yield {"provider":"crossref-doi","title":(msg.get("title") or [""])[0],
                   "author":" ".join(x.get("family","") for x in msg.get("author",[])),
                   "year":year_from_crossref(msg),"doi":msg.get("DOI"),"url":msg.get("URL"),"record_type":msg.get("type")}
        else:
            yield {"provider":"crossref-doi","error":data.get("_error","no result")}
        return
    if "bibliographic-search" != ref.get("verification"): return
    if any(k in ref.get("source_type","").lower() for k in ("textbook","book","primary","secondary","historical")):
        q=urllib.parse.urlencode({"title":title,"limit":3,"fields":"key,title,author_name,first_publish_year,edition_key"})
        data=get_json("https://openlibrary.org/search.json?"+q,timeout)
        for doc in data.get("docs",[])[:3]:
            yield {"provider":"openlibrary","title":doc.get("title",""),
                   "author":", ".join(doc.get("author_name",[])[:3]),
                   "year":str(doc.get("first_publish_year","")),
                   "url":"https://openlibrary.org"+doc["key"] if doc.get("key","").startswith("/works/") else None}
        if "_error" in data: yield {"provider":"openlibrary","error":data["_error"]}

def score(ref, candidate):
    title=similarity(ref["title"],candidate.get("title",""))
    author=similarity(ref.get("author",""),candidate.get("author",""))
    year=str(ref.get("year",""))
    exact_year=year.isdigit() and year == candidate.get("year")
    return {"title_similarity":title,"author_similarity":author,"year_exact":exact_year,
            "score":round(0.75*title+0.2*author+0.05*int(exact_year),4)}

def reconcile(refs, online=False, timeout=18, pause=0.35, limit=0):
    out=[]
    for ref in refs:
        entry={"reference_id":ref["id"],"original":{"author":ref.get("author"),"title":ref["title"],
                "year":ref.get("year"),"url":ref.get("url"),"verification":ref.get("verification")},
                "candidates":[],"decision":"manual_review_required"}
        if online and (not limit or len(out)<limit):
            for candidate in candidates(ref,timeout):
                if "error" not in candidate: candidate["match"]=score(ref,candidate)
                entry["candidates"].append(candidate)
            if entry["candidates"]: time.sleep(pause)
        entry["candidates"].sort(key=lambda c:c.get("match",{}).get("score",0),reverse=True)
        top=next((c for c in entry["candidates"] if "match" in c),None)
        if top:
            m=top["match"]
            entry["decision"]="high_confidence_candidate_not_verified" if m["title_similarity"]>=0.94 and m["score"]>=0.84 else "ambiguous_candidate_manual_review"
        elif online: entry["decision"]="no_candidate_or_lookup_failed"
        else: entry["decision"]="not_queried_offline"
        out.append(entry)
    return out

def main():
    p=argparse.ArgumentParser()
    p.add_argument("--online",action="store_true",help="Allow outbound Crossref/Open Library requests")
    p.add_argument("--limit",type=int,default=0,help="Only query first N references (0=all)")
    p.add_argument("--timeout",type=int,default=18)
    p.add_argument("--pause",type=float,default=0.35)
    p.add_argument("--output",default="build/bibliography/reconciliation.json")
    args=p.parse_args()
    if args.limit<0 or args.pause<0: p.error("limit and pause must be non-negative")
    data=json.loads((ROOT/"data/references.json").read_text(encoding="utf-8"))
    rows=reconcile(data["records"],args.online,args.timeout,args.pause,args.limit)
    output=Path(args.output)
    output.parent.mkdir(parents=True,exist_ok=True)
    payload={"schema":"keum.bibliography.reconciliation.v1","mode":"online" if args.online else "offline",
             "policy":"suggestions only; never auto-promote primary_source_verified or scientific_evidence_for_claim",
             "records":rows}
    output.write_text(json.dumps(payload,ensure_ascii=False,indent=2)+"\n",encoding="utf-8")
    from collections import Counter
    print(json.dumps({"records":len(rows),"decisions":dict(Counter(r["decision"] for r in rows)),"output":str(output)},ensure_ascii=False))
if __name__=="__main__": main()
