# ChronoCTI report explorer

A FastAPI + Angular workspace for turning CTI report text into an evidence-backed entity graph.

## Run

From the repository root, using the existing Python environment:

```sh
venv/bin/python web-server/run.py
```

Open http://localhost:8000. Use **Try an example**, paste a report, or import a `.txt` / `.md` file, then choose **Build knowledge graph**. Imported files are shown for review before submission.

The production frontend is included in `static/browser/`. To rebuild after frontend changes:

```sh
cd web-server/frontend
npm install
npm run build
```

For development, `npm start` serves Angular on port 4200 and proxies API requests to port 8000. The production app uses same-origin API requests.

## Graph behavior

- Violet cards represent unique ATT&CK techniques; green cards represent asset **categories**, not individual machines.
- Repeated mentions share a card, with occurrence counts and all supporting sentences preserved.
- Dashed **co-mentioned** links mean a technique and asset were extracted from the same sentence. They do not establish a verified targeting relationship.
- Directed **next mention** links record the sequence of technique-bearing sentences. They do not establish execution order or causality. Recurring techniques can create cycles.
- These relationships are constructed from report evidence; the offline GNN/XGBoost temporal models are not used by this web endpoint.
- Select a card or relationship to see its evidence. Search highlights matching IDs/names; filters hide assets or narrative links. Drag to pan, scroll to zoom, and use **Fit** for a complete overview.
- SVG/PNG exports include the visible entity categories and relationship filters, with full graph bounds. JSON exports the complete graph, including evidence and detection provenance.
- The backend uses the available trained classifiers and supplements them with keyword rules. Keyword scores are fixed rule values, not calibrated probabilities. Both types respect the requested threshold.

## API

- `POST /api/analyze`: `{ "text": "...", "report_name": "...", "asset_threshold": 0.5, "technique_threshold": 0.5 }`
- `POST /api/upload`: multipart file input, processed as UTF-8 text.
- `GET /api/assets/taxonomy`, `GET /api/techniques/taxonomy`
- `GET /api/health`
- `/docs`: interactive API documentation.

Analysis returns `summary`, `assets`, `techniques`, `sentences`, and `attack_flow`. Graph nodes include `evidence`, `prediction_sources`, and `occurrence_count`; edges include `evidence` and `basis`.

Legacy scenario routes remain in the backend but are not used by this interface and still refer to unimplemented scenario generators.

## Checks

From the repository root:

```sh
venv/bin/python -m unittest discover -s web-server/backend -p test_graph.py
HF_HUB_OFFLINE=1 TRANSFORMERS_OFFLINE=1 venv/bin/python web-server/backend/test_api.py
npm run build --prefix web-server/frontend
```

The API integration check loads the local trained models. The graph unit tests do not require model inference.
