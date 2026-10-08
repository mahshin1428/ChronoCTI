import spacy
import json
import os

MODEL_PATH = "bagging_models/asset_classifier_model/model-best"
TEST_DATA = "assets/train_test_splits/test_assets_split_0.jsonl"
TAXONOMY_PATH = "selected_assetsWName.json"

if not os.path.exists(MODEL_PATH):
    print(f"Model path '{MODEL_PATH}' does not exist.")
    print("Please train the model first using: python train_single_model.py")
    exit(1)

print(f"Loading model from {MODEL_PATH}...")
nlp = spacy.load(MODEL_PATH)

with open(TAXONOMY_PATH) as f:
    taxonomy = json.load(f)
asset_ids = sorted([x["id"] for x in taxonomy])
asset_names = {x["id"]: x["name"] for x in taxonomy}

y_true = []
y_pred = []

with open(TEST_DATA, "r", encoding="utf-8") as f:
    for line in f:
        if not line.strip():
            continue
        item = json.loads(line)
        text = item["text"]
        actual_dict = item["cats"]
        
        doc = nlp(text)
        
        # Ground truth binary vector
        y_true_sample = [1 if actual_dict.get(aid, 0.0) == 1.0 else 0 for aid in asset_ids]
        
        # Predicted binary vector (threshold >= 0.5)
        y_pred_sample = [1 if doc.cats.get(aid, 0.0) >= 0.5 else 0 for aid in asset_ids]
        
        y_true.append(y_true_sample)
        y_pred.append(y_pred_sample)

try:
    from sklearn.metrics import classification_report
    target_names = [f"{aid} ({asset_names.get(aid, aid)})" for aid in asset_ids]
    report = classification_report(y_true, y_pred, target_names=target_names, zero_division=0)
    print("=" * 75)
    print("SENTENCE-TO-ASSET CLASSIFICATION EVALUATION REPORT")
    print("=" * 75)
    print(report)
except ImportError:
    print("=" * 75)
    print(f"Evaluated {len(y_true)} test samples successfully across {len(asset_ids)} asset classes.")
    print("Install scikit-learn (`pip install scikit-learn`) for formatted classification tables.")
    print("=" * 75)

