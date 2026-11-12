#!/usr/bin/env python3
"""Validate and classify the full KEUM concept catalog without inventing laws."""
from collections import Counter
from pathlib import Path
import json
import argparse

BASE=Path(__file__).resolve().parents[1]
CLASS_RULES={
    "Космология":"ontology",
    "Сакральная геометрия":"geometry",
    "Меркаба и поля":"kinematics",
    "Дыхание и циклы":"oscillator",
    "Энергетическая анатомия":"ontology",
    "Планетарные модели":"astronomy-visualization",
    "Тела Hova":"ontology",
    "ДНК и коды":"symbolic-algebra",
    "Кристаллическое тело":"geometry",
    "Пламена и Eukatharista":"state-machine",
    "Спирали и вихри":"parametric-geometry",
    "Проекции и голография":"projection",
    "Матрицы излучения":"graph-dynamics",
    "Коды и Christos":"symbolic-algebra",
    "Алхимия и символические соответствия":"symbolic-algebra",
    "Психологические модели":"ontology"
}

def compile_ontology(catalog):
    ids=[item["id"] for item in catalog]
    if len(ids)!=len(set(ids)):raise ValueError("duplicate concept IDs")
    if any(not isinstance(i,int) or i<1 for i in ids):raise ValueError("invalid IDs")
    if len(catalog)<412:raise ValueError(f"expected at least 412, got {len(catalog)}")
    unknown=set(x["category"] for x in catalog)-set(CLASS_RULES)
    if unknown:raise ValueError(f"unknown categories: {unknown}")
    return {
        "schema":"keum.ontology.v1",
        "concept_count":len(catalog),
        "category_counts":dict(Counter(x["category"] for x in catalog)),
        "status":"symbolic classification; not 412 empirical scientific theories",
        "concepts":[{
            "id":x["id"],"name":x["name"],"category":x["category"],
            "source":x.get("source"),"description":x.get("description"),
            "formal_family":CLASS_RULES[x["category"]],
            "equation_status":"family-level template only; individual law not established",
            "empirical_status":"not verified"
        } for x in catalog]
    }

def main():
    p=argparse.ArgumentParser()
    p.add_argument("--catalog",default=str(BASE/"data/catalog.json"))
    p.add_argument("--output",default="astronomy/ontology_412.json")
    a=p.parse_args()
    data=json.loads(Path(a.catalog).read_text(encoding="utf-8"))
    result=compile_ontology(data)
    path=Path(a.output);path.parent.mkdir(parents=True,exist_ok=True)
    path.write_text(json.dumps(result,ensure_ascii=False,indent=2),encoding="utf-8")
    print("validated",result["concept_count"],"concepts in",len(result["category_counts"]),"categories")

if __name__=="__main__":main()
