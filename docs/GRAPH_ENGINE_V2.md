# KEUM Graph Engine v2 — unified procedural geometry

## Architecture

The shared **keum.graph.v1** schema is the source of truth for nodes, links, 3D coordinates, semantic entity IDs, groups, and traceability metadata. Both SVG and glTF are projections of this graph; the browser studio can edit the graph and export either representation. The VR scene can load the edited graph from the browser studio or built-in preset JSON.

**Model is symbolic.** Its laws are design axioms, not validated physical laws. Images are interpreted, not exact vector tracings. The 412-entry catalogue is a separate glossary and **does not imply 412 distinct geometries**.

## Core schema

```json
{"schema":"keum.graph.v1","preset":"kathara","units":"normalized","nodes":[{"id":"K1","position":[0,-4.5,0],"kind":"signet","entity_id":21,"label":"1","group":"base"}],"edges":[],"annotations":[],"metadata":{"entity_id":21}}
```

- `nodes[].id`: unique immutable ID.
- `nodes[].position`: finite three-dimensional vector in normalized units.
- `nodes[].entity_id`: lookup into `data/catalog.json`; semantic association, not proof.
- `edges[].source/target`: existing node IDs; `kind`, `weight`, `group` for rendering.
- `metadata.source_images`: conceptual attribution only unless verified against a page.

## Mathematics

Graph adjacency matrix: \(A_{ij}=w_{ij}\) if connected, otherwise zero. Graph Laplacian: \(L=D-A\). For a scalar node signal \(u\), a stable diffusion model is \(\dot u=-\kappa Lu\), with \(\kappa\ge0\); for an undirected graph, \(\sum_i u_i\) is conserved. The viewer's PCM/PKA rotation is \(R_z(\omega t)\) and \(R_z(-\eta\omega t)\); it is a visual animation, not a dynamical solution. Projection onto an SVG plane is \(P_{xy}(x,y,z)=(x,y)\), and alternatives \(P_{xz}\), \(P_{yz}\). Deterministic geometric generation uses fixed index-based angles \(\theta_i=2\pi i/n\). A normalized 15D-to-3D projection can be added as a configurable linear matrix \(P\in\mathbb R^{3\times15}\), but is not yet inferred from historical diagrams.

## Reproducible commands

```bash
cd KEUM_VR
python3 vector_engine/graph_engine.py --preset all --output vector_engine/graph_exports
python3 -m unittest discover -s vector_engine -p 'test_*.py'
python3 serve.py
```

Visit `/vector_engine/editor.html` for live drag-to-edit geometry. Use SVG / JSON / glTF export; the glTF contains 3D line primitives (`mode=1`), so choose a viewer that supports line primitives. The existing `/index.html` uses Three.js from a CDN and requires an internet connection for that dependency.

## Accuracy and remaining work

The current graph representations are reusable, editable procedural interpretations. Accurate digitization of the 49 source plates requires verified control points and topology per plate, plus a traceability review. Physical claims about energy, DNA, healing, or dimensional travel are not established by this simulation. No claim of numerical simulation of all 412 glossary concepts is made.

## Semantic crosswalk

`data/entity_geometry_index.json` maps all glossary IDs to a primary procedural geometry family and optional secondary families. **Mappings are heuristic, explicitly low-confidence, and must not be mistaken for source-verified diagram reconstructions.** The 12 graph families are templates; many concepts share a geometry family.