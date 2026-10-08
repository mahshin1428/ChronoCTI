# ChronoCTI — Project Flow & Architecture

**ChronoCTI** is an NLP/ML pipeline that reads Cyber Threat Intelligence (CTI) reports and predicts *temporal relationships* between MITRE ATT&CK techniques — i.e., which technique happens **before**, **after**, **during**, or **concurrently** with another in a given intrusion narrative.

> **Input:** Raw text CTI reports (`.md` or `.txt`).  
> **Output:** Per-report directed graphs (`.gexf`) where nodes = ATT&CK techniques and edges = temporal relations (`NEXT`, `OVERLAP`, `CONCURRENT`).

---

## High-Level Pipeline Overview

The project is organized into **8 conceptual stages**. Data generally flows left-to-right, with several parallel feature-extraction branches that converge at the final learning step.

```
Raw CTI Reports
      │
      ▼
┌─────────────────┐
│ 1. Custom       │
│    Embeddings   │  ← trains domain-specific Word2Vec on CTI corpus
└────────┬────────┘
         │
         ▼
┌─────────────────┐
│ 2. RoBERTa-CTI  │  ← further pre-trains RoBERTa on CTI text
│    + Discourse  │  ← trains sentence-pair discourse classifiers
└────────┬────────┘
         │
         ▼
┌─────────────────┐     ┌──────────────────┐     ┌──────────────────┐
│ 3. Sentence →   │     │ 4. Coreference   │     │ 5. TimeML        │
│    Technique    │     │    Resolution    │     │    Extraction    │
│    Classifier   │     │                  │     │                  │
└────────┬────────┘     └────────┬─────────┘     └────────┬─────────┘
         │                       │                        │
         └───────────┬───────────┘────────────────────────┘
                     ▼
         ┌──────────────────┐
         │ 6. Feature       │  ← combines everything into tabular
         │    Engineering   │    examples (TTP-pair rows)
         └────────┬─────────┘
                  │
                  ▼
         ┌──────────────────┐
         │ 7. Apriori /     │  ← static association-rule features
         │    Assoc. Rules  │
         └────────┬─────────┘
                  │
                  ▼
         ┌──────────────────┐
         │ 8. Temporal      │  ← trains GNN + XGBoost classifiers
         │    Relation      │    to predict CONCURRENT / NEXT /
         │    Learner       │    OVERLAP / NULL
         └────────┬─────────┘
                  │
                  ▼
         ┌──────────────────┐
         │ Final Graphs     │  ← per-report .gexf attack-flow graphs
         │ (.gexf)          │
         └──────────────────┘
```

---

## Stage 1: Custom Embeddings
**Purpose:** Build a domain-specific word vector space so downstream NLP models understand CTI vocabulary better.

| | |
|---|---|
| **Key Script** | `create_cti_w2v.py` |
| **Inputs** | `Datasets/relevance_train.jsonl`, `relevance_eval.jsonl`, `all_report_sentences.jsonl` |
| **What it does** | Trains a Word2Vec model (gensim) on all CTI sentences, filtering stop-words and extracting bigrams. Then converts the vectors into a spaCy-compatible model. |
| **Output** | `Datasets/cti_w2v_v2` — a spaCy word-vector model customized for the CTI domain. |

This custom embedding is later used by the spaCy sentence-to-technique classifiers.

---

## Stage 2: RoBERTa-CTI Pretraining + Discourse Classifiers
**Purpose:** Create a language model that "speaks CTI" and learn to classify the semantic relationship between pairs of sentences.

| | |
|---|---|
| **Folder** | `roberta_cti_and_discourse_classifier/` |
| **Key Scripts** | `mlm.py`, `train_discourse_relation.py`, `train_discourse_relation_coref.py` |
| **Inputs** | `train.txt`, `test.txt` (raw CTI text), `discourse_train_v2.json`, `discourse_train_v2_coref.json` |

### 2a. Masked Language Modeling (`mlm.py`)
- Further pre-trains `roberta-base` on CTI corpora using masked language modeling.
- Output: a custom `CTI-Roberta` checkpoint.

### 2b. Discourse Relation Classifiers
- `train_discourse_relation.py` — trains a sentence-pair classifier on **consecutive** sentences. Labels: `ELABORATION`, `LIST`, `NEXT`, `IF_ELSE`, `MISC`.
- `train_discourse_relation_coref.py` — same task but for **coreferenced** (non-consecutive) sentence pairs.

Both classifiers feed into Stage 6 by providing discourse-relation features for any pair of techniques that appear in related sentences.

---

## Stage 3: Sentence → Technique Classifier
**Purpose:** Tag every sentence in a report with the MITRE ATT&CK techniques it describes, along with confidence scores.

| | |
|---|---|
| **Folder** | `sentence_to_technique_classifier/` |
| **Key Scripts** | `train_models.py`, `openai/fine_tune.py` |
| **Inputs** | Report sentences; spaCy configs (`config-w2v.cfg`, `config-lg.cfg`, `config-trf.cfg`, `config-roberta-base.cfg`, `config-roberta-cti.cfg`); `selected_techniquesWName.json` |

### What it does
-Ensembling (Bagging) and Comparative Analysis are core research techniques. So here we are evaluating the performance of the model with different embedding. This helps in selecting the best performing model for the downstream task.
- Trains multiple spaCy text-c=lassification models in a bagging setup (5-fold splits), each using a different embedding source:
  - `w2vAll` — custom CTI Word2Vec (Stage 1)
  - `lgAll` — spaCy `en_core_web_lg` vectors
  - `trfAll` — transformer embeddings
  - `robertaBaseAll` — off-the-shelf RoBERTa
  - `robertaCtiAll` — domain-adapted CTI-RoBERTa (Stage 2a)
- Also supports OpenAI GPT-3.5 fine-tuning (`openai/fine_tune.py`) for comparison.

### Output
- `report_sentences_with_prediction.json` / `unseen_report_sentences_with_prediction.json`
- Each entry contains the report ID, the sentence text, and a list of predicted techniques with probabilities.

> **Downstream impact:** This is the *backbone* of the entire pipeline. Almost every later stage consumes these technique predictions to know which techniques appear in which sentences.

---

## Stage 4: Coreference Resolution
**Purpose:** Identify sentences that talk about the same entity even when they are not consecutive (e.g., “The malware … It then …”).

| | |
|---|---|
| **Folder** | `Neuralcoref/` |
| **Key Script** | `construct_dataset_of_coreferred_sentences.py` |
| **Inputs** | Raw reports (`unseen_reports/`); sentence predictions from Stage 3 |
| **What it does** | Runs spaCy’s experimental coreference model (`en_coreference_web_trf`) over each report, finds clusters of sentences referring to the same entity, and records non-consecutive sentence pairs within each cluster. |
| **Outputs** | `unseen_report_coreferenced_sentences.json`, `unseen_report_coreferenced_clusters.json` |

These outputs feed directly into Stage 2b (coref discourse classifier) and Stage 6 (coref-based features).

---

## Stage 5: TimeML Temporal Extraction
**Purpose:** Extract explicit temporal expressions and events from reports and map them to ATT&CK techniques.

| | |
|---|---|
| **Folder** | `TimeML/` |
| **Key Scripts** | `obtain_cti_report_to_timeML.py`, `convert_timeML_to_json.py`, `classify_temporal_events_to_TTPs.py`, `construct_features_from_timeML.py` |
| **What it does** | Uses `tarsqi-ttk` (TimeML toolkit) to annotate temporal events and relations in CTI text, converts the events into noun/verb phrases, links them to ATT&CK techniques, and extracts TimeML relation features per TTP pair. |
| **Outputs** | TimeML feature JSONs per report (e.g., `BEFORE_TIMEML`, `AFTER_TIMEML`, `DURING_TIMEML`, `SIMULTANEOUS_TIMEML`, etc.) |

This is one of the “semantic temporal signal” branches that converge in Stage 6.

---

## Stage 6: Feature Engineering (The “Combination Kitchen”)
**Purpose:** Merge all signals into a single tabular dataset where each row = one ordered TTP pair in one report, and columns = features from every upstream branch.

| | |
|---|---|
| **Folder** | `temporal-learner-code/` |
| **Key Scripts** | `construct_consecutive_sentence_features.py`, `construct_coref_sentence_features.py`, `construct_similarity_features.py`, `construct_time_signal_heuristics.py`, `construct_features_from_next_discourse_relation.py`, `construct_features_from_next_discourse_relation_coref.py`, `combine_all_features.py` |

### Feature families created
1. **BASIC** — top-5 confidence scores for each technique (`T1_P0..P4`, `T2_P0..P4`).
2. **SENTENCE** — proximity features (`consecutive_sentence_n1..n5`, `consecutive_sentence_p1..p5`), `same_sentence`, sentence similarity, `same_coreference_cluster`.
3. **DISCOURSE** — discourse-relation probabilities from Stage 2 (`ELABORATION_NEXT`, `NEXT_NEXT`, `LIST_NEXT`, `ELABORATION_COREF`, `NEXT_COREF`, etc.).
4. **AMR** (Association Rule Mining) — static association metrics from Stage 7 (`supportXY_AMR`, `confidence_AMR`, `jaccard_AMR`, `pmi_AMR`, etc.).
5. **TIMEML** — temporal relations from Stage 5 (`BEFORE_TIMEML`, `AFTER_TIMEML`, `DURING_TIMEML`, `SIMULTANEOUS_TIMEML`, etc.).
6. **TIME SIGNAL HEURISTIC** — simple lexical counts of temporal adverbs (`heuristic_next`, `heuristic_overlap`, `heuristic_concurrent`) in sentences.

### Output
- `unseen_reports_features/all_reports_threshold_95.json` (and similar)
- A large JSON where each element is a feature vector for a single `(report, T1, T2)` triple.

---

## Stage 7: Apriori / Association Rule Mining
**Purpose:** Compute statistical co-occurrence patterns across the ATT&CK technique corpus.

| | |
|---|---|
| **Folder** | `apriori-features/` |
| **Key Script** | `construct_association_rule_mining_features.py` |
| **What it does** | Runs the apriori algorithm on technique co-occurrence data derived from ATT&CK procedures. Computes association-rule metrics (support, confidence, conviction, lift, phi, jaccard, PMI, etc.) for every ordered TTP pair. |
| **Output** | `unseen_reports_rule_mining_features.json` — static features consumed by Stage 6. |

> These features are *report-independent*: they capture general world-knowledge about which techniques tend to appear together, regardless of the specific report.

---

## Stage 8: Temporal Relation Learner & Evaluation
**Purpose:** Train machine learning models to predict the temporal relation between two techniques given all the engineered features.

| | |
|---|---|
| **Folder** | `temporal-learner-code/` |
| **Key Scripts** | `learn_graph_ML_imbalanced_multilabel-v2.py`, `make_final_evaluation.py`, `cross_validate_p2.py`, `Utils.py` |
| **Inputs** | Combined feature dataset from Stage 6; `temporal_relation_dataset.xlsx` (ground-truth labels); `selected_techniquesWName.json` |

### Labels
Each TTP pair is labeled with one or more of:
- `CONCURRENT` — both techniques happen at the same time
- `NEXT` — one strictly precedes the other
- `OVERLAP` — their time windows partially overlap
- `NULL` — no temporal relation

### Models trained
1. **Graph Neural Network (DGL)** — `learn_graph_ML_imbalanced_multilabel-v2.py` builds per-report directed graphs where nodes = techniques (with confidence features) and edges = all possible TTP pairs (with the engineered features from Stage 6). It trains a GraphConv + MLP predictor with BCE loss.
2. **XGBoost (MultiOutput)** — `make_final_evaluation.py` trains an XGBoost classifier on the tabular feature vectors and evaluates with standard multi-label metrics plus Precision@K and Recall@K.
3. **Cross-validation benchmark** — `cross_validate_p2.py` / `Utils.py` compares 18+传统 ML estimators (Random Forest, SVM, MLP, AdaBoost, etc.) across different feature subsets using 5-fold CV.

### Evaluation metrics
- Macro F1, Precision, Recall
- Precision@K / Recall@K (per relation)
- NDCG, Coverage Error
- SHAP feature-importance analysis (grouped by feature family)
- MUC-style graph-edit-distance for graph-level evaluation

### Output
- Trained model checkpoints (`.pt`, `.pkl`)
- Evaluation JSONs / Excel files (`results.json`, `cross_validation/...`)
- **Per-report attack-flow graphs** (`.gexf` files in `input and outputs/`) showing predicted temporal edges between techniques

---

## Typical Execution Order (from README)

If you want to *run* the pipeline end-to-end, the README suggests this order:

1. `pipenv install` + `python -m spacy download en_core_web_lg`
2. `create_cti_w2v.py` → custom embeddings
3. `roberta_cti_and_discourse_classifier/`
   - `mlm.py`
   - `train_discourse_relation.py`
   - `train_discourse_relation_coref.py`
4. `sentence_to_technique_classifier/`
   - `train_models.py`
   - `openai/fine_tune.py`
5. `TimeML/` → follow `STEPS.md`
6. `apriori-features/` → follow `STEPS.md`
7. `Neuralcoref/` → coreference extraction
8. `temporal-learner-code/` → feature construction + learning + evaluation (follow `STEPS.md`)

---

## Key Data Artifacts You’ll See

| File / Folder | What it holds |
|---|---|
| `Datasets/*.jsonl` | Raw sentences from ATT&CK, TRAM, and other CTI sources |
| `unseen_reports/` | Raw `.md` / `.txt` CTI reports to be analyzed |
| `report_sentences_with_prediction.json` | Every sentence tagged with predicted techniques |
| `unseen_reports_features/*.json` | Per-report feature vectors for every TTP pair |
| `temporal_relation_dataset.xlsx` | Ground-truth labels for training/evaluation |
| `input and outputs/*_graph.gexf` | Final predicted attack-flow graphs |
| `*.xlsx` (Features, patterns, links) | Intermediate analysis spreadsheets |

---

*End of document. For deeper code-level details, inspect the individual scripts in each folder.*
