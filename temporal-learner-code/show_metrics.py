import json
import statistics
import pandas as pd

print("=== GRAPH NEURAL NETWORK (GNN) METRICS ===")
with open('cross_validation/cross_validation_95_RGCN_without_ohe.json', 'r') as f:
    data = json.load(f)

# Find the entry with all feature sets
final_model = [d for d in data if len(d['feature_set']) == 6][0]

print(f"Features Used: {final_model['feature_set']}")
print(f"Macro Precision (Average over 5 folds): {statistics.mean(final_model['precision_macro']):.4f}")
print(f"Macro Recall (Average over 5 folds): {statistics.mean(final_model['recall_macro']):.4f}")
print(f"Macro F1-Score (Average over 5 folds): {statistics.mean(final_model['f1_macro']):.4f}")
print("==========================================")
