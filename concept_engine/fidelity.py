#!/usr/bin/env python3
"""Geometry verification utilities; source control points must be supplied.

No claim of image fidelity is made when reference points are missing.
"""
from __future__ import annotations
import argparse,json,math
from pathlib import Path

def rmse(reference,predicted):
    if len(reference)!=len(predicted) or not reference:
        raise ValueError("matched non-empty point sets required")
    dim=len(reference[0])
    if any(len(p)!=dim for p in reference+predicted):
        raise ValueError("inconsistent point dimensions")
    return math.sqrt(sum(sum((a-b)**2 for a,b in zip(x,y))
                         for x,y in zip(reference,predicted))/len(reference))

def chamfer(a,b):
    if not a or not b:raise ValueError("non-empty point sets required")
    if any(len(p)!=len(a[0]) for p in a+b):
        raise ValueError("inconsistent dimensions")
    def dist(x,y):return sum((u-v)**2 for u,v in zip(x,y))
    return sum(min(dist(x,y) for y in b) for x in a)/len(a)+sum(min(dist(y,x) for x in a) for y in b)/len(b)

def topology(nodes,edges):
    ids=set(nodes)
    if len(ids)!=len(nodes):raise ValueError("duplicate IDs")
    adj={x:set() for x in ids}
    for a,b in edges:
        if a not in adj or b not in adj:raise ValueError("dangling edge")
        adj[a].add(b);adj[b].add(a)
    seen=set();components=0
    for n in nodes:
        if n in seen:continue
        components+=1;stack=[n]
        while stack:
            x=stack.pop()
            if x in seen:continue
            seen.add(x);stack.extend(adj[x]-seen)
    # multigraph edge count retained, with loops allowed by definition
    return {"vertices":len(nodes),"edges":len(edges),
            "components":components,"cycle_rank":len(edges)-len(nodes)+components}

def compare(record):
    """A source record contains explicit matched reference and generated points."""
    if record.get("reference_points") is None or record.get("model_points") is None:
        return {"status":"unverified","reason":"no matched source control points"}
    ref=record["reference_points"];mod=record["model_points"]
    result={"status":"measured","rmse":rmse(ref,mod),"chamfer":chamfer(ref,mod)}
    if "reference_graph" in record and "model_graph" in record:
        a,b=record["reference_graph"],record["model_graph"]
        ta=topology(a["nodes"],a["edges"]);tb=topology(b["nodes"],b["edges"])
        result["topology_reference"]=ta;result["topology_model"]=tb
        result["cycle_rank_error"]=abs(ta["cycle_rank"]-tb["cycle_rank"])
    return result

def main():
    p=argparse.ArgumentParser()
    p.add_argument("input",help="JSON with reference_points and model_points")
    p.add_argument("--output")
    a=p.parse_args()
    result=compare(json.loads(Path(a.input).read_text(encoding="utf-8")))
    output=json.dumps(result,indent=2,ensure_ascii=False)
    if a.output:Path(a.output).write_text(output,encoding="utf-8")
    else:print(output)

if __name__=="__main__":main()
