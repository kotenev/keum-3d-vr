#!/usr/bin/env python3
"""Export all 412 symbolic concept instances to SVG, JSON and glTF 2.0."""
import argparse,json,sys
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT/"vector_engine"))
from graph_engine import gltf, validate as validate_graph
from runtime import catalog,instance,validate,svg

def as_graph(model):
    """Bridge keum.concept.v1 -> existing keum.graph.v1 exporter."""
    graph={
      "schema":"keum.graph.v1",
      "preset":f'concept-{model["id"]:04d}',
      "seed":model["parameters"]["seed"],
      "complexity":2,
      "units":"normalized",
      "source_status":"symbolic procedural representation",
      "nodes":[{
          "id":n["id"],"position":n["position"],"kind":n["role"],
          "entity_id":model["id"],"label":n["id"],"group":model["family"]
      } for n in model["nodes"]],
      "edges":[{
          "source":e["source"],"target":e["target"],
          "kind":e["role"],"weight":1,"group":model["family"]
      } for e in model["edges"]],
      "annotations":[],
      "metadata":{"entity_id":model["id"],"category":model["category"],
                  "source_images":model["source"],
                  "coordinate_system":"right-handed; z-up"}
    }
    validate_graph(graph)
    return graph

def export(output,time=0,selected=None):
    output=Path(output);output.mkdir(parents=True,exist_ok=True)
    records=[]
    for item in catalog():
        if selected is not None and item["id"]!=selected:continue
        model=instance(item,time);validate(model);graph=as_graph(model)
        name=f'keum-{item["id"]:04d}'
        (output/(name+".json")).write_text(json.dumps(graph,ensure_ascii=False,indent=2),encoding="utf-8")
        (output/(name+".svg")).write_text(svg(model),encoding="utf-8")
        (output/(name+".gltf")).write_text(json.dumps(gltf(graph)),encoding="utf-8")
        records.append({"id":item["id"],"name":item["name"],"family":model["family"],
                        "json":name+".json","svg":name+".svg","gltf":name+".gltf"})
    if not records:raise ValueError("concept ID not found")
    (output/"manifest.json").write_text(json.dumps(records,ensure_ascii=False,indent=2),encoding="utf-8")
    return len(records)

if __name__=="__main__":
    p=argparse.ArgumentParser()
    p.add_argument("--output",default="build/concepts")
    p.add_argument("--time",type=float,default=0)
    p.add_argument("--id",type=int)
    a=p.parse_args()
    print("exported",export(a.output,a.time,a.id),"models")
