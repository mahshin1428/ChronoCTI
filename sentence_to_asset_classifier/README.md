# Sentence to Asset Classifier

This subproject handles multi-label text classification to map threat intelligence sentences to target **Asset IDs** (`A0001` to `A0018`).

---

## 📁 Directory Structure
```
sentence_to_asset_classifier/
├── assets/
│   ├── train_test_splits/         # 5-fold cross-validation splits (train/test_assets_split_0..4.jsonl)
│   ├── train_test_prompt_splits/  # Formatted for OpenAI API fine-tuning
│   └── train_test_response_splits/# Prediction response outputs
├── configs/                       # spaCy pipeline configurations (config-lg.cfg, etc.)
├── corpus/                        # Binary spaCy DocBin datasets (.spacy)
├── openai/
│   └── fine_tune.py               # OpenAI fine-tuning and evaluation script
├── scripts/
│   ├── convert.py                 # JSONL to .spacy format converter
│   └── visualize_model.py         # Model prediction visualizer
├── selected_assetsWName.json      # Complete asset taxonomy (A0001 - A0018)
├── project.yml                    # spaCy project workflow runner
├── train_single_model.py          # Train a single spaCy model
├── train_models.py                # Run full 5-fold bagging cross validation
└── evaluate_models.py             # Evaluate and output Classification Report
```

---

## 🚀 How to Run and Train the Models

### 1. Train a Single Model (Quick Start)
```bash
python train_single_model.py
```
This trains an `en_core_web_lg` based text classifier on `split_0` and saves the best model to `bagging_models/asset_classifier_model/model-best`.

### 2. Evaluate the Trained Model
```bash
python evaluate_models.py
```
This evaluates the trained model on the test split and displays precision, recall, and F1-score across all 18 asset classes.

### 3. Run Full 5-Fold Cross Validation Bagging
```bash
python train_models.py
```
This executes 5-fold cross-validation across multiple spaCy architectures (`lgAll`, `w2vAll`, `trfAll`, `robertaBaseAll`, `robertaCtiAll`) and saves benchmark metrics into `bagging_models/dump/`.

### 4. Fine-Tune OpenAI GPT-3.5
```bash
cd openai
python fine_tune.py
```
