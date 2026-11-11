#!/usr/bin/env python3
"""Validate manual image annotations and compute geometric QA without inventing approvals."""
from __future__ import annotations
import argparse,json,math
from pathlib import Path

ROOT=Path(__file__).resolve().parents[1]
MANIFEST=ROOT/"reconstruction/results/manifest.json"
LINKS=ROOT/"reconstruction/results/concept_image_links_412.json"

def rmse(a,b):
    return math.sqrt(sum((x[0]-y[0])**2+(x[1]-y[1])**2 for x,y in zip(a,b))/len(a))

def chamfer(a,b):
    def d(x,y):return (x[0]-y[0])**2+(x[1]-y[1])**2
    return sum(min(d(x,y) for y in b) for x in a)/len(a)+sum(min(d(x,y) for x in a) for y in b)/len(b)

def verify(record,manifest,links):
    if record.get("schema")!="keum.manual-review.v1":raise ValueError("unknown review schema")
    image_id,concept_id=record.get("image_id"),record.get("concept_id")
    if not isinstance(image_id,int) or not 1<=image_id<=49:raise ValueError("invalid image id")
    if not isinstance(concept_id,int) or not 1<=concept_id<=412:raise ValueError("invalid concept id")
    images={x["image_id"]:x for x in manifest["records"]}
    concepts={x["concept_id"]:x for x in links["records"]}
    if image_id not in images or concept_id not in concepts:raise ValueError("missing source entry")
    size=images[image_id]["original_size"]
    if record.get("image_size")!=size:raise ValueError("source image dimensions mismatch")
    points=record.get("points",{})
    a,b=points.get("reference",[]),points.get("model",[])
    for p in a+b:
        if not isinstance(p,list) or len(p)!=2 or not all(isinstance(v,(int,float)) and math.isfinite(v) for v in p):raise ValueError("invalid point")
        if not 0<=p[0]<=size[0] or not 0<=p[1]<=size[1]:raise ValueError("point outside image")
    status=record.get("status","draft")
    if status not in ("draft","reviewed","verified"):raise ValueError("invalid status")
    if status=="verified":
        if not record.get("reviewer","").strip() or not record.get("notes","").strip():
            raise ValueError("verified needs reviewer and justification")
        if len(a)<3 or len(a)!=len(b):raise ValueError("verified requires >=3 matched control point pairs")
    return {
      "schema":"keum.review-result.v1",
      "image_id":image_id,"concept_id":concept_id,"status":status,
      "source_sha256":images[image_id]["sha256"],
      "catalog_link_status":concepts[concept_id]["link_status"],
      "point_count":len(a),
      "rmse_px":round(rmse(a,b),4) if a and len(a)==len(b) else None,
      "chamfer_px2":round(chamfer(a,b),4) if a and b else None,
      "geometry_verified":status=="verified",
      "scientific_claim_verified":False,
      "warning":"Manual review does not validate metaphysical claims or image semantics."
    }

def main():
    p=argparse.ArgumentParser()
    p.add_argument("review",nargs="+",help="manual review JSON files")
    p.add_argument("--output",default="build/review_results.json")
    a=p.parse_args()
    manifest=json.loads(MANIFEST.read_text(encoding="utf-8"))
    links=json.loads(LINKS.read_text(encoding="utf-8"))
    results=[verify(json.loads(Path(f).read_text(encoding="utf-8")),manifest,links) for f in a.review]
    path=Path(a.output);path.parent.mkdir(parents=True,exist_ok=True)
    path.write_text(json.dumps({"schema":"keum.review-batch.v1","results":results},indent=2,ensure_ascii=False),encoding="utf-8")
    print("checked",len(results),"review records")

if __name__=="__main__":main()
