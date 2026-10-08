# ChronoCTI

ChronoCTI is an NLP+ML pipeline for identifying **temporal patterns of cyberattack TTPs** (Tactics, Techniques, and Procedures) from Cyber Threat Intelligence (CTI) reports. Given a raw CTI report, it predicts temporal relations between MITRE ATT&CK techniques — e.g., Technique A happens **NEXT** to Technique B, they **OVERLAP**, or happen **CONCURRENTLY**.

> **Input:** Raw CTI reports (`.md`, `.txt`)  
> **Output:** Per-report attack-flow graphs (`.gexf`) showing temporal relationships between techniques.

**⚠️ Important:** This repository contains source code only. Intermediate model outputs are not included. The full trained model requires approximately **250GB** of disk space. Please open an issue if you need access to pretrained artifacts.

---

## Table of Contents

1. [Prerequisites](#prerequisites)
2. [Quick Start Overview](#quick-start-overview)
3. [Stage 1: Custom Word Embeddings](#stage-1-custom-word-embeddings)
4. [Stage 2: RoBERTa-CTI + Discourse Classifiers](#stage-2-roberta-cti--discourse-classifiers)
5. [Stage 3: Sentence → Technique Classifier](#stage-3-sentence--technique-classifier)
6. [Stage 4: Coreference Resolution](#stage-4-coreference-resolution)
7. [Stage 5: TimeML Temporal Extraction](#stage-5-timeml-temporal-extraction)
8. [Stage 6: Feature Engineering](#stage-6-feature-engineering)
9. [Stage 7: Apriori / Association Rule Mining](#stage-7-apriori--association-rule-mining)
10. [Stage 8: Temporal Relation Learning & Evaluation](#stage-8-temporal-relation-learning--evaluation)
11. [Data Artifacts Reference](#data-artifacts-reference)
12. [Troubleshooting](#troubleshooting)

---

## Prerequisites

### System Requirements

- **OS:** Linux, macOS, or WSL (Windows Subsystem for Linux)
- **Python:** Multiple versions are used across submodules:
  - Root / TimeML / Neuralcoref: **Python 3.11**
  - RoBERTa-CTI: **Python 3.10**
  - Sentence Classifier / Temporal Learner: **Python 3.11**
- **GPU:** Optional but **strongly recommended** for RoBERTa training and spaCy transformers. If you have a GPU, install CUDA-compatible PyTorch.
- **Disk:** ~250GB for full model artifacts; ~5GB minimum for code + basic datasets

### Global Tools to Install

```bash
# 1. Install pipenv globally
pip install pipenv

# 2. Install spaCy and download the large English model
pip install spacy
python -m spacy download en_core_web_lg
```

### Environment Requirements Summary

| Module | Python | Key Packages |
|--------|--------|--------------|
| Root | 3.11 | spacy, gensim, jsonlines |
| RoBERTa-CTI | 3.10 | torch, simpletransformers, transformers==4.30.2, sklearn |
| Sentence Classifier | * | spacy, spacy-transformers, torch, skorch, transformers, openai |
| Temporal Learner | 3.11 | torch, dgl, xgboost, networkx, scikit-learn, imbalanced-learn, skmultilearn, skorch, shap, pytorch-tabnet, sentence-transformers |
| TimeML | 3.11 | spacy, beautifulsoup4, lxml, benepar, flask |
| Neuralcoref | 3.11 | spacy, spacy-transformers, spacy-experimental, torch, en_coreference_web_trf |
| Apriori | 3.11 | pandas, mlxtend, networkx, stix2, scikit-learn |

---

## Quick Start Overview

The pipeline has **8 stages**. Below is the recommended order to run them. Each stage is explained in detail afterward.

```bash
# Stage 1: Custom Embeddings (root directory)
pipenv install
pipenv shell
python -m spacy download en_core_web_lg
python create_cti_w2v.py

# Stage 2: RoBERTa-CTI + Discourse (roberta_cti_and_discourse_classifier/)
cd roberta_cti_and_discourse_classifier/
pipenv install
pipenv shell
python mlm.py
python train_discourse_relation.py
python train_discourse_relation_coref.py
cd ..

# Stage 3: Sentence→Technique (sentence_to_technique_classifier/)
cd sentence_to_technique_classifier/
pipenv install
# If you have a GPU: edit Pipfile and uncomment `cupy`
pipenv shell
export OPENAI_API_KEY="your-key-here"
cp ../Datasets/cti-w2v_v2 ./cti_w2v_v2
cp -r ../roberta_cti_and_discourse_classifier/Roberta-CTI ./
python train_models.py
python openai/fine_tune.py
cd ..

# Stage 4: Coreference (Neuralcoref/)
cd Neuralcoref/
pipenv install
pipenv shell
python construct_dataset_of_coreferred_sentences.py
cd ..

# Stage 5: TimeML (TimeML/)
cd TimeML/
pipenv install
pipenv shell
python obtain_cti_report_to_timeML.py
python convert_timeML_to_json.py
python classify_temporal_events_to_TTPs.py
python construct_features_from_timeML.py
cd ..

# Stage 6-8: Temporal Learner (temporal-learner-code/)
cd temporal-learner-code/
pipenv install
pipenv shell

# Feature construction
python construct_consecutive_sentence_features.py
python construct_coref_sentence_features.py
python construct_similarity_features.py
python construct_time_signal_heuristics.py
python construct_features_from_next_discourse_relation.py
python construct_features_from_next_discourse_relation_coref.py

# Combine all features
python combine_all_features.py

# Train and evaluate
python make_final_evaluation.py
python learn_graph_ML_imbalanced_multilabel-v2.py
python cross_validate_p2.py
cd ..
```

---

## Stage 1: Custom Word Embeddings

**Purpose:** Train a Word2Vec model on CTI corpus vocabulary so downstream models understand domain-specific terms.

**Directory:** Repository root (`/`)

**Python Version:** 3.11

**Steps:**

```bash
# From the repository root
pipenv install
pipenv shell
python -m spacy download en_core_web_lg
python create_cti_w2v.py
```

**What it does:**
- Reads sentences from `Datasets/relevance_train.jsonl`, `relevance_eval.jsonl`, and `all_report_sentences.jsonl`
- Removes stop words, extracts bigrams
- Trains Word2Vec (300-dim vectors, window=5, min_count=5)
- Converts the vectors into a spaCy-compatible model

**Outputs:**
- `Datasets/w2v_cti_reports-v2.txt` — word vectors in text format
- `Datasets/cti_w2v_v2` — spaCy model with CTI word vectors

> **Note:** You will need to copy `Datasets/cti_w2v_v2` into the `sentence_to_technique_classifier/` directory in Stage 3.

---

## Stage 2: RoBERTa-CTI + Discourse Classifiers

**Purpose:** Further pre-train RoBERTa on CTI text and train discourse-relation classifiers for sentence pairs.

**Directory:** `roberta_cti_and_discourse_classifier/`

**Python Version:** 3.10

**Prerequisites:** Ensure you have `train.txt` and `test.txt` in this directory.

**Steps:**

```bash
cd roberta_cti_and_discourse_classifier/
pipenv install
pipenv shell

# 2a. Train RoBERTa-CTI (masked language modeling)
python mlm.py

# After training, copy the best model checkpoint
mkdir -p Roberta-CTI
cp CTI-Roberta/outputs_*/model-best/* Roberta-CTI/

# 2b. Train discourse relation classifiers
python train_discourse_relation.py        # for consecutive sentences
python train_discourse_relation_coref.py   # for coreferenced sentences
```

**What it does:**
- `mlm.py` — further pre-trains `roberta-base` on CTI text with masked language modeling
- `train_discourse_relation.py` — trains a sentence-pair classifier on consecutive sentences for discourse relations (`ELABORATION`, `LIST`, `NEXT`, `IF_ELSE`, `MISC`)
- `train_discourse_relation_coref.py` — same task for coreferenced (non-consecutive) sentence pairs

**Outputs:**
- `CTI-Roberta/outputs_*/model-best/` — the domain-adapted RoBERTa checkpoint
- Trained discourse classifiers (saved by `simpletransformers`)

> **Note:** You will need to copy the `Roberta-CTI` folder into `sentence_to_technique_classifier/` in Stage 3.

---

## Stage 3: Sentence → Technique Classifier

**Purpose:** Classify each sentence in a CTI report to zero or more MITRE ATT&CK techniques.

**Directory:** `sentence_to_technique_classifier/`

**Python Version:** Flexible (use 3.11)

**Prerequisites:**
- Custom word vectors from Stage 1: `cp ../Datasets/cti-w2v_v2 ./cti_w2v_v2`
- RoBERTa-CTI from Stage 2: `cp -r ../roberta_cti_and_discourse_classifier/Roberta-CTI ./`
- OpenAI API key (optional, for GPT fine-tuning): `export OPENAI_API_KEY="your-key"`

**Steps:**

```bash
cd sentence_to_technique_classifier/
pipenv install

# IMPORTANT: If you have a GPU, edit the Pipfile and uncomment the `cupy` line
# This is required for GPU-accelerated spaCy processing

pipenv shell
export OPENAI_API_KEY="your-key-here"

# Copy dependencies from previous stages
cp ../Datasets/cti-w2v_v2 ./cti_w2v_v2
cp -r ../roberta_cti_and_discourse_classifier/Roberta-CTI ./

# Train spaCy textcat models (w2v, lg, trf, roberta-base, roberta-cti)
python train_models.py

# Optional: Fine-tune OpenAI GPT-3.5 for comparison
python openai/fine_tune.py
```

**What it does:**
- `train_models.py` trains 5 different spaCy textcat models in a bagging setup (5-fold CV), each with different embeddings:
  - `w2vAll` — custom CTI Word2Vec
  - `lgAll` — spaCy `en_core_web_lg`
  - `trfAll` — transformer embeddings
  - `robertaBaseAll` — off-the-shelf RoBERTa
  - `robertaCtiAll` — domain-adapted CTI-RoBERTa
- `openai/fine_tune.py` fine-tunes GPT-3.5 for sentence-to-technique classification

**Outputs:**
- `bagging_models/` — trained spaCy models
- `report_sentences_with_prediction.json` or similar — every sentence tagged with predicted techniques and probabilities

> **This is the backbone of the pipeline.** Almost every downstream stage consumes these sentence predictions.

---

## Stage 4: Coreference Resolution

**Purpose:** Identify sentences that talk about the same entity even when not consecutive.

**Directory:** `Neuralcoref/`

**Python Version:** 3.11

**Prerequisites:** `en_coreference_web_trf` spaCy model (installed via Pipfile)

**Steps:**

```bash
cd Neuralcoref/
pipenv install
pipenv shell
python construct_dataset_of_coreferred_sentences.py
```

**What it does:**
- Reads raw reports from `unseen_reports/` (or `reports/`)
- Uses spaCy `en_coreference_web_trf` to find coreference clusters
- Extracts non-consecutive sentence pairs within each cluster

**Outputs:**
- `unseen_report_coreferenced_sentences.json`
- `unseen_report_coreferenced_clusters.json`

---

## Stage 5: TimeML Temporal Extraction

**Purpose:** Extract explicit temporal expressions and events from reports and map them to ATT&CK techniques.

**Directory:** `TimeML/`

**Python Version:** 3.11

**Prerequisites:** You need to install `tarsqi-ttk` (TimeML Toolkit) separately. This directory contains modified tarsqi-ttk source code.

**Steps:**

```bash
cd TimeML/
pipenv install
pipenv shell

# TimeML processing pipeline
python obtain_cti_report_to_timeML.py
python convert_timeML_to_json.py
python classify_temporal_events_to_TTPs.py
python construct_features_from_timeML.py
```

**What it does:**
1. `obtain_cti_report_to_timeML.py` — converts CTI reports to TimeML XML using tarsqi-ttk
2. `convert_timeML_to_json.py` — converts TimeML events to noun/verb phrases
3. `classify_temporal_events_to_TTPs.py` — maps temporal events to ATT&CK techniques
4. `construct_features_from_timeML.py` — extracts TimeML relation features per TTP pair (e.g., `BEFORE_TIMEML`, `AFTER_TIMEML`, `DURING_TIMEML`, `SIMULTANEOUS_TIMEML`)

**Outputs:**
- TimeML XML files per report
- JSON features per TTP pair per report

> **Note:** For detailed tarsqi-ttk installation instructions, see the [official documentation](https://tarsqi.github.io/ttk/versions/3.0.1/index.html).

---

## Stage 6: Feature Engineering

**Purpose:** Merge all signals into a single tabular dataset where each row = one ordered TTP pair in one report.

**Directory:** `temporal-learner-code/`

**Python Version:** 3.11

**Prerequisites:** All previous stages must have produced their output files.

**Steps:**

```bash
cd temporal-learner-code/
pipenv install
pipenv shell

# Run feature construction scripts in any order
python construct_consecutive_sentence_features.py    # SENTENCE features
python construct_coref_sentence_features.py           # coreference-based features
python construct_similarity_features.py               # sentence similarity
python construct_time_signal_heuristics.py            # lexical temporal signals
python construct_features_from_next_discourse_relation.py       # discourse for next sentences
python construct_features_from_next_discourse_relation_coref.py # discourse for coref sentences

# Combine everything into one dataset
python combine_all_features.py
```

**What each script produces:**
- `construct_consecutive_sentence_features.py` — proximity features (n sentences before/after), `same_sentence`
- `construct_coref_sentence_features.py` — coreference-based proximity features
- `construct_similarity_features.py` — semantic similarity between techniques
- `construct_time_signal_heuristics.py` — counts of temporal adverbs (`after`, `before`, `during`, etc.)
- `construct_features_from_next_discourse_relation.py` — discourse relation probabilities for consecutive sentences (`ELABORATION_NEXT`, `NEXT_NEXT`, etc.)
- `construct_features_from_next_discourse_relation_coref.py` — discourse relation probabilities for coreferenced sentences (`ELABORATION_COREF`, `NEXT_COREF`, etc.)
- `combine_all_features.py` — merges all feature families into one JSON per report

**Feature Families in Combined Output:**
| Family | Examples |
|--------|----------|
| BASIC | `T1_P0..P4`, `T2_P0..P4` (technique probabilities) |
| SENTENCE | `consecutive_sentence_n1..n5`, `same_sentence`, `similarity` |
| DISCOURSE | `ELABORATION_NEXT`, `NEXT_NEXT`, `ELABORATION_COREF`, `NEXT_COREF` |
| AMR | `supportXY_AMR`, `confidence_AMR`, `jaccard_AMR`, `pmi_AMR` |
| TIMEML | `BEFORE_TIMEML`, `AFTER_TIMEML`, `DURING_TIMEML`, `SIMULTANEOUS_TIMEML` |
| TIME SIGNAL | `heuristic_next`, `heuristic_overlap`, `heuristic_concurrent` |

**Outputs:**
- `unseen_reports_features/all_reports_threshold_95.json` (and variants)
- Each entry is a feature vector for a `(report, T1, T2)` triple

---

## Stage 7: Apriori / Association Rule Mining

**Purpose:** Compute statistical co-occurrence patterns across the ATT&CK technique corpus.

**Directory:** `apriori-features/`

**Python Version:** 3.11

**Steps:**

```bash
cd apriori-features/
pipenv install
pipenv shell
python construct_association_rule_mining_features.py
```

**What it does:**
- Runs the apriori algorithm on ATT&CK technique co-occurrence data
- Computes association metrics for every ordered TTP pair: support, confidence, conviction, lift, phi, jaccard, PMI, etc.
- These features are **report-independent** — they capture general world-knowledge about which techniques tend to appear together

**Outputs:**
- `unseen_reports_rule_mining_features.json`

> **Note:** This only needs to be run once. The features are static across all reports.

---

## Stage 8: Temporal Relation Learning & Evaluation

**Purpose:** Train ML models to predict temporal relations between techniques.

**Directory:** `temporal-learner-code/`

**Python Version:** 3.11

**Prerequisites:**
- Combined feature dataset from Stage 6
- Ground-truth labels in `temporal_relation_dataset.xlsx`

**Steps:**

```bash
cd temporal-learner-code/
pipenv shell

# Train XGBoost multi-output classifier and evaluate
python make_final_evaluation.py

# Train Graph Neural Network (DGL) for edge classification
python learn_graph_ML_imbalanced_multilabel-v2.py

# Cross-validate multiple estimators (Random Forest, SVM, MLP, etc.)
python cross_validate_p2.py
```

**What each script does:**
- `make_final_evaluation.py` — trains XGBoost MultiOutputClassifier, evaluates with precision@K, recall@K, NDCG, coverage error, and SHAP feature importance analysis
- `learn_graph_ML_imbalanced_multilabel-v2.py` — builds per-report directed graphs (nodes=techniques, edges=TTP pairs), trains GraphConv + MLP predictor with BCE loss
- `cross_validate_p2.py` — benchmarks 18+ traditional ML estimators across different feature subsets using 5-fold CV

**Labels:**
- `CONCURRENT` — techniques happen simultaneously
- `NEXT` — one strictly precedes the other
- `OVERLAP` — time windows partially overlap
- `NULL` — no temporal relation

**Outputs:**
- Trained model checkpoints (`*.pt`, `*.pkl`)
- Evaluation results (`results.json`, `cross_validation/*.json`)
- **Per-report attack-flow graphs** (`.gexf` files in `input and outputs/`)

---

## Data Artifacts Reference

| File / Folder | Description |
|---------------|-------------|
| `Datasets/*.jsonl` | Source sentences from ATT&CK, TRAM, and other CTI datasets |
| `unseen_reports/` | Raw `.md` / `.txt` CTI reports to analyze |
| `report_sentences_with_prediction.json` | Every sentence tagged with predicted ATT&CK techniques and probabilities |
| `unseen_report_coreferenced_sentences.json` | Coreferenced sentence pairs per report |
| `unseen_reports_features/*.json` | Per-report feature vectors for all TTP pairs |
| `temporal_relation_dataset.xlsx` | Ground-truth temporal relation labels for training/evaluation |
| `input and outputs/*_graph.gexf` | Final predicted attack-flow graphs |
| `selected_techniquesWName.json` | List of ATT&CK techniques used in the pipeline |

---

## Troubleshooting

### Module Not Found Errors
Each submodule has its own `Pipfile` and virtual environment. **Always** run `pipenv install && pipenv shell` before running scripts in a new directory.

### GPU Issues
- If you have a GPU, uncomment `cupy` in `sentence_to_technique_classifier/Pipfile` before `pipenv install`
- For RoBERTa training, ensure CUDA-compatible PyTorch is installed
- For temporal learner, `dgl` may need platform-specific installation. See [DGL installation guide](https://www.dgl.ai/pages/start.html).

### Path Errors
Some scripts use relative paths or hardcoded paths (`../Workspace/...`). You may need to adjust paths based on your local setup:
- Ensure `cti_w2v_v2` is copied into `sentence_to_technique_classifier/`
- Ensure `Roberta-CTI` is copied into `sentence_to_technique_classifier/`
- Ensure output directories exist before running scripts

### Missing Scripts
Some scripts referenced in older STEPS.md files (e.g., `prepareDiscourseDataset.py`, `compare_ttp_classifiers.py`) may not exist in this repository version. The core pipeline scripts listed above are confirmed present.

### Memory / Disk Issues
- Word2Vec training uses ~8 workers and can consume significant RAM
- RoBERTa training saves checkpoints frequently — ensure you have enough disk space
- The full pipeline produces large JSON files (some >50MB)

### OpenAI Fine-Tuning
- Requires `OPENAI_API_KEY` environment variable
- Optional — the spaCy models in `train_models.py` work independently
- Uses `skllm` (scikit-llm) for GPT integration

---

*For deeper architectural understanding, see `PROJECT_FLOW.md` in the repository root.*
