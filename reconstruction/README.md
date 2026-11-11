# KEUM 49-source reconstruction — candidate extraction and QA

This module runs **automated geometric candidate extraction** for 49 source images. It does **not** recover a semantically correct vector original automatically, and its edge F1 score must not be reported as source-fidelity accuracy.

## Setup and execution

```bash
python3 -m pip install -r reconstruction/requirements.txt
python3 -m unittest discover -s reconstruction -p 'test_*.py'
python3 reconstruction/pipeline.py --sources /path/to/49/images --output build/reconstruction
```

Use a source folder containing **only** the 49 intended image files in their original order. For this particular source corpus, files `65782.jpg` through `65830.jpg` were processed in ascending order. Original raster images are not committed to GitHub because redistribution rights are not established.

## Output

Each `image_NN/` directory contains `candidates.json`, `candidates.svg`, `overlay.jpg`, and `edges.png`. The root contains `manifest.json` and `QA_REPORT.md`. An image SHA-256 digest links the output to the source image without publishing its pixels.

Open `reconstruction/review.html` locally to inspect candidates over an image. Click a candidate and press Delete to reject it; export a JSON draft. The tool does not automatically promote a candidate to `verified`.

## QA metrics

Edge F1 is computed between Canny edges and the rasterized extracted candidate primitives, within a 3-pixel tolerance. This is **in-sample extraction overlap**, not ground-truth vector accuracy or semantic/topological equivalence. For source-fidelity measurement, manually annotate matching reference and model control points, then run `concept_engine/fidelity.py`.

## Review gate

A reconstruction becomes `verified` only after: (1) source provenance confirmed; (2) manual topology and text labels checked; (3) geometric alignment and scale normalized; (4) independent metrics computed; (5) reviewer and date recorded. All 49 remain `unverified` at this stage.