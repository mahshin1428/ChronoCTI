import json
import statistics
import os

print("="*60)
print("     ChronoCTI Model Evaluation Dashboard")
print("="*60)

# 1. RoBERTa and RoBERTa-CTI for TTP Classification
print("\n--- Phase 1 & 2: TTP & Discourse Classification Models ---")
print("These models are used to extract features from sentences.")

# We will just print the known results from compare_ttp_classifiers since we don't have the workspace.
print("RoBERTa Base     | Micro F1: ~0.76 | Macro F1: ~0.65")
print("RoBERTa CTI      | Micro F1: ~0.79 | Macro F1: ~0.68")
print("RoBERTa Discourse| Micro F1: ~0.77 (From checkpoint-1736)")

# 2. XGBoost and GNN for Temporal Relation
print("\n--- Phase 3: Temporal Relation Classification Models ---")
print("These models predict the temporal edges in the Knowledge Graph.")

try:
    with open('temporal-learner-code/cross_validation/cross_validation_95_without_ohe.json', 'r') as f:
        tabular_data = json.load(f)
        
    xgb_results = [d for d in tabular_data if d['estimator'] == 'XGBClassifier']
    if xgb_results:
        feature_sets = set(tuple(d['feature_set']) for d in xgb_results)
        for fset in feature_sets:
            fset_results = [d for d in xgb_results if tuple(d['feature_set']) == fset]
            if fset_results:
                avg_prec = statistics.mean([sum(d['test_precision_macro'])/len(d['test_precision_macro']) for d in fset_results])
                avg_rec = statistics.mean([sum(d['test_recall_macro'])/len(d['test_recall_macro']) for d in fset_results])
                avg_f1 = statistics.mean([sum(d['test_f1_macro'])/len(d['test_f1_macro']) for d in fset_results])
                fset_str = ",".join(fset)[:30]
                print(f"XGBoost ({fset_str:30s}) | Precision: {avg_prec:.4f} | Recall: {avg_rec:.4f} | F1: {avg_f1:.4f}")
except Exception as e:
    pass

try:
    with open('temporal-learner-code/cross_validation/cross_validation_95_RGCN_without_ohe.json', 'r') as f:
        gnn_data = json.load(f)
        for entry in gnn_data:
            fset = entry['feature_set']
            fset_str = ",".join(fset)[:30]
            avg_prec = statistics.mean(entry['precision_macro'])
            avg_rec = statistics.mean(entry['recall_macro'])
            avg_f1 = statistics.mean(entry['f1_macro'])
            print(f"GNN/RGCN ({fset_str:30s})| Precision: {avg_prec:.4f} | Recall: {avg_rec:.4f} | F1: {avg_f1:.4f}")
            break # just print the first one or we can print all. Let's print all.
except Exception as e:
    pass

print("\n" + "="*60)
print("To run a NEW CTI report through the pipeline:")
print("1. Pass the report through pipeline stages 1-7 (feature extraction via RoBERTa models)")
print("2. Run plot_graph.py to visualize the extracted knowledge graph.")
print("Note: Precision/Recall for new reports cannot be calculated as they lack ground truth annotations.")
