import subprocess
import os

print("Training a single spaCy model (en_core_web_lg) on split_0 for Sentence-to-Asset Classifier...")

result = subprocess.run([
    'spacy', 'project', 'run', 'all', '.',
    "--vars.train", "train_test_splits/train_assets_split_0.jsonl",
    "--vars.dev", "train_test_splits/test_assets_split_0.jsonl",
    "--vars.output", "asset_classifier_model",
    "--vars.config", "config-lg.cfg"
])

print("Training finished with return code:", result.returncode)
print("Trained model saved at: bagging_models/asset_classifier_model/model-best")
