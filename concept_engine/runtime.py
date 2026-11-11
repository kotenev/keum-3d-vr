#!/usr/bin/env python3
"""KEUM universal symbolic runtime for all 412 catalog entries.

Every entry gets a deterministic, typed model instance. This is an executable
visualization and ontology engine, NOT 412 independently verified physical laws.
Python standard library only.
"""
from __future__ import annotations
import argparse
import hashlib
import json
import math
from pathlib import Path
from xml.etree import ElementTree as ET

BASE=Path(__file__).resolve().parents[1]
CATEGORIES={
 "Космология":"ontology","Сакральная геометрия":"geometry",
 "Меркаба и поля":"kinematics","Дыхание и циклы":"oscillator",
 "Энергетическая анатомия":"ontology","Планетарные модели":"astronomy-visualization",
 "Тела Hova":"ontology","ДНК и коды":"symbolic-algebra",
 "Кристаллическое тело":"geometry","Пламена и Eukatharista":"state-machine",
 "Спирали и вихри":"parametric-geometry","Проекции и голография":"projection",
 "Матрицы излучения":"graph-dynamics","Коды и Christos":"symbolic-algebra"
}
TWO_PI=2*math.pi

def catalog(path=BASE/"data/catalog.json"):
    items=json.loads(Path(path).read_text(encoding="utf-8"))
    if len(items)!=412 or len({x["id"] for x in items})!=412:
        raise ValueError("catalog must contain exactly 412 unique IDs")
    if {x["category"] for x in items}-CATEGORIES.keys():
        raise ValueError("unknown category")
    return sorted(items,key=lambda x:x["id"])

def stable_seed(item):
    return int.from_bytes(hashlib.sha256(f'{item["id"]}:{item["name"]}'.encode()).digest()[:8],"big")

def params(item):
    seed=stable_seed(item)
    return {
        "phase":(seed%360)*math.pi/180,
        "omega":.025+((seed>>9)%120)/2000,
        "radius":1.0+((seed>>17)%140)/100,
        "amplitude":.15+((seed>>27)%45)/100,
        "density":1+(item["id"]-1)%5,
        "count":8+((seed>>35)%9),
        "seed":seed
    }

def point(radius,angle,z=0):
    return [round(radius*math.cos(angle),6),round(radius*math.sin(angle),6),round(z,6)]

def instance(item,t=0.0):
    """One executable, deterministic graph/geometry/state instance."""
    if not math.isfinite(t):raise ValueError("non-finite time")
    p=params(item);kind=CATEGORIES[item["category"]];n=p["count"]
    theta=p["phase"]+p["omega"]*t
    nodes=[];edges=[]
    def add(name,xyz,role="node"):
        nodes.append({"id":name,"position":xyz,"role":role})
    def link(a,b,role="connection"):
        edges.append({"source":a,"target":b,"role":role})
    add("center",[0.,0.,0.],"center")
    if kind in ("geometry","ontology","symbolic-algebra","state-machine"):
        for i in range(n):
            a=theta+TWO_PI*i/n
            r=p["radius"]*(1+.12*math.sin(3*a)) if kind=="geometry" else p["radius"]
            add(f"n{i}",point(r,a),"symbol")
            link("center",f"n{i}","radial")
            if i:link(f"n{i-1}",f"n{i}","cycle")
        link(f"n{n-1}","n0","cycle")
    elif kind in ("kinematics","oscillator","graph-dynamics","astronomy-visualization"):
        for i in range(n):
            a=theta+TWO_PI*i/n
            shift=p["amplitude"]*math.sin(theta+i*TWO_PI/n)
            add(f"n{i}",point(p["radius"]+shift,a,shift),"phase")
            link("center",f"n{i}","coupling")
            if i:link(f"n{i-1}",f"n{i}","ring")
        link(f"n{n-1}","n0","ring")
    elif kind in ("parametric-geometry","projection"):
        for i in range(n):
            a=theta+TWO_PI*i/n
            r=p["radius"]*(.5+i/n)
            add(f"n{i}",point(r,a,p["amplitude"]*math.sin(a*2)),"curve")
            if i:link(f"n{i-1}",f"n{i}","curve")
    else:raise AssertionError(kind)
    return {
      "schema":"keum.concept.v1",
      "id":item["id"],"name":item["name"],"category":item["category"],
      "family":kind,"source":item.get("source"),
      "status":"symbolic procedural representation; no empirical validation",
      "time":t,"parameters":p,"nodes":nodes,"edges":edges,
      "invariants":{"node_count":len(nodes),"edge_count":len(edges),
                    "finite_coordinates":True}
    }

def validate(model):
    ids={n["id"] for n in model["nodes"]}
    if len(ids)!=len(model["nodes"]):raise ValueError("duplicate nodes")
    for n in model["nodes"]:
        if len(n["position"])!=3 or not all(math.isfinite(v) for v in n["position"]):
            raise ValueError("invalid position")
    for e in model["edges"]:
        if e["source"] not in ids or e["target"] not in ids:
            raise ValueError("dangling edge")
    return True

def svg(model,size=900):
    """Pure SVG with safe XML serialization and stable IDs."""
    validate(model)
    root=ET.Element("svg",xmlns="http://www.w3.org/2000/svg",
                    width=str(size),height=str(size),viewBox="-450 -450 900 900")
    ET.SubElement(root,"title").text=f'KEUM #{model["id"]} — {model["name"]}'
    ET.SubElement(root,"desc").text="Symbolic model, not empirical physics"
    ET.SubElement(root,"rect",x="-450",y="-450",width="900",height="900",fill="#071222")
    lookup={n["id"]:n["position"] for n in model["nodes"]}
    scale=340/max(1,max(abs(v) for xyz in lookup.values() for v in xyz[:2]))
    for e in model["edges"]:
        a,b=lookup[e["source"]],lookup[e["target"]]
        ET.SubElement(root,"line",x1=f"{a[0]*scale:.3f}",y1=f"{-a[1]*scale:.3f}",
          x2=f"{b[0]*scale:.3f}",y2=f"{-b[1]*scale:.3f}",
          stroke="#7ecbf4",**{"stroke-width":"1.5","stroke-opacity":".65"})
    for n in model["nodes"]:
        x,y,_=n["position"]
        ET.SubElement(root,"circle",cx=f"{x*scale:.3f}",cy=f"{-y*scale:.3f}",
                      r="7",fill="#ffd27e")
    ET.SubElement(root,"text",x="0",y="-400",fill="#ffffff",
                  **{"text-anchor":"middle","font-size":"18"}).text=f'KEUM {model["id"]}: {model["name"]}'
    return ET.tostring(root,encoding="unicode")

def scene(items,t=0):
    models=[instance(x,t) for x in items]
    for m in models:validate(m)
    return {"schema":"keum.scene.v1","time":t,"count":len(models),
            "models":models,"status":"symbolic executable atlas"}

def main():
    parser=argparse.ArgumentParser()
    parser.add_argument("--id",type=int,help="one concept; default all 412")
    parser.add_argument("--time",type=float,default=0)
    parser.add_argument("--output",default="build/concepts")
    parser.add_argument("--format",choices=["json","svg","both"],default="both")
    args=parser.parse_args()
    items=catalog()
    if args.id is not None:
        items=[x for x in items if x["id"]==args.id]
        if not items:parser.error("unknown concept ID")
    output=Path(args.output);output.mkdir(parents=True,exist_ok=True)
    manifest=[]
    for item in items:
        m=instance(item,args.time);validate(m)
        stem=f'keum-{item["id"]:04d}'
        if args.format in ("json","both"):
            (output/(stem+".json")).write_text(json.dumps(m,ensure_ascii=False,indent=2),encoding="utf-8")
        if args.format in ("svg","both"):
            (output/(stem+".svg")).write_text(svg(m),encoding="utf-8")
        manifest.append({"id":item["id"],"name":item["name"],"family":m["family"],
                         "nodes":len(m["nodes"]),"edges":len(m["edges"])})
    (output/"manifest.json").write_text(json.dumps(manifest,ensure_ascii=False,indent=2),encoding="utf-8")
    print(f"generated {len(items)} concept models in {output}")

if __name__=="__main__":main()
