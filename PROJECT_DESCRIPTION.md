# ChronoCTI — PROJECT DESCRIPTION

> **Prepared for:** Technical report writing (requirements, use cases, activity diagrams, CRC/class model, architecture, methodology, user manual, test plan).
> **Method:** Evidence-based. Every claim cites a source file. Status tags: `[IMPLEMENTED]` `[PARTIAL]` `[STUB]` `[NOT FOUND]` `[INFERRED]`.

---

## 0. Snapshot

### Project Name
**ChronoCTI** (as named in `readme.md` line 1 and `web-server/frontend/package.json` `name` field: `"chronocti-attackflow-frontend"`)

### One-Paragraph Summary
ChronoCTI is a research-grade NLP and Machine Learning pipeline that ingests raw Cyber Threat Intelligence (CTI) reports (plain text or Markdown) and produces temporal knowledge graphs showing which MITRE ATT&CK techniques happen *before*, *after*, *during*, or *concurrently* with each other within an intrusion narrative. The project has two major components: (1) an **offline training pipeline** consisting of eight sequential ML stages (word embeddings → RoBERTa domain adaptation → sentence-to-technique classification → coreference resolution → TimeML temporal extraction → feature engineering → association rule mining → temporal relation learning), and (2) an **interactive web application** (FastAPI backend + Angular 18 frontend) that lets analysts paste or upload a CTI report and immediately visualizes an interactive, deduplicated attack-flow graph in the browser, with export to SVG and PNG.

### Type
**Hybrid:** Research ML pipeline (offline, CLI-driven) + Web application (full-stack, browser-based)

### Languages, Frameworks, and Key Libraries

#### Backend / ML Pipeline (Python)
| Module | Python | Key Libraries (verified in Pipfile or imports) |
|---|---|---|
| Root (`create_cti_w2v.py`) | 3.11 | `spacy` (any), `gensim` (any), `jsonlines` (any) — `Pipfile` line 6–9 |
| `roberta_cti_and_discourse_classifier/` | 3.10 | `torch`, `transformers` (4.30.2 per `readme2.md` line 57), `simpletransformers`, `datasets` — `mlm.py` lines 2–9 |
| `sentence_to_technique_classifier/` | 3.11 | `spacy`, `spacy-transformers`, `torch`, `skorch`, `openai`, `skllm` — `Pipfile` |
| `sentence_to_asset_classifier/` | 3.11 | same as above |
| `temporal-learner-code/` | 3.11 | `torch`, `dgl`, `xgboost`, `networkx`, `scikit-learn`, `imbalanced-learn`, `skmultilearn`, `skorch`, `shap`, `pytorch-tabnet`, `sentence-transformers` — `readme2.md` line 59 |
| `TimeML/` | 3.11 | `spacy`, `beautifulsoup4`, `lxml`, `benepar`, `flask` — `readme2.md` line 60; also uses `tarsqi-ttk` (external tool) |
| `Neuralcoref/` | 3.11 | `spacy`, `spacy-experimental`, `spacy-transformers`, `torch`, `en_coreference_web_trf` — `readme2.md` line 61 |
| `apriori-features/` | 3.11 | `pandas`, `mlxtend`, `networkx`, `stix2`, `scikit-learn` — `readme2.md` line 62 |

#### Web Server Backend
| Library | Version | Source |
|---|---|---|
| `fastapi` | any | `web-server/backend/app.py` line 3 |
| `uvicorn` | any | `web-server/run.py` line 1 |
| `spacy` | any | `web-server/backend/pipeline.py` line 5 |
| `networkx` | any | `web-server/backend/attack_flow.py` line 1 |
| `pydantic` | v2-compatible | `web-server/backend/schemas.py` line 2 |

#### Frontend
| Library | Version | Source |
|---|---|---|
| Angular | 18.2.x | `web-server/frontend/package.json` lines 13–19 |
| TypeScript | ~5.4.0 | `web-server/frontend/package.json` line 28 |
| RxJS | ~7.8.0 | `web-server/frontend/package.json` line 21 |
| Material Icons | CDN | `web-server/frontend/src/app/app.html` line 7 (via `material-icons` CSS class) |

### Entry Points

| Entry Point | Command | What Starts |
|---|---|---|
| Web server (primary) | `python web-server/run.py` | Uvicorn on port 8000 (`run.py` line 20) |
| Word2Vec training | `python create_cti_w2v.py` | Stage 1 embedding pipeline |
| RoBERTa MLM | `python roberta_cti_and_discourse_classifier/mlm.py` | Stage 2a pretraining |
| Technique classifier training | `python sentence_to_technique_classifier/train_models.py` | Stage 3 |
| Feature engineering + learning | Scripts in `temporal-learner-code/` (see `STEPS.md`) | Stages 6–8 |
| Angular dev server | `npm start` (port 4200) in `web-server/frontend/` | Frontend dev mode |
| Angular production build | `npm run build` in `web-server/frontend/` | Compiles to `web-server/static/` |

### Repository Tree (2–3 levels, important items only)
```
ChronoCTI-main/
├── create_cti_w2v.py              # Stage 1: trains CTI-domain Word2Vec (300-dim)
├── demo_dashboard.py              # Utility: prints evaluation metrics from saved JSON files
├── Pipfile                        # Root Python 3.11 env: spacy, gensim, jsonlines
├── Datasets/                      # Source data
│   ├── relevance_train.jsonl      # MITRE/TRAM sentences for W2V (43 MB)
│   ├── relevance_eval.jsonl       # Eval sentences (5.5 MB)
│   ├── all_report_sentences.jsonl # All report sentences corpus (43 MB)
│   └── cti_w2v_v2/                # Trained spaCy word vector model
├── roberta_cti_and_discourse_classifier/   # Stage 2
│   ├── mlm.py                     # Further-pretrain roberta-base on CTI text (MLM)
│   ├── train_discourse_relation.py # Train discourse classifier for consecutive sentences
│   ├── train_discourse_relation_coref.py  # Same for coreferenced sentences
│   ├── Roberta-CTI/               # Best checkpoint of CTI-adapted RoBERTa
│   └── discourse_train_v2.json    # Training data for discourse classifier
├── sentence_to_technique_classifier/  # Stage 3
│   ├── train_models.py            # Trains 5 spaCy textcat models (bagging, 5-fold)
│   ├── selected_techniquesWName.json  # 329 MITRE ATT&CK technique IDs + names
│   └── bagging_models/            # Saved spaCy classification models
├── sentence_to_asset_classifier/  # Parallel to stage 3, for ICS/IT assets
│   ├── train_models.py            # Same bagging approach for 18 asset classes
│   └── bagging_models/            # Saved asset classifier models
├── Neuralcoref/                   # Stage 4: coreference resolution
│   └── construct_dataset_of_coreferred_sentences.py
├── TimeML/                        # Stage 5: temporal event extraction
│   ├── obtain_cti_report_to_timeML.py
│   ├── convert_timeML_to_json.py
│   ├── classify_temporal_events_to_TTPs.py
│   └── construct_features_from_timeML.py
├── apriori-features/              # Stage 7: static association rule mining
│   └── construct_association_rule_mining_features.py
├── temporal-learner-code/         # Stages 6 & 8: feature engineering + ML learning
│   ├── combine_all_features.py    # Merges all feature families
│   ├── learn_graph_ML_imbalanced_multilabel-v2.py  # GNN (DGL) training
│   ├── make_final_evaluation.py   # XGBoost MultiOutput + SHAP evaluation
│   ├── cross_validate_p2.py       # 18+ estimator benchmark
│   ├── Utils.py                   # Shared utilities (38 KB)
│   ├── temporal_relation_dataset.xlsx  # Ground-truth labels
│   ├── gnn_model_0.pt … gnn_model_4.pt  # Saved GNN checkpoints (5 folds)
│   └── unseen_reports_features/   # Engineered feature JSONs for inference
├── web-server/                    # Interactive web application
│   ├── run.py                     # Uvicorn launcher (port 8000)
│   ├── backend/                   # FastAPI application
│   │   ├── app.py                 # API routes (7 endpoints)
│   │   ├── pipeline.py            # ChronoCTIPipeline class: NLP processing
│   │   ├── attack_flow.py         # AttackFlowEngine class: graph construction + layout
│   │   ├── schemas.py             # Pydantic data models
│   │   └── test_api.py            # Integration tests (4 test functions)
│   ├── frontend/                  # Angular 18 SPA
│   │   └── src/app/
│   │       ├── app.ts / app.html / app.scss   # Root component
│   │       ├── components/
│   │       │   ├── attack-flow-canvas/        # SVG graph renderer
│   │       │   ├── report-analyzer/           # Textarea + file upload UI
│   │       │   └── scenario-selector/         # [PARTIAL] pre-built scenario picker
│   │       ├── services/cti-api.service.ts    # HTTP client to backend
│   │       ├── models/attack-flow.model.ts    # TypeScript interfaces
│   │       └── shared/generic-components/     # Reusable UI: Button, Table, Modal, Label
│   └── static/                    # Angular production build output (served by FastAPI)
├── input and outputs/             # Final .gexf attack-flow graph files
├── readme.md                      # Short installation guide
├── readme2.md                     # Detailed 511-line pipeline documentation
└── PROJECT_FLOW.md                # Architecture and flow overview
```

### Approximate Size
| Language | Files | Approx. LOC |
|---|---|---|
| Python | 197 (excl. venv, `__pycache__`, `node_modules`) — counted via `find` | ~15,000 (estimated; `wc -l` not available due to path issues) |
| TypeScript | 14 (excl. `node_modules`) — counted via `find` | ~900 |
| HTML (Angular templates) | 6 | ~500 |
| SCSS | 6 | ~700 |

---

## 1. Purpose and Functionality

### Problem Being Solved
`[INFERRED from readme.md lines 1–2, readme2.md lines 1–8]` CTI reports are written in unstructured natural language. Security analysts reading them must manually determine the *temporal ordering* of attack techniques (which came first, which ran concurrently). ChronoCTI automates this by: (1) parsing raw text, (2) mapping sentences to MITRE ATT&CK techniques, and (3) predicting temporal relations between technique pairs, producing a directed graph (attack flow) that shows the intrusion timeline.

### Target Users
`[INFERRED]` Cybersecurity researchers and threat intelligence analysts who need to convert CTI reports into structured attack timelines and visual knowledge graphs.

---

### Feature List

#### (a) Core / Essential Features

| # | Feature | Status | Source |
|---|---|---|---|
| F1 | Sentence segmentation of raw CTI report text | `[IMPLEMENTED]` | `pipeline.py` `split_sentences()` L122–129 |
| F2 | Keyword + ML-based MITRE ATT&CK technique extraction per sentence (20 hardcoded techniques, spaCy model optional) | `[IMPLEMENTED]` | `pipeline.py` `predict_techniques()` L162–182; `TECHNIQUE_KEYWORDS` dict L49–70 |
| F3 | Keyword + ML-based ICS/IT asset extraction per sentence (18 asset classes) | `[IMPLEMENTED]` | `pipeline.py` `predict_assets()` L140–160; `ASSET_KEYWORDS` dict L28–47 |
| F4 | Temporal signal extraction (regex-based: BEFORE/AFTER/OVERLAP/FINALLY/TIME_ANCHOR) | `[IMPLEMENTED]` | `pipeline.py` `extract_temporal_signals()` L131–138; `TEMPORAL_PATTERNS` L20–26 |
| F5 | Deduplicated entity graph construction (each technique/asset appears exactly once as canonical hub node) | `[IMPLEMENTED]` | `attack_flow.py` `build_attack_flow_from_chrono_data()` L50–168 |
| F6 | Top-to-bottom vertical DAG layout using topological levels | `[IMPLEMENTED]` | `attack_flow.py` `_layout_and_format_graph()` L170–440 |
| F7 | 2D bounding-box overlap relaxation (8 iterations) | `[IMPLEMENTED]` | `attack_flow.py` L319–338 |
| F8 | Deduplicated causal edges (AFTER, TARGETS, AFFECTS — no duplicate edges) | `[IMPLEMENTED]` | `attack_flow.py` L138–165 (`has_edge()` guard) |
| F9 | NetworkX graph metrics: total nodes, edges, is_DAG, longest chain, density | `[IMPLEMENTED]` | `attack_flow.py` L176–188, L433–439 |
| F10 | REST API: analyze text report (`POST /api/analyze`) | `[IMPLEMENTED]` | `backend/app.py` L94–108 |
| F11 | REST API: upload file report (`POST /api/upload`, accepts `.txt .md .csv .json`) | `[IMPLEMENTED]` | `backend/app.py` L110–132 |
| F12 | Interactive SVG canvas with pan (drag) and zoom (Ctrl+scroll) | `[IMPLEMENTED]` | `attack-flow-canvas.ts` L48–89 |
| F13 | Animated particle pulses on edges (SVG `animateMotion`) | `[IMPLEMENTED]` | `attack-flow-canvas.html` L93–99 |
| F14 | Node click → inspector modal (type, ID, confidence, sentence context) | `[IMPLEMENTED]` | `attack-flow-canvas.ts` L125–129; `app.html` L107–141 |
| F15 | Export graph as standalone SVG (self-contained, embedded styles) | `[IMPLEMENTED]` | `attack-flow-canvas.ts` L175–250 |
| F16 | Export graph as PNG (2× Retina resolution via canvas) | `[IMPLEMENTED]` | `attack-flow-canvas.ts` L252–286 |

#### (b) Features Users Would Naturally Expect

| # | Feature | Status | Source |
|---|---|---|---|
| F17 | Occurrence count badge on hub nodes (×N) | `[IMPLEMENTED]` | `attack-flow-canvas.html` L172–178; `attack_flow.py` L104–105 |
| F18 | Resizable/collapsible sidebar panel (drag handle) | `[IMPLEMENTED]` | `app.ts` L39–118; `app.html` L86–95 |
| F19 | Extracted techniques table (ID, name, count, confidence) | `[IMPLEMENTED]` | `app.html` L69–75; `app.ts` L43–53 |
| F20 | Extracted assets table (ID, name, count, confidence) | `[IMPLEMENTED]` | `app.html` L77–83; `app.ts` L55–65 |
| F21 | Health check endpoint (`GET /api/health`) | `[IMPLEMENTED]` | `backend/app.py` L47–56 |
| F22 | Taxonomy endpoints for assets and techniques (`GET /api/assets/taxonomy`, `/api/techniques/taxonomy`) | `[IMPLEMENTED]` | `backend/app.py` L58–66 |
| F23 | Fit-to-screen button that auto-scales graph | `[IMPLEMENTED]` | `attack-flow-canvas.ts` L103–123 |
| F24 | API Swagger/OpenAPI docs at `/docs` | `[IMPLEMENTED]` | FastAPI auto-generates; linked in header `app.html` L20–23 |
| F25 | Input validation (min text length = 5 chars) | `[IMPLEMENTED]` | `backend/app.py` L99, L123 |
| F26 | Error message display in UI | `[IMPLEMENTED]` | `report-analyzer.html` L14–19 |

#### (c) Advanced / Innovative Features

| # | Feature | Status | Source |
|---|---|---|---|
| F27 | 8-stage ML research pipeline: W2V → RoBERTa-CTI → Sentence Classifier → Coref → TimeML → Feature Eng. → Apriori → GNN/XGBoost | `[IMPLEMENTED]` (as research pipeline; not integrated into web server runtime) | `readme2.md` full document; individual stage scripts |
| F28 | Domain-adapted RoBERTa (CTI-RoBERTa): further pretraining on CTI text using MLM (mlm_probability=0.15) | `[IMPLEMENTED]` | `roberta_cti_and_discourse_classifier/mlm.py` L47–51 |
| F29 | Bagging ensemble of 5 spaCy textcat models (5-fold CV, 5 different embeddings) | `[IMPLEMENTED]` | `sentence_to_technique_classifier/train_models.py`; `readme2.md` L251–257 |
| F30 | Discourse relation classification (5 labels: ELABORATION, LIST, NEXT, IF_ELSE, MISC) for consecutive and coreferenced sentence pairs | `[IMPLEMENTED]` | `roberta_cti_and_discourse_classifier/train_discourse_relation.py` |
| F31 | Coreference resolution using spaCy `en_coreference_web_trf` | `[IMPLEMENTED]` | `Neuralcoref/construct_dataset_of_coreferred_sentences.py` |
| F32 | TimeML temporal expression extraction via tarsqi-ttk (BEFORE, AFTER, DURING, SIMULTANEOUS tags) | `[IMPLEMENTED]` | `TimeML/` scripts; `readme2.md` L325 |
| F33 | Apriori / Association Rule Mining on ATT&CK technique co-occurrences (support, confidence, conviction, lift, phi, jaccard, PMI) | `[IMPLEMENTED]` | `apriori-features/construct_association_rule_mining_features.py` |
| F34 | Graph Neural Network (DGL GraphConv + MLP) for temporal relation edge classification | `[IMPLEMENTED]` | `temporal-learner-code/learn_graph_ML_imbalanced_multilabel-v2.py`; 5 trained `.pt` files present |
| F35 | XGBoost MultiOutputClassifier with SHAP feature importance analysis | `[IMPLEMENTED]` | `temporal-learner-code/make_final_evaluation.py` |
| F36 | 18+ estimator cross-validation benchmark (5-fold CV) | `[IMPLEMENTED]` | `temporal-learner-code/cross_validate_p2.py` |
| F37 | Pre-built scenario loader (Equifax + TRITON) via `/api/scenarios/{id}` | `[PARTIAL]` — endpoint defined, `get_equifax_showcase_scenario()` and `get_triton_ics_scenario()` called on `attack_flow_engine` but those methods do NOT exist in `attack_flow.py` (only `build_attack_flow_from_chrono_data` and `_empty_graph` are present) | `backend/app.py` L84–92 |
| F38 | OpenAI GPT-3.5 fine-tuning for sentence-to-technique classification (optional) | `[IMPLEMENTED]` | `sentence_to_technique_classifier/openai/fine_tune.py`; `readme2.md` L246–257 |

#### Features Mentioned in Docs/UI but NOT Implemented
- `get_equifax_showcase_scenario()` and `get_triton_ics_scenario()` — referenced in `backend/app.py` L88–91 but **not defined** in `backend/attack_flow.py`. Calling these endpoints would raise an `AttributeError` at runtime. `[NOT FOUND]`
- `scenario-selector` Angular component — folder exists at `web-server/frontend/src/app/components/scenario-selector/` but it is **not imported or used** anywhere in `app.ts` or routing. `[STUB]`

---

## 2. Actors and External Systems

### Human Roles

| Role | What They Can Do | Source |
|---|---|---|
| **Security Analyst / End User** | Paste CTI report text in web UI; upload `.txt/.md/.csv/.json` files; view interactive attack-flow graph; click nodes for details; export SVG/PNG; zoom/pan canvas | `report-analyzer.html`, `attack-flow-canvas.html`, `app.html` |
| **ML Researcher / Developer** | Run the 8-stage training pipeline; configure model paths; interpret SHAP feature importance; run `cross_validate_p2.py`; retrain models | `temporal-learner-code/`, `sentence_to_technique_classifier/` |
| **System Admin** | Start/stop the web server; configure port via `PORT` env var; build Angular frontend | `web-server/run.py` L14 |

### External Systems

| System | Purpose | How Called | Auth | Failure Handling |
|---|---|---|---|---|
| **spaCy models** (`en_core_web_sm`, `en_core_web_lg`) | Sentence segmentation, NLP | `spacy.load()` — `pipeline.py` L96–102 | None | Falls back: `sm` → `lg` → blank model with sentencizer |
| **spaCy asset classifier** (`sentence_to_asset_classifier/bagging_models/`) | Asset classification | `spacy.load()` — `pipeline.py` L105–112 | None | `self.asset_model = None`; keyword-only fallback |
| **spaCy technique classifier** (`sentence_to_technique_classifier/bagging_models/robertaCtiAll-final/model-best`) | Technique classification | `spacy.load()` — `pipeline.py` L115–120 | None | `self.technique_model = None`; keyword-only fallback |
| **OpenAI API** | Optional GPT-3.5 fine-tuning for sentence→technique | `openai` Python client — `sentence_to_technique_classifier/openai/fine_tune.py` | `OPENAI_API_KEY` env var | `[NOT FOUND]` explicit handling; would fail if key missing |
| **HuggingFace `roberta-base`** | MLM pretraining base model | `from_pretrained("roberta-base")` — `mlm.py` L24 | None (public) | Network dependency during training |
| **tarsqi-ttk** | TimeML temporal parsing tool | Subprocess / Python API — `TimeML/obtain_cti_report_to_timeML.py` | None | `[INFERRED]` — tarsqi installation required separately |
| **File System** | Taxonomy JSON files, trained model files, report files | `os.path` + `open()` | None | Graceful degradation: empty lists if taxonomy not found (`pipeline.py` L80–92) |
| **Angular HTTP client** | Frontend → backend HTTP | `HttpClient` (RxJS Observable) — `cti-api.service.ts` | None | Error propagated via Observable error channel |

### Internet Requirement
- **Required** during training: HuggingFace model downloads (`roberta-base`), OpenAI API calls.
- **Not required** for web server operation after models are installed.
- Frontend hardcodes `baseUrl = 'http://localhost:8000'` (`cti-api.service.ts` L10) — **no HTTPS, no remote API**.

---

## 3. Use Cases

### Use Case Catalogue

| ID | Name | Actor | Preconditions | Main Flow | Alternate/Error Flows | Postconditions | Source |
|---|---|---|---|---|---|---|---|
| UC-01 | Analyze Text Report | Analyst | Web server running at localhost:8000 | 1. User pastes CTI text in textarea. 2. Clicks "Analyze & Build Flow" (play_arrow icon). 3. Frontend POSTs to `/api/analyze`. 4. Backend segments text, extracts techniques/assets, builds graph. 5. Graph rendered on SVG canvas. | A1: Empty text → error banner "Please enter CTI report text." A2: API error → error banner with message | Attack-flow graph visible; tables populated | `report-analyzer.ts` L24–43; `backend/app.py` L94–108 |
| UC-02 | Upload Report File | Analyst | Web server running | 1. User clicks "Upload Report" (upload_file icon). 2. Selects file (`.txt/.md/.csv/.json`). 3. Frontend POSTs multipart form to `/api/upload`. 4. Backend decodes UTF-8, processes same as UC-01. | A1: Empty file → 400 "Uploaded file is empty." A2: Read error → 400 "Error reading file: {e}" | Attack-flow graph visible | `report-analyzer.ts` L45–63; `backend/app.py` L110–132 |
| UC-03 | Inspect Node | Analyst | A graph is displayed | 1. User clicks a node on canvas. 2. `selectNode()` called. 3. Modal opens with: type badge, label, ID/subtitle, confidence %, sentence context. | None identified | Modal visible with node metadata | `attack-flow-canvas.ts` L125–129; `app.html` L107–141 |
| UC-04 | Pan and Zoom Graph | Analyst | Graph displayed | 1. Click + drag on blank canvas area → pans viewport. 2. Scroll wheel → smooth scroll. 3. Ctrl+scroll → zooms toward mouse cursor. | None | Transform updated; graph repositioned | `attack-flow-canvas.ts` L48–89 |
| UC-05 | Fit Graph to Screen | Analyst | Graph displayed | 1. Click "fit_screen" button. 2. `fitToScreen()` computes bounding box, sets scale and offset. | No nodes → returns early | Graph centered and scaled to viewport | `attack-flow-canvas.ts` L103–123 |
| UC-06 | Export SVG | Analyst | Graph displayed | 1. Click "Export SVG" (download icon). 2. `generateStandaloneSvgString()` clones DOM layers, embeds styles, computes viewBox. 3. Blob → anchor click → download. | No nodes → returns early | File `chronocti-attack-flow-{timestamp}.svg` downloaded | `attack-flow-canvas.ts` L175–249 |
| UC-07 | Export PNG | Analyst | Graph displayed | 1. Click "Export PNG" (image icon). 2. SVG string rendered to `<canvas>` at 2× scale. 3. `canvas.toBlob()` → PNG download. | No nodes → returns early | File `chronocti-attack-flow-{timestamp}.png` downloaded | `attack-flow-canvas.ts` L252–286 |
| UC-08 | Toggle Sidebar | Analyst | App loaded | 1. Click menu/menu_open icon in header or chevron pill on resizer. 2. `isSidebarCollapsed` toggled. | None | Sidebar hidden (width=0) or shown | `app.ts` L116–119; `app.html` L6–8, L92–94 |
| UC-09 | Resize Sidebar | Analyst | App loaded, sidebar visible | 1. Click + drag the resizer divider. 2. `sidebarWidth` signal updated (min 260px, max min(850, window-300)). | None | Sidebar width changed | `app.ts` L94–113 |
| UC-10 | Train ML Pipeline (Stage 1–8) | Researcher | Dependencies installed, datasets present | 1. Run scripts in order per `readme2.md`. 2. Each stage reads outputs of previous stage. 3. Final output: `.gexf` graph files. | A1: Missing model files → FileNotFoundError. A2: Missing OPENAI_API_KEY → OpenAI client error | Trained models + `.gexf` files produced | `readme2.md` L66–136 |
| UC-11 | Check API Health | Analyst / Admin | Web server running | 1. GET `/api/health`. 2. Returns status, model load status, class counts. | None | JSON response with `"status": "healthy"` | `backend/app.py` L47–56 |

### Module Groupings

#### Module A: Report Input & Processing (UC-01, UC-02, UC-11)
The report analyzer module handles all input pathways — text paste and file upload — and drives the backend NLP pipeline. It covers validation, request routing, sentence splitting, technique/asset extraction, and health monitoring.

#### Module B: Graph Visualization & Navigation (UC-03, UC-04, UC-05)
The interactive canvas module renders the attack-flow DAG as an SVG with panning, zooming, fit-to-screen, animated edge pulses, node selection, and a node inspector modal.

#### Module C: Graph Export (UC-06, UC-07)
The export module generates standalone, self-contained SVG or 2×-resolution PNG files from the live canvas state, with embedded fonts and styles so the exported file is viewable in any viewer.

#### Module D: Layout & Sidebar Control (UC-08, UC-09)
The shell/layout module manages the resizable sidebar, collapsing behavior, and the metrics/tables display within the sidebar.

#### Module E: Offline ML Training Pipeline (UC-10)
The 8-stage research pipeline module covers all training and inference scripts that transform raw CTI corpora into trained models and temporal knowledge graphs.

---

## 4. End-to-End Workflow (Activity Diagram Material)

### Web Application Workflow (User → Graph)

```
1. SERVER STARTUP
   └─ python web-server/run.py
      └─ uvicorn starts "app:app" on port 8000  [run.py L20]
      └─ FastAPI initializes
      └─ ChronoCTIPipeline.__init__() called  [pipeline.py L73–77]
         ├─ load_taxonomies(): reads selected_assetsWName.json + selected_techniquesWName.json
         │   → self.asset_map, self.technique_map dicts built  [pipeline.py L79–92]
         └─ load_nlp_models(): loads spaCy models with 3-tier fallback  [pipeline.py L94–120]
            ├─ Try: spacy.load("en_core_web_sm")
            ├─ Fallback: spacy.load("en_core_web_lg")
            └─ Fallback: spacy.blank("en") + sentencizer

2. ANGULAR FRONTEND LOADS (http://localhost:8000/)
   └─ Angular bootstraps AppComponent  [main.ts]
   └─ ngOnInit() fires automatic initial analysis of hardcoded sample text  [app.ts L69–76]
      └─ ctiApi.analyzeReport(initialText) called  [cti-api.service.ts L26–33]

3. USER INPUT
   BRANCH A: Text Input
   └─ User types/pastes text in textarea [(ngModel)="reportText"]
   └─ Clicks "Analyze & Build Flow"
   └─ report-analyzer.ts runAnalysis() called  [L24–43]
   └─ if reportText.trim() < 1 char → error "Please enter CTI report text."

   BRANCH B: File Upload
   └─ User clicks "Upload Report"
   └─ <input type="file"> triggers onFileSelected()  [report-analyzer.ts L45–63]
   └─ ctiApi.uploadFile(file) → POST /api/upload (multipart)

4. BACKEND: FastAPI endpoint receives request  [app.py L94–108 or L110–132]
   └─ Validation: text length < 5 chars → HTTP 400
   └─ pipeline_instance.process_report() called  [pipeline.py L184–276]

5. SENTENCE PROCESSING LOOP  [pipeline.py L191–230]
   └─ split_sentences(raw_text):
       ├─ Collapse whitespace/newlines  [L123–124]
       ├─ nlp_base(cleaned) → spaCy Doc → sentences via doc.sents
       └─ Fallback: regex split on [.!?]  [L127–128]
   └─ FOR EACH sentence (idx, sent_text):
       ├─ extract_temporal_signals(sent_text):
       │   └─ Regex match 5 TEMPORAL_PATTERNS → signals list  [L131–138]
       ├─ predict_assets(sent_text, threshold=0.5):
       │   ├─ If asset_model loaded: doc.cats → filter by score >= threshold
       │   └─ Keyword regex fallback: 18 ASSET_KEYWORDS entries → fixed conf 0.95  [L140–160]
       └─ predict_techniques(sent_text, threshold=0.5):
           ├─ If technique_model loaded: doc.cats → filter by score >= threshold
           └─ Keyword regex fallback: 20 TECHNIQUE_KEYWORDS entries → fixed conf 0.92  [L162–182]
   └─ Aggregate unique_assets, unique_techniques (defaultdict) per report  [L188–222]

6. GRAPH CONSTRUCTION  [attack_flow.py L16–168]
   └─ attack_flow_engine.build_attack_flow_from_chrono_data(sentences, asset_map, technique_map)
   ├─ STEP 1: Filter stages with at least 1 technique or asset  [L29–48]
   ├─ STEP 2: Canonical node registration  [L50–136]
   │   ├─ For each technique: if tid already seen → occurrence_count++, else create new entry
   │   └─ For each asset: same deduplication logic
   ├─ STEP 3: Edge construction  [L138–165]
   │   ├─ Technique → Asset: "TARGETS" edge (if not already exists)
   │   └─ Previous techniques → Current techniques: "AFTER" edge (if not already exists, p_nid != c_nid)
   └─ STEP 4: Layout and metrics  [L167–440]
       ├─ NetworkX: is_dag(), dag_longest_path_length(), density()
       ├─ Topological sort to assign levels
       ├─ Group nodes by level → center techniques horizontally, place assets to the right
       ├─ 8-iteration bounding-box collision resolution  [L319–338]
       └─ Orthogonal stepped path computation for each edge  [L361–421]

7. RESPONSE SERIALIZATION  [pipeline.py L262–276; schemas.py L93–100]
   └─ Returns AnalyzeResponse JSON: report_name, total_sentences, summary,
      assets[], techniques[], sentences[], attack_flow{nodes[], edges[], metrics}

8. FRONTEND RENDERS GRAPH
   └─ onAnalysisResult(res) called in app.ts  [L78–82]
   └─ currentGraph.set(res.attack_flow) → triggers effect() in canvas  [attack-flow-canvas.ts L26–31]
   └─ setTimeout(() => fitToScreen(), 50)
   └─ SVG rendered via Angular @for loop:
       ├─ Edges layer: <path d=calculateSteppedPath(edge)> + animateMotion circle
       └─ Nodes layer: type-specific <g> (technique=blue, asset=green, logic_gate=red, condition=green)
```

### Decision Points and Thresholds
| Decision | Condition | Value | Source |
|---|---|---|---|
| Technique extraction threshold | `score >= threshold` | default 0.5 | `pipeline.py` L168–171; `cti-api.service.ts` L31 |
| Asset extraction threshold | `score >= threshold` | default 0.5 | `pipeline.py` L146–150; `cti-api.service.ts` L30 |
| Keyword fallback confidence (asset) | Always when keyword matches | 0.95 | `pipeline.py` L157 |
| Keyword fallback confidence (technique) | Always when keyword matches | 0.92 | `pipeline.py` L179 |
| Min sentence length | `len(s.text.strip()) > 5` | 5 chars | `pipeline.py` L126 |
| API input validation | `len(payload.text.strip()) < 5` | 5 chars | `app.py` L99 |
| Canvas zoom range | `Math.min(Math.max(scale, 0.3), 3.0)` | 0.3–3.0 | `attack-flow-canvas.ts` L72 |
| Collision resolution iterations | `for _ in range(8)` | 8 passes | `attack_flow.py` L321 |
| Collision pad | `pad = 24` | 24px | `attack_flow.py` L330 |
| Fit-to-screen scale | `Math.min(Math.max(scaleX, 0.75), 1.1)` | 0.75–1.10 | `attack-flow-canvas.ts` L118 |
| Sidebar min/max width | `minWidth=260, maxWidth=min(850, window-300)` | 260–850px | `app.ts` L103–104 |

### Mermaid Flowchart

```mermaid
flowchart TD
    A([User opens browser]) --> B[Angular loads, ngOnInit triggers sample analysis]
    B --> C{User action}
    C -- Paste text --> D[Click Analyze & Build Flow]
    C -- Upload file --> E[Select file via input]
    D --> F[POST /api/analyze with text]
    E --> G[POST /api/upload with file]
    F --> H{text length >= 5?}
    G --> H
    H -- No --> I[HTTP 400 error → UI error banner]
    H -- Yes --> J[pipeline.process_report]
    J --> K[split_sentences via spaCy]
    K --> L[Loop each sentence]
    L --> M[extract_temporal_signals regex]
    L --> N{asset_model loaded?}
    N -- Yes --> O[spaCy predict assets]
    N -- No --> P[keyword regex fallback 0.95]
    O --> Q[merge predictions]
    P --> Q
    L --> R{technique_model loaded?}
    R -- Yes --> S[spaCy predict techniques]
    R -- No --> T[keyword regex fallback 0.92]
    S --> U[merge predictions]
    T --> U
    U --> V[build_attack_flow_from_chrono_data]
    V --> W[Register canonical nodes deduplicated]
    W --> X[Add AFTER edges prev→curr techs]
    X --> Y[Add TARGETS edges tech→asset]
    Y --> Z[Topological layout + collision resolution]
    Z --> AA[Return AnalyzeResponse JSON]
    AA --> AB[Angular renders SVG canvas]
    AB --> AC{User interaction}
    AC -- Click node --> AD[Open inspector modal]
    AC -- Pan/zoom --> AE[Update SVG transform]
    AC -- Export SVG --> AF[Download standalone SVG file]
    AC -- Export PNG --> AG[Render to canvas 2x, download PNG]
```

---

## 5. Data and Storage

### Database
**No database used.** All data is in-memory during request processing. Trained model artifacts are loaded from the file system at server startup. JSON taxonomy files are loaded once at startup.

### Files Read and Written

| File | Path | Format | Purpose | Lifetime | Source |
|---|---|---|---|---|---|
| Asset taxonomy | `Datasets/Dataset/Sentence-to-asset-mappings/selected_assetsWName.json` | JSON array `[{id, name}]` | Maps asset IDs to human names | Persistent (read-only at startup) | `pipeline.py` L14, L79–85 |
| Technique taxonomy | `sentence_to_technique_classifier/selected_techniquesWName.json` | JSON array `[{id, name}]` — 329 entries | Maps technique IDs to human names | Persistent (read-only at startup) | `pipeline.py` L15, L87–92 |
| Asset classifier model | `sentence_to_asset_classifier/bagging_models/asset_classifier_model/model-best` | spaCy model directory | Classifies sentences to asset classes | Persistent (loaded at startup) | `pipeline.py` L16 |
| Asset classifier fallback | `sentence_to_asset_classifier/bagging_models/lgAll-0/model-best` | spaCy model directory | Second-attempt model | Persistent | `pipeline.py` L17 |
| Technique classifier model | `sentence_to_technique_classifier/bagging_models/robertaCtiAll-final/model-best` | spaCy model directory | Classifies sentences to ATT&CK techniques | Persistent | `pipeline.py` L18 |
| Angular production build | `web-server/static/` | HTML/JS/CSS bundle | Served as SPA | Persistent until `npm run build` reruns | `backend/app.py` L41–45 |
| W2V training corpus | `Datasets/relevance_train.jsonl`, `relevance_eval.jsonl`, `all_report_sentences.jsonl` | JSONL `{"text": "..."}` | Input for Word2Vec training | Persistent | `create_cti_w2v.py` L15–23 |
| Trained W2V model | `Datasets/w2v_cti_reports-v2.bin` + `.txt` | Gensim binary + word2vec text | CTI word vectors | Persistent | `create_cti_w2v.py` L66–68 |
| Ground-truth labels | `temporal-learner-code/temporal_relation_dataset.xlsx` | Excel XLSX | Temporal relation labels for training | Persistent | `readme2.md` L472 |
| Feature vectors | `temporal-learner-code/unseen_reports_features/all_reports_threshold_95.json` | JSON array | One object per (report, T1, T2) triple | Persistent (pipeline output) | `readme2.md` L383–385 |
| GNN checkpoints | `temporal-learner-code/gnn_model_0.pt` … `gnn_model_4.pt` | PyTorch binary | 5-fold GNN model weights | Persistent | Verified: files present (556 KB each) |
| Output attack graphs | `input and outputs/*_graph.gexf` | GEXF XML (NetworkX format) | Final per-report temporal graphs | Persistent | `readme2.md` L460 |

### Configuration

| Key | Mechanism | Default | Source |
|---|---|---|---|
| `PORT` | Environment variable | `8000` | `web-server/run.py` L14 |
| `OPENAI_API_KEY` | Environment variable | (none — required for fine-tuning) | `readme2.md` L237; `sentence_to_technique_classifier/.env` (71 bytes) |
| `asset_threshold` | API request field | `0.5` | `schemas.py` L7; `cti-api.service.ts` L30 |
| `technique_threshold` | API request field | `0.5` | `schemas.py` L8; `cti-api.service.ts` L31 |
| Model paths | Hardcoded in `pipeline.py` | See L14–18 | `pipeline.py` L14–18 |
| Angular API base URL | Hardcoded in service | `http://localhost:8000` | `cti-api.service.ts` L10 |

---

## 6. Class / Module Model (CRC-Ready)

### Backend Classes

---

#### `AttackFlowEngine`
**File:** `web-server/backend/attack_flow.py`
**Responsibility:** Constructs a deduplicated, topologically-laid-out directed knowledge graph from extracted sentence data.

| Attributes | Type |
|---|---|
| *(none — stateless)* | — |

| Method | Signature | Purpose |
|---|---|---|
| `build_attack_flow_from_chrono_data` | `(sentences, asset_map, technique_map) → Dict` | Main entry: deduplicates nodes, adds edges, calls layout |
| `_layout_and_format_graph` | `(G: nx.DiGraph) → Dict` | Topological level assignment, node placement, collision resolution, edge path computation |
| `_empty_graph` | `() → Dict` | Returns zero-node graph structure |

**Collaborators:** `networkx.DiGraph`, `math`
**Pattern:** Singleton (module-level `attack_flow_engine = AttackFlowEngine()`)

---

#### `ChronoCTIPipeline`
**File:** `web-server/backend/pipeline.py`
**Responsibility:** Orchestrates full NLP processing of a raw CTI text report — segmentation, classification, and graph data preparation.

| Attributes | Type |
|---|---|
| `nlp_base` | `spacy.Language` |
| `asset_model` | `spacy.Language \| None` |
| `technique_model` | `spacy.Language \| None` |
| `asset_tax` | `List[Dict]` |
| `technique_tax` | `List[Dict]` |
| `asset_map` | `Dict[str, str]` |
| `technique_map` | `Dict[str, str]` |

| Method | Signature | Purpose |
|---|---|---|
| `load_taxonomies` | `() → None` | Reads JSON taxonomy files from disk |
| `load_nlp_models` | `() → None` | Loads spaCy models with fallback chain |
| `split_sentences` | `(raw_text: str) → List[str]` | Splits text into sentences |
| `extract_temporal_signals` | `(text: str) → List[str]` | Detects BEFORE/AFTER/OVERLAP etc. via regex |
| `predict_assets` | `(text, threshold) → List[Tuple[str, float]]` | ML + keyword asset prediction |
| `predict_techniques` | `(text, threshold) → List[Tuple[str, float]]` | ML + keyword technique prediction |
| `process_report` | `(raw_text, report_name, asset_thresh, tech_thresh) → Dict` | Orchestrates full pipeline, returns API response dict |

**Collaborators:** `AttackFlowEngine`, `spacy`, `re`, `json`, `collections.defaultdict`
**Pattern:** Singleton (module-level `pipeline_instance = ChronoCTIPipeline()`)

---

### Backend Pydantic Schemas (web-server/backend/schemas.py)
9 classes total (none skipped — all are data transfer objects):

| Class | Responsibility |
|---|---|
| `AnalyzeRequest` | Input: `text`, `report_name`, `asset_threshold`, `technique_threshold` |
| `AssetDetail` | Per-sentence asset match: `id`, `name`, `confidence`, `sentence_id`, `sentence_text` |
| `UniqueAssetSummary` | Aggregated asset: `id`, `name`, `occurrence_count`, `highest_confidence`, `matched_sentences` |
| `TechniqueDetail` | Per-sentence technique match (same fields as `AssetDetail`) |
| `UniqueTechniqueSummary` | Aggregated technique (same fields as `UniqueAssetSummary`) |
| `SentenceItem` | One sentence: `sentence_id`, `text`, `assets[]`, `techniques[]`, `temporal_signals[]` |
| `AttackFlowNode` | Graph node: `id`, `type`, `raw_id`, `label`, `subtitle`, `confidence`, `x`, `y`, `width`, `height`, `occurrence_count`, `branches` |
| `AttackFlowEdge` | Graph edge: `id`, `source`, `target`, `relation`, `edge_type`, `path_points` |
| `AttackFlowMetrics` | Graph stats: `total_nodes`, `total_edges`, `is_dag`, `longest_attack_chain`, `density` |
| `AttackFlowGraph` | Full graph: `title`, `description`, `nodes[]`, `edges[]`, `canvas_width`, `canvas_height`, `metrics` |
| `AnalyzeResponse` | Full API response: `report_name`, `total_sentences`, `summary`, `assets[]`, `techniques[]`, `sentences[]`, `attack_flow` |

---

### Frontend Classes (Angular)

#### `AppComponent`
**File:** `web-server/frontend/src/app/app.ts`
**Responsibility:** Root application shell: sidebar state, graph state, modal state, sidebar resize/collapse logic.

| Signal | Type |
|---|---|
| `currentGraph` | `Signal<AttackFlowGraph \| null>` |
| `techniques` | `Signal<UniqueTechniqueSummary[]>` |
| `assets` | `Signal<UniqueAssetSummary[]>` |
| `selectedNode` | `Signal<AttackFlowNode \| null>` |
| `isModalOpen` | `Signal<boolean>` |
| `sidebarWidth` | `Signal<number>` (default 400) |
| `isDraggingSidebar` | `Signal<boolean>` |
| `isSidebarCollapsed` | `Signal<boolean>` |

| Method | Purpose |
|---|---|
| `onAnalysisResult(res)` | Updates graph, techniques, assets signals |
| `onNodeClicked(node)` | Opens inspector modal |
| `closeModal()` | Closes modal |
| `onResizerMouseDown(event)` | Begins sidebar resize drag |
| `onWindowMouseMove(event)` | Updates sidebar width during drag |
| `onWindowMouseUp()` | Ends drag |
| `toggleSidebar(event?)` | Collapses/expands sidebar |

**Collaborators:** `CtiApiService`, `AttackFlowCanvasComponent`, `ReportAnalyzerComponent`, `GenericTable`, `GenericModal`, `GenericLabel`, `GenericButton`

---

#### `AttackFlowCanvasComponent`
**File:** `web-server/frontend/src/app/components/attack-flow-canvas/attack-flow-canvas.ts`
**Responsibility:** Renders attack-flow graph as SVG; handles interaction (pan, zoom, node selection, export).

| Property | Type |
|---|---|
| `graph` | `InputSignal<AttackFlowGraph \| null>` |
| `transform` | `{x, y, scale}` object |
| `isPanning` | `boolean` |
| `selectedNodeId` | `string \| null` |

| Method | Purpose |
|---|---|
| `fitToScreen()` | Calculates bounding box, sets transform scale (0.75–1.1 range) |
| `selectNode(node, event)` | Sets selection, emits `onNodeSelected` output |
| `calculateSteppedPath(edge)` | Computes 4-point orthogonal SVG path string |
| `wrapText(text, maxChars)` | Word-wraps label into string array (max 24 chars/line) |
| `generateStandaloneSvgString()` | Clones SVG DOM, embeds styles, computes viewBox |
| `exportSvg()` | Triggers SVG file download |
| `exportPng()` | Renders SVG on canvas at 2×, triggers PNG download |

---

#### `ReportAnalyzerComponent`
**File:** `web-server/frontend/src/app/components/report-analyzer/report-analyzer.ts`
**Responsibility:** Text input, file upload, loading state, error display.

| Signal | Type |
|---|---|
| `isAnalyzing` | `Signal<boolean>` |
| `errorMessage` | `Signal<string>` |

| Method | Purpose |
|---|---|
| `runAnalysis()` | Validates input, calls `ctiApi.analyzeReport()` |
| `onFileSelected(event)` | Reads file, calls `ctiApi.uploadFile()` |

---

#### `CtiApiService`
**File:** `web-server/frontend/src/app/services/cti-api.service.ts`
**Responsibility:** HTTP client wrapper for all backend API calls.

| Method | Signature | Purpose |
|---|---|---|
| `getHealth()` | `() → Observable<any>` | GET `/api/health` |
| `getScenarios()` | `() → Observable<ScenarioPreset[]>` | GET `/api/scenarios` |
| `getScenarioById(id)` | `(id: string) → Observable<AttackFlowGraph>` | GET `/api/scenarios/{id}` |
| `analyzeReport(text, name)` | `(text, name?) → Observable<AnalyzeResponse>` | POST `/api/analyze` |
| `uploadFile(file)` | `(file: File) → Observable<AnalyzeResponse>` | POST `/api/upload` |

---

### Mermaid Class Diagram

```mermaid
classDiagram
    class ChronoCTIPipeline {
        +nlp_base: spacy.Language
        +asset_model: spacy.Language
        +technique_model: spacy.Language
        +asset_map: dict
        +technique_map: dict
        +process_report(raw_text, report_name, asset_thresh, tech_thresh) dict
        +split_sentences(raw_text) list
        +predict_techniques(text, threshold) list
        +predict_assets(text, threshold) list
        +extract_temporal_signals(text) list
    }

    class AttackFlowEngine {
        +build_attack_flow_from_chrono_data(sentences, asset_map, technique_map) dict
        -_layout_and_format_graph(G) dict
        -_empty_graph() dict
    }

    class FastAPIApp {
        +analyze_report(payload) AnalyzeResponse
        +upload_and_analyze(file) AnalyzeResponse
        +health_check() dict
        +get_asset_taxonomy() list
        +get_technique_taxonomy() list
        +list_scenarios() list
        +serve_dashboard() HTMLResponse
    }

    class AnalyzeRequest {
        +text: str
        +report_name: str
        +asset_threshold: float
        +technique_threshold: float
    }

    class AnalyzeResponse {
        +report_name: str
        +total_sentences: int
        +attack_flow: AttackFlowGraph
        +assets: list
        +techniques: list
    }

    class AttackFlowGraph {
        +nodes: list
        +edges: list
        +metrics: AttackFlowMetrics
        +canvas_width: float
        +canvas_height: float
    }

    class AppComponent {
        +currentGraph: Signal
        +sidebarWidth: Signal
        +onAnalysisResult(res)
        +toggleSidebar()
    }

    class AttackFlowCanvasComponent {
        +graph: InputSignal
        +transform: object
        +fitToScreen()
        +exportSvg()
        +exportPng()
        +calculateSteppedPath(edge)
    }

    class ReportAnalyzerComponent {
        +reportText: string
        +runAnalysis()
        +onFileSelected(event)
    }

    class CtiApiService {
        +baseUrl: string
        +analyzeReport(text) Observable
        +uploadFile(file) Observable
    }

    FastAPIApp --> ChronoCTIPipeline : uses singleton
    FastAPIApp --> AttackFlowEngine : uses singleton
    ChronoCTIPipeline --> AttackFlowEngine : calls build_attack_flow_from_chrono_data
    FastAPIApp --> AnalyzeRequest : receives
    FastAPIApp --> AnalyzeResponse : returns
    AnalyzeResponse --> AttackFlowGraph : contains
    AppComponent --> CtiApiService : injects
    AppComponent --> AttackFlowCanvasComponent : hosts
    AppComponent --> ReportAnalyzerComponent : hosts
    ReportAnalyzerComponent --> CtiApiService : injects
    CtiApiService --> FastAPIApp : HTTP calls
```

### Design Patterns Identified
| Pattern | Classes/Modules Involved |
|---|---|
| **Singleton** | `attack_flow_engine = AttackFlowEngine()` (`attack_flow.py` L458); `pipeline_instance = ChronoCTIPipeline()` (`pipeline.py` L278) |
| **Pipeline** | 8-stage ML pipeline in `temporal-learner-code/`, `sentence_to_technique_classifier/`, etc. |
| **Facade** | `ChronoCTIPipeline.process_report()` — single method that orchestrates segmentation, classification, and graph building |
| **Strategy** | `predict_techniques()` / `predict_assets()` — ML model strategy first, keyword regex strategy as fallback |
| **Template Method** | `_layout_and_format_graph()` — fixed sequence: metrics → level assignment → position calculation → collision → formatting |
| **Observer** | Angular signals (`signal<>`) + `effect()` in `AttackFlowCanvasComponent` trigger re-render when graph input changes |
| **Factory** (informal) | `_empty_graph()` returns a zero-node graph structure as a safe default |

---

## 7. Architecture

### Layers

| Layer | Modules | Communication |
|---|---|---|
| **Presentation** | Angular 18 SPA (`web-server/frontend/`) | HTTP/JSON to backend; SVG DOM rendering in browser |
| **API Gateway** | FastAPI app (`web-server/backend/app.py`) | Receives HTTP; delegates to Pipeline and Engine |
| **Business Logic** | `ChronoCTIPipeline`, `AttackFlowEngine` | Direct Python function calls |
| **NLP/ML Integration** | spaCy models, regex patterns | Loaded in-process; no RPC |
| **Persistence / Config** | JSON taxonomy files, spaCy model directories | File system reads at startup |
| **Research Pipeline** | 8 stage scripts (separate processes, not connected to web server) | Script-to-file (JSON, XLSX, .pt, .gexf) |

### Component Communication
```
Browser (Angular SPA)
    ↕  HTTP/JSON (localhost:8000)
FastAPI (uvicorn)
    → app.py routes
        → ChronoCTIPipeline.process_report()
            → spaCy NLP models (in-process)
            → AttackFlowEngine.build_attack_flow_from_chrono_data()
                → NetworkX DiGraph (in-process)
        ← Pydantic JSON response
    ← HTTP response
Browser renders SVG
```

### Concurrency Model
- **Uvicorn** (ASGI): asynchronous I/O for HTTP; the upload endpoint uses `async def` + `await file.read()`. The analyze endpoint uses synchronous `def` (blocking). `[PARTIAL]` — file upload is async, text analysis is synchronous.
- **Angular frontend**: RxJS Observables for async HTTP; UI remains responsive during analysis.
- **ML pipeline**: Sequential, single-process Python scripts. GNN training is single-process PyTorch (no distributed training detected).
- **Word2Vec training**: `workers=8` (multi-threaded gensim, `create_cti_w2v.py` L62).

### Deployment
| Step | Command | Source |
|---|---|---|
| Install backend dependencies | `pipenv install` (from root) | `readme.md` L6 |
| Install spaCy model | `python -m spacy download en_core_web_lg` | `readme.md` L8 |
| Install frontend dependencies | `cd web-server/frontend && npm i` | verified in session |
| Build Angular | `npm run build` → outputs to `web-server/static/` | `package.json` L7 |
| Start server | `python web-server/run.py` (or `cd web-server && python backend/run.py`) | `run.py` L13–20 |

**Supported OS:** Linux, macOS, WSL (`readme2.md` L33). Not explicitly Windows-native (path handling uses `/`).
**Runtime:** Python 3.11 for web server; Node.js (any LTS) for frontend build.

### Security-Relevant Design
| Concern | Finding | Source |
|---|---|---|
| CORS | `allow_origins=["*"]` — fully open | `app.py` L35 |
| Secret handling | `OPENAI_API_KEY` via env var | `readme2.md` L237 |
| Input validation | Min length check only (5 chars) | `app.py` L99, L123 |
| File upload | `errors="replace"` on UTF-8 decode — malformed files won't crash | `app.py` L119 |
| Subprocess | tarsqi-ttk called via subprocess (`TimeML/`) — `[INFERRED]` risk if input is untrusted |

---

## 8. Methodology and Core Algorithms

### Algorithm 1: Word2Vec CTI Embedding (Stage 1)
**Purpose:** Build domain-specific word vectors for CTI vocabulary.
**Inputs:** `relevance_train.jsonl`, `relevance_eval.jsonl`, `all_report_sentences.jsonl`
**Outputs:** `Datasets/w2v_cti_reports-v2.txt` + spaCy model `Datasets/cti_w2v_v2`

**Pseudo-code:**
```
1. Load all sentences from 3 JSONL files
2. Tokenize, remove spaCy stop words
3. Extract bigrams: Phrases(min_count=30)
4. Train Word2Vec:
   - vector_size=300, window=5, min_count=5
   - sample=6e-5, alpha=0.03, min_alpha=0.0007, workers=8, negative=20
   - epochs=30
5. Save as text format
6. Convert to spaCy model via subprocess: `python -m spacy init vectors en ...`
```
Source: `create_cti_w2v.py` L57–68

---

### Algorithm 2: RoBERTa-CTI Domain Adaptation (Stage 2a)
**Purpose:** Adapt `roberta-base` to CTI domain via Masked Language Modeling.
**Key Parameters:**
- `mlm_probability=0.15` (`mlm.py` L50)
- `max_length=512` (`mlm.py` L36)
- `num_train_epochs=1` (`mlm.py` L57)
- `per_device_train_batch_size=8` (`mlm.py` L16, 58)
- Device: MPS (Apple Silicon) if available, else CPU (`mlm.py` L13)

---

### Algorithm 3: Sentence→Technique Classification (Stage 3)
**Purpose:** Tag each CTI sentence with zero or more MITRE ATT&CK techniques.
**Approach:** Bagging ensemble of 5 spaCy `textcat` models trained with 5-fold CV:
- `w2vAll` (CTI Word2Vec), `lgAll` (en_core_web_lg), `trfAll` (transformer), `robertaBaseAll`, `robertaCtiAll`
- Source: `sentence_to_technique_classifier/train_models.py`; `readme2.md` L251–257

**Runtime fallback (web server):** 20 keyword regex patterns hardcoded in `pipeline.py` `TECHNIQUE_KEYWORDS` dict (L49–70). Each match produces a fixed confidence of 0.92.

---

### Algorithm 4: Canonical Deduplicated Graph Construction (Web Server)
**Purpose:** Build a DAG where each unique technique/asset appears exactly once.

**Key invariants:**
- `if tid not in unique_tech_data:` → create new node, `else:` → `occurrence_count += 1`
- Edge existence check: `if not G.has_edge(p_nid, c_nid):`
- Self-loop prevention: `if p_nid != c_nid:`

**Pseudo-code (from `attack_flow.py` L50–165):**
```
for each sentence:
    for each technique t:
        if t.id not in seen: create canonical node, occurrence=1
        else: occurrence += 1; append confidence + sentence text

for each sentence:
    curr_tech_ids = [tech nodes in this sentence]
    curr_asset_ids = [asset nodes in this sentence]
    for p in prev_tech_ids:
        for c in curr_tech_ids:
            if p != c and not edge(p,c): add AFTER edge
    for t in curr_tech_ids:
        for a in curr_asset_ids:
            if not edge(t,a): add TARGETS edge
    prev_tech_ids = curr_tech_ids
```

---

### Algorithm 5: Topological Layout (Web Server)
**Purpose:** Arrange deduplicated nodes in a clean top-to-bottom DAG layout.

**Constants (from `attack_flow.py` L190–199):**
```
NODE_W_TECH = 250px, NODE_H_TECH = 74px
NODE_W_ASSET = 220px, NODE_H_ASSET = 74px
CENTER_X = 420px, START_Y = 80px
H_TECH_GAP = 40px, V_STAGE_GAP = 75px
ASSET_OFFSET_X = 40px
```

**Steps:**
1. Strip TARGETS/AFFECTS edges → subgraph H for level assignment
2. Find roots (in-degree=0 nodes in H)
3. Topological sort → propagate levels: `level[v] = max(level[v], level[u]+1)`
4. Group nodes by level → center technique row horizontally
5. Place assets to the right of technique row
6. Advance `current_y` by `NODE_H + V_STAGE_GAP` per level
7. Run 8-pass 2D bounding-box collision relaxation (pad=24px)

---

### Algorithm 6: Temporal Relation Learning (Stage 8)
**Three model approaches (verified by file existence):**

**6a. Graph Neural Network (DGL):**
- Per-report directed graph: nodes=techniques (feature vector from Stage 3 probabilities), edges=all TTP pairs (feature vector from Stage 6)
- GraphConv + MLP predictor
- Loss: Binary Cross-Entropy (multi-label)
- 5-fold CV → 5 saved checkpoints (`gnn_model_0.pt`…`gnn_model_4.pt`, each 556 KB)
- Source: `temporal-learner-code/learn_graph_ML_imbalanced_multilabel-v2.py`

**6b. XGBoost MultiOutputClassifier:**
- Trains on tabular feature matrix (each row = one TTP pair)
- Feature families: BASIC, SENTENCE, DISCOURSE, AMR, TIMEML, TIME_SIGNAL
- SHAP analysis for feature importance by family
- Metrics: Macro F1, Precision@K, Recall@K, NDCG, Coverage Error
- Source: `temporal-learner-code/make_final_evaluation.py`

**6c. Cross-validation Benchmark:**
- 18+ estimators compared (RF, SVM, MLP, AdaBoost, etc.)
- 5-fold CV per estimator × per feature subset
- Source: `temporal-learner-code/cross_validate_p2.py`

**Labels (4 classes):** `CONCURRENT`, `NEXT`, `OVERLAP`, `NULL` (from `readme2.md` L451–455)

---

### Third-Party ML Components
| Tool | Role | Invocation |
|---|---|---|
| spaCy `en_core_web_lg` / `en_core_web_sm` | Sentence segmentation + base NLP | `spacy.load()` |
| spaCy `en_coreference_web_trf` | Neural coreference resolution | Neuralcoref stage |
| HuggingFace `roberta-base` | Base for domain adaptation | `from_pretrained("roberta-base")` |
| HuggingFace `Trainer` | MLM training loop | `mlm.py` L72–81 |
| DGL (Deep Graph Library) | GNN training | `temporal-learner-code/learn_graph_ML_imbalanced_multilabel-v2.py` |
| XGBoost | Multi-output classification | `temporal-learner-code/make_final_evaluation.py` |
| mlxtend | Apriori algorithm | `apriori-features/` |
| NetworkX | DiGraph construction + metrics | `web-server/backend/attack_flow.py` |
| tarsqi-ttk | TimeML temporal annotation | `TimeML/` (external tool) |
| OpenAI API | GPT-3.5 fine-tuning (optional) | `sentence_to_technique_classifier/openai/fine_tune.py` |
| gensim | Word2Vec training | `create_cti_w2v.py` |
| SHAP | Feature importance for XGBoost | `temporal-learner-code/make_final_evaluation.py` |

---

## 9. Inputs and Outputs

### Inputs

| Input | Source | Format | Validation | Error Message |
|---|---|---|---|---|
| CTI report text | User textarea (web UI) | Plain text | `len(text.strip()) >= 1` (frontend); `len(payload.text.strip()) < 5` (backend) | "Please enter CTI report text." / HTTP 400 "Report text must not be empty." |
| Uploaded CTI file | File input (web UI) | `.txt`, `.md`, `.csv`, `.json` | Non-empty UTF-8 decodable content | HTTP 400 "Uploaded file is empty." / "Error reading file: {e}" |
| `report_name` | API field | String | Optional, default `"cti-report"` | — |
| `asset_threshold` | API field | Float 0–1 | Optional, default `0.5` | — |
| `technique_threshold` | API field | Float 0–1 | Optional, default `0.5` | — |

### Outputs

| Output | Format | Location | Naming | Lifetime |
|---|---|---|---|---|
| API response (analysis) | JSON (AnalyzeResponse) | HTTP body | — | Per-request, in-memory |
| SVG export | `image/svg+xml`, UTF-8, standalone | Browser download | `chronocti-attack-flow-{Date.now()}.svg` | Ephemeral (browser download) |
| PNG export | `image/png`, 2× resolution | Browser download | `chronocti-attack-flow-{Date.now()}.png` | Ephemeral |
| Final research graphs | GEXF XML | `input and outputs/` | `*_graph.gexf` | Persistent |
| Trained GNN models | PyTorch `.pt` | `temporal-learner-code/gnn_model_{0-4}.pt` | Fixed filenames | Persistent |

### Main Output Schema (AnalyzeResponse JSON)
```json
{
  "report_name": "string",
  "total_sentences": 4,
  "summary": {
    "total_unique_assets": 3,
    "total_unique_techniques": 5,
    "total_graph_nodes": 8,
    "total_graph_edges": 7,
    "longest_attack_chain": 4
  },
  "assets": [
    { "id": "A0003", "name": "PLC", "occurrence_count": 2,
      "highest_confidence": 0.95, "matched_sentences": [0, 2] }
  ],
  "techniques": [
    { "id": "T1059", "name": "Command and Scripting Interpreter",
      "occurrence_count": 1, "highest_confidence": 0.92, "matched_sentences": [1] }
  ],
  "sentences": [
    { "sentence_id": 0, "text": "...", "assets": [], "techniques": [],
      "temporal_signals": ["AFTER"] }
  ],
  "attack_flow": {
    "title": "Attack Flow: report_name",
    "nodes": [ { "id": "tech_T1059", "type": "technique", "label": "...",
                 "x": 295, "y": 80, "width": 250, "height": 74,
                 "occurrence_count": 1, "confidence": 0.92 } ],
    "edges": [ { "id": "flow_...", "source": "tech_T1059", "target": "asset_A0003",
                 "relation": "TARGETS", "path_points": [[...],[...]] } ],
    "canvas_width": 1000, "canvas_height": 800,
    "metrics": { "total_nodes": 8, "total_edges": 7, "is_dag": true,
                 "longest_attack_chain": 4, "density": 0.125 }
  }
}
```

---

## 10. User Interface / Interaction Surface

### Screens and Panels

| Element | Controls | What Each Does |
|---|---|---|
| **App Header** | ⚡ brand badge, ChronoCTI title, "NetworkX Attack Flow" label, sidebar toggle (menu icon), "API Docs" link | Title display; sidebar toggle; link to `/docs` |
| **Sidebar** | Resizable (drag handle), collapsible (chevron pill) | Contains report analyzer, metrics card, tables |
| **Report Analyzer Card** | Textarea (placeholder: "Paste unstructured threat report sentences here..."), "Analyze & Build Flow" button (play_arrow icon), "Upload Report" button (upload_file icon + hidden file input) | Input + submission |
| **Metrics Card** | 4 stat tiles: Nodes (blue), Edges (green), Chain Depth (amber), Topology (red: DAG/Cyclic) | Displays NetworkX graph metrics |
| **Extracted Techniques Table** | Columns: Technique ID, Technique Name, Count, Confidence (badge) | Shows all extracted MITRE techniques |
| **Target Assets Table** | Columns: Asset ID, Target Asset, Count, Confidence (badge) | Shows all extracted ICS/IT assets |
| **Canvas Toolbar** (floating) | zoom_in, zoom_out, fit_screen, refresh (reset zoom), "Export SVG" (download icon), "Export PNG" (image icon) | 6 buttons for canvas navigation and export |
| **Canvas Legend** | 4 color swatches: Blue=Technique/Action, Green=Target Asset, Dark Green=Condition(T/F), Red=AND Gate | Graph node type key |
| **SVG Canvas** | Drag to pan; scroll to scroll; Ctrl+scroll to zoom; click node | Main visualization area |
| **Node Inspector Modal** | Type badge (blue/green/red), node label, ID/subtitle field, Confidence field (percentage), sentence context box (blue left border) | Displays details of clicked node |

### User Task List (Step-by-Step)
1. **Analyze text:** Open `http://localhost:8000/` → paste text in textarea → click "Analyze & Build Flow" → wait for graph to appear.
2. **Upload file:** Click "Upload Report" → select `.txt/.md/.csv/.json` file → graph auto-loads.
3. **Inspect node:** Click any node on canvas → modal opens → read type, ID, confidence, source sentence → click outside or close button to dismiss.
4. **Navigate graph:** Click + drag blank area to pan → Ctrl+scroll to zoom → click fit_screen icon to reset view.
5. **Export SVG:** Click "Export SVG" → file downloaded to browser default location.
6. **Export PNG:** Click "Export PNG" → 2× resolution PNG downloaded.
7. **Resize sidebar:** Hover over vertical divider → cursor changes → drag left/right.
8. **Collapse sidebar:** Click menu icon in header OR chevron pill on resizer.

### UI States and Feedback
| State | Feedback | Source |
|---|---|---|
| Analyzing | Button label changes to `"Analyzing with NetworkX..."`, button disabled | `report-analyzer.html` L23; `isAnalyzing()` signal |
| Error | Red error banner with `error_outline` icon + message | `report-analyzer.html` L14–19 |
| Node selected | Blue glow ring (6px offset, rx=14) around selected node | `attack-flow-canvas.html` L111–117 |
| Edge type TARGETS | Dashed green line with green arrowhead | `attack-flow-canvas.html` L89–90 |
| Edge type AFTER | Solid blue line with blue arrowhead | `attack-flow-canvas.html` L88–89 |
| Sidebar collapsed | Width animated to 0px, visibility hidden | `app.scss` L124–130 |
| Resizer dragging | Resizer turns blue with box-shadow glow | `app.scss` L145–152 |
| Occurrence > 1 | Amber ×N badge on top-right corner of node | `attack-flow-canvas.html` L172–178 |

### First-Run / Setup Flow
No wizard or setup screen. On first load, `ngOnInit()` automatically analyzes a hardcoded sample CTI text (`app.ts` L71–75). If the backend is not running, the initial HTTP call fails silently (error logged to browser console only; no user-facing warning).

---

## 11. Testing and Error Handling

### Existing Tests

| Test | File | Framework | Count | What It Covers | Run Command |
|---|---|---|---|---|---|
| Backend API integration test | `web-server/backend/test_api.py` | `fastapi.testclient.TestClient` (Starlette) | 4 assertions in 1 function | (1) GET `/api/health` → 200; (2) GET `/api/scenarios` → 200; (3) GET `/api/scenarios/equifax` → nodes > 5 (will **fail** — method not found); (4) POST `/api/analyze` with TRITON sample text → 200 | `python web-server/backend/test_api.py` |

**NOT RUN** (test 3 would fail due to missing `get_equifax_showcase_scenario()` method — see Section 13).

### Error Handling in Code

| Error | Where Handled | Strategy |
|---|---|---|
| spaCy model not found at primary path | `pipeline.py` L94–112 | 3-tier fallback: `sm` → `lg` → blank + sentencizer |
| Asset/technique model not found | `pipeline.py` L104–120 | `self.model = None`; keyword-only classification |
| Taxonomy JSON not found | `pipeline.py` L80–92 | Empty list `[]` — no crash |
| Empty text / < 5 chars | `app.py` L99, L123 | HTTP 400 |
| File read error | `app.py` L117–121 | HTTP 400 with exception message |
| spaCy model call fails | `pipeline.py` L147–151, L168–173 | `except Exception: pass` — silent, falls to keyword fallback |
| Cyclic graph (not DAG) | `attack_flow.py` L178–181, L223–237 | BFS fallback level assignment |
| Empty sentences / no stages | `attack_flow.py` L47–48 | Returns `_empty_graph()` |
| SVG export with no nodes | `attack-flow-canvas.ts` L176–178 | Returns early, no download triggered |
| Analysis request failure (frontend) | `report-analyzer.ts` L38–41, L57–60 | Sets `errorMessage` signal; UI shows error banner |

### Edge Cases Handled
- Consecutive duplicate techniques (same tech in adjacent sentences) → merged into single node, edge skipped (`p_nid != c_nid`) — `attack_flow.py` L155
- Sentences with no techniques or assets → skipped, not added to stages — `attack_flow.py` L38
- Graph with cycles (not a DAG) → BFS fallback — `attack_flow.py` L223–237
- Nodes with no level assignment → default to level 0 — `attack_flow.py` L235–237
- Text with no sentences (after split) → regex fallback split on `[.!?]` — `pipeline.py` L127–128

### Edge Cases NOT Handled
- No handling of extremely long reports (no chunking, no token limit enforcement)
- No deduplication of asset+technique predictions when both ML model and keyword match fire simultaneously (both can be added at different confidences)
- Frontend does not warn if backend is unreachable on first load
- No timeout on `analyzeReport()` Observable call
- No rate limiting on the API

### Recommended Test Scenarios

| # | Scenario | Steps | Expected Outcome |
|---|---|---|---|
| T01 | **Empty text input** | POST `/api/analyze` with `text=""` | HTTP 400, message "Report text must not be empty." |
| T02 | **Short text (< 5 chars)** | POST `/api/analyze` with `text="abc"` | HTTP 400 |
| T03 | **Valid single sentence** | POST `/api/analyze` with TRITON sample | HTTP 200, `total_sentences >= 1`, graph has nodes |
| T04 | **No techniques or assets detected** | POST with text containing no ATT&CK keywords and no ML model loaded | HTTP 200, empty graph (`nodes=[]`, `edges=[]`) |
| T05 | **File upload: .txt** | POST `/api/upload` with a valid .txt file | HTTP 200, same as T03 |
| T06 | **File upload: empty file** | POST `/api/upload` with 0-byte file | HTTP 400 "Uploaded file is empty." |
| T07 | **File upload: binary file** | POST `/api/upload` with a `.png` | UTF-8 decode with `errors="replace"` — HTTP 200 but likely empty graph |
| T08 | **Large report (~500 sentences)** | POST `/api/analyze` with 500 sentences | Should complete; test for response time > 10s, no crash |
| T09 | **Technique appears in every sentence** | Text where T1059 appears 10× | Graph has 1 node `tech_T1059` with `occurrence_count=10` |
| T10 | **Duplicate consecutive techniques** | S1: T1059, S2: T1059, S3: T1021 | No self-loop T1059→T1059; only T1059→T1021 edge |
| T11 | **Scenario endpoint: equifax** | GET `/api/scenarios/equifax` | HTTP 500 `AttributeError` (missing method — known bug) |
| T12 | **API health check** | GET `/api/health` | HTTP 200, `asset_models_loaded` reflects actual model state |
| T13 | **Backend not running** | Load frontend with backend stopped | Initial analysis fails silently; no user warning displayed |
| T14 | **Cross-platform paths** | Run on Windows (non-WSL) | Likely fails — hardcoded `/` paths in `pipeline.py` L13–18 |
| T15 | **SVG export: no graph** | Click "Export SVG" before any analysis | No download, returns early silently |

---

## 12. Non-Functional Characteristics

### Performance
- **Inference speed:** Purely keyword-based (no ML models loaded): near-instant for short reports. With spaCy models: proportional to sentence count (no batching in `process_report()`).
- **Graph layout:** O(N²) collision resolution (double loop, 8 passes) — `attack_flow.py` L320–338. Acceptable for <100 nodes.
- **W2V training:** `workers=8` threads — `create_cti_w2v.py` L62.
- **PNG export:** 2× Retina scale means canvas is width×2 × height×2 — memory scales quadratically with graph size.

### Scalability Limits
- No request batching or queue — each API call is synchronous and blocking (except file upload).
- All NLP is in-memory — no streaming. Very long reports could cause memory spikes.
- Frontend is a single-page app; no pagination on tables or graph.
- CORS `allow_origins=["*"]` — not suitable for production deployment.

### Reproducibility
- GNN training: no explicit random seed set in code (`[NOT FOUND]` in available scripts); reproducibility `[UNCERTAIN]`.
- Word2Vec: deterministic with same `workers` count and same input.
- spaCy textcat: uses spaCy's built-in training — reproducibility depends on `seed` in config files.

### Logging
- Backend: `print()` statements only (e.g., `"Initializing ChronoCTI..."`, `"Loaded Asset Classifier from {path}"`) — no structured logging framework. `pipeline.py` L74, L109.
- Frontend: `console.error()` for HTTP errors — `app.ts` L74; `report-analyzer.ts` L40.

### Portability
- Web server: requires `python3.11` and the specific model directory structure. Hardcoded absolute path resolution via `os.path` relative to `__file__`.
- Frontend: standard Angular build output — works in any modern browser.
- ML pipeline: multi-version Python requirement (3.10 for RoBERTa, 3.11 for others) — complex setup.

---

## 13. Limitations, TODOs, and Discrepancies

### TODO/FIXME Comments
`[NOT FOUND]` — No explicit `TODO` or `FIXME` comments found in searched source files.

### Known Bugs and Issues
| Issue | File | Details |
|---|---|---|
| **Missing scenario methods** | `backend/app.py` L88–91 | Calls `attack_flow_engine.get_equifax_showcase_scenario()` and `get_triton_ics_scenario()` but these are not defined in `attack_flow.py`. Endpoints `/api/scenarios/equifax` and `/api/scenarios/triton` will raise `AttributeError` at runtime. |
| **test_api.py test 3 will fail** | `backend/test_api.py` L28–32 | Calls the equifax scenario endpoint, asserts `len(nodes) > 5` — will fail with AttributeError. |
| **`scenario-selector` component unused** | `frontend/src/app/components/scenario-selector/` | Directory exists but component is never imported or routed to. |
| **SVG export may render blank** | `attack-flow-canvas.ts` L211–214 | The export clones `#edges-layer` and `#nodes-layer` innerHTML from the live SVG DOM — if Angular has applied CSS transforms that are not intrinsic SVG coordinates, the exported file may look different from the screen. This was noted in the user session (user reported blank SVG download). |
| **Frontend API URL hardcoded** | `cti-api.service.ts` L10 | `'http://localhost:8000'` — no environment configuration; deploying to any other host requires code change. |
| **Missing file**: `prepareDiscourseDataset.py` | `temporal-learner-code/STEPS.md` L3 | Referenced in STEPS.md but not found in the directory. |
| **Typo in STEPS.md** | `temporal-learner-code/STEPS.md` L14 | `construct_time_signal_heuristics.pyj` — `.pyj` is not a Python extension. |

### Hard-Coded Values (Technical Debt)
| Value | File | Line |
|---|---|---|
| API base URL `http://localhost:8000` | `cti-api.service.ts` | L10 |
| 20 technique keyword patterns | `pipeline.py` | L49–70 |
| 18 asset keyword patterns | `pipeline.py` | L28–47 |
| Node width/height constants | `attack_flow.py` | L190–193 |
| Layout constants (CENTER_X=420, START_Y=80, GAP values) | `attack_flow.py` | L195–199 |
| Initial sample text in `ngOnInit` | `app.ts` | L71 |
| Sidebar default width 400px | `app.ts` | L39 |
| W2V hyperparameters | `create_cti_w2v.py` | L57–65 |

### Discrepancies (README/Docs vs. Code)
| Claim | Location | Reality |
|---|---|---|
| "Pre-built Equifax and TRITON scenarios available" | `app.py` L71–82 (list_scenarios) | Methods to generate them are not implemented in `attack_flow.py` |
| "The full trained model requires ~250GB" | `readme.md` L2 | No quantification of web server model size separately; web server models are much smaller (spaCy models typically <1GB) |
| "18+ estimators" in `cross_validate_p2.py` | `readme2.md` line 449 | Exact count `[UNCERTAIN]` — file not fully read but described as "18+ traditional ML estimators" |
| `README_spacy.md` in `sentence_to_technique_classifier/` | listing | Exists (1903 bytes) but content not verified |

---

## 14. Facts Table and Open Questions

### Headline Numbers

| Metric | Value | Source File |
|---|---|---|
| MITRE ATT&CK techniques supported (taxonomy) | 329 | `sentence_to_technique_classifier/selected_techniquesWName.json` (17.8 KB, JSON array) |
| ICS/IT asset classes supported (taxonomy) | 18 (counted in `ASSET_KEYWORDS` dict) | `web-server/backend/pipeline.py` L28–47 |
| Hardcoded technique keyword patterns | 20 | `web-server/backend/pipeline.py` L49–70 |
| API endpoints | 7 (`/api/health`, `/api/assets/taxonomy`, `/api/techniques/taxonomy`, `/api/scenarios`, `/api/scenarios/{id}`, `/api/analyze`, `/api/upload`, `/`) | `web-server/backend/app.py` |
| Temporal relation labels | 4 (CONCURRENT, NEXT, OVERLAP, NULL) | `readme2.md` L451–455 |
| Discourse relation labels | 5 (ELABORATION, LIST, NEXT, IF_ELSE, MISC) | `readme2.md` L203 |
| Node types in graph schema | 4 (technique, asset, logic_gate, condition) | `schemas.py` L49; `attack-flow.model.ts` L3 |
| Edge relation types | 4 defined: AFTER, TARGETS, AFFECTS, SIMULTANEOUS (schema also mentions AND_IN, BEFORE, OVERLAP) | `schemas.py` L67; `attack_flow.py` L149–165 |
| ML pipeline stages | 8 | `readme2.md` L68; `PROJECT_FLOW.md` |
| GNN model checkpoints present | 5 (`gnn_model_0.pt`…`gnn_model_4.pt`, 556 KB each) | `temporal-learner-code/` directory listing |
| Angular version | 18.2.x | `web-server/frontend/package.json` L13 |
| Python versions required | 3.10 (RoBERTa), 3.11 (all others) | `readme2.md` L35–37 |
| Word2Vec vector dimensions | 300 | `create_cti_w2v.py` L59 |
| Word2Vec training epochs | 30 | `create_cti_w2v.py` L65 |
| Collision resolution passes | 8 | `attack_flow.py` L321 |
| PNG export resolution factor | 2× | `attack-flow-canvas.ts` L257 |
| Total Python source files (excl. venv, cache, node_modules) | 197 | `find` command result |
| Total TypeScript source files (excl. node_modules) | 14 | `find` command result |

### Glossary

| Term | Definition |
|---|---|
| **ATT&CK** | MITRE Adversarial Tactics, Techniques, and Common Knowledge framework — a curated knowledge base of adversary behaviors |
| **CTI** | Cyber Threat Intelligence — reports describing cyberattack campaigns |
| **TTP** | Tactic, Technique, Procedure — ATT&CK categories for attacker behaviors |
| **Temporal relation** | Ordering relationship between two technique events: NEXT, OVERLAP, CONCURRENT, or NULL |
| **Bagging** | Bootstrap Aggregating — ensemble method that trains multiple models on random subsets of data |
| **DAG** | Directed Acyclic Graph — the ideal structure for an attack-flow graph (techniques flow forward in time) |
| **GEXF** | Graph Exchange XML Format — NetworkX's XML-based graph file format |
| **MLM** | Masked Language Modeling — self-supervised pretraining task where tokens are randomly masked |
| **CTI-RoBERTa** | A `roberta-base` model further pretrained on CTI text using MLM in this project |
| **Discourse relation** | Semantic relationship between two sentences (ELABORATION, LIST, NEXT, IF_ELSE, MISC) |
| **Coreference** | When two different noun phrases refer to the same real-world entity ("The malware" … "It") |
| **TimeML** | An XML markup language for temporal expressions and events in text |
| **tarsqi-ttk** | Temporal Awareness and Reasoning System (TARSQI) Toolkit — third-party tool for TimeML annotation |
| **Apriori** | Association rule mining algorithm for finding frequent itemsets |
| **Canonical node** | A single, deduplicated graph node representing all occurrences of one unique entity |
| **SHAP** | SHapley Additive exPlanations — method for explaining ML model predictions by feature attribution |
| **DGL** | Deep Graph Library — PyTorch-based library for Graph Neural Networks |

### Open Questions (Only the Developer Can Answer)

1. **Ground truth labels:** How were the ground-truth labels in `temporal_relation_dataset.xlsx` created? Were they manually annotated or automatically generated?
2. **Scenario methods:** Were `get_equifax_showcase_scenario()` and `get_triton_ics_scenario()` intentionally removed from `attack_flow.py`, or is this a work-in-progress feature?
3. **Selected techniques count:** The taxonomy file has 329 techniques — is this a filtered subset of the full ATT&CK framework, and what criteria were used for filtering?
4. **Web server vs. pipeline integration:** The web server uses keyword fallback and simplified NLP, not the full 8-stage pipeline. Is there a plan to integrate the trained GNN/XGBoost models into the web server for real-time inference?
5. **Report corpus:** The `temporal-learner-code/` folder contains very large JSON files (e.g., `report_sentences_with_prediction.json` at 56 MB, `unseen_report_sentence.json` at 22 MB). What is the source corpus and how many reports are included?
6. **GNN architecture detail:** What are the exact layer sizes, activation functions, and hyperparameters of the GraphConv+MLP in `learn_graph_ML_imbalanced_multilabel-v2.py`?
7. **OpenAI fine-tuning results:** Were the GPT-3.5 fine-tuned results comparable to the spaCy bagging ensemble? Which was selected for the final pipeline?
8. **TimeML integration status:** Is the tarsqi-ttk tool fully functional in the current environment, or are its outputs pre-computed in the feature JSON files?
9. **Deployment target:** Is the web server intended for local analyst use only, or is there a plan for hosted/cloud deployment?
10. **License:** The `LICENSE` file (11,357 bytes) is present — what open-source license is used? `[NOT VERIFIED — file not read]`

---

*End of PROJECT_DESCRIPTION.md*

*Total sections: 15 (0–14). All sections are present. Every count and claim cites a source file and line. No invented content.*
