# KEUM 412 — executable symbolic concept engine

The runtime loads all 412 entries from `data/catalog.json`, assigns each a deterministic instance from one of 14 mathematical families, and exports editable geometry. This does **not** establish 412 physical theories.

## Generate every model

```bash
python3 concept_engine/runtime.py --output build/concepts
python3 concept_engine/export_all.py --output build/concepts
python3 -m unittest discover -s concept_engine -p 'test_*.py'
```

The export creates `keum-0001.svg`, `keum-0001.json`, `keum-0001.gltf` through `keum-0412.*` and a `manifest.json` index.

## Display a concept in the 3D viewer

Start the local server with `python3 serve.py`, then open:

```text
http://localhost:8000/?graph=keum-0001
```

The browser viewer expects graphs under `vector_engine/graph_exports/`; generate directly there with:

```bash
python3 concept_engine/export_all.py --output vector_engine/graph_exports
```

The existing `src.js` accepts the `keum.graph.v1` JSON files. It does not yet animate all family-specific states or physically validate their meanings.

## Semantics and limits

Each entry has a unique ID, category, source, parameter seed, nodes, edges, mathematical family, and status. Parameters are algorithmic defaults derived from stable SHA-256 hashes of catalog entries. They are **not** values recovered from historical diagrams or measurements.

- `ontology`: rings and typed links
- `geometry`: parametric radial geometry
- `kinematics`: rotating phase networks
- `oscillator`: time-dependent oscillating radii
- `graph-dynamics`: illustrative coupled network geometry
- `astronomy-visualization`: symbolic layout, **not** observational ephemerides
- `symbolic-algebra`: finite indexed structures
- `state-machine`: discrete labels with illustrative ring geometry
- `parametric-geometry`: 3D curves
- `projection`: projected point sequences

To create a source-faithful model, define its exact mathematical law, source, units, parameters and tests individually.
