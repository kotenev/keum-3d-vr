#!/usr/bin/env python3
"""Process the ten user-supplied diagrams as KEUM image IDs 50–59."""
from pathlib import Path
import argparse,json
from pipeline import list_sources,process

ROOT=Path(__file__).resolve().parents[1]
DEFAULT_SOURCES=ROOT/"reconstruction/sources/additional_10"

def main():
    p=argparse.ArgumentParser()
    p.add_argument("--sources",type=Path,default=DEFAULT_SOURCES)
    p.add_argument("--output",type=Path,default=ROOT/"build/reconstruction_50_59")
    p.add_argument("--max-side",type=int,default=1100)
    args=p.parse_args()
    files=list_sources(args.sources)
    if len(files)!=10:raise ValueError(f"expected 10 new originals, found {len(files)}")
    args.output.mkdir(parents=True,exist_ok=True)
    records=[]
    for i,path in enumerate(files,start=50):
        records.append(process(path,args.output/f"image_{i:02d}",i,args.max_side))
    manifest={"schema":"keum.reconstruction.additional.v1",
              "image_id_range":[50,59],"count":len(records),
              "verified_count":0,"records":records,
              "status":"automatic candidates; manual review pending"}
    (args.output/"manifest.json").write_text(json.dumps(manifest,indent=2,ensure_ascii=False),encoding="utf-8")
    print("processed",len(records),"new diagrams; output",args.output)

if __name__=="__main__":main()
