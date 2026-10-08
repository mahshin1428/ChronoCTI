import subprocess
import os

print("Training a single RoBERTa-CTI model to replace the missing classifier...")

# Run spaCy project to train the model on split_0 and output to bagging_models/robertaCtiAll-final
result = subprocess.run([
    'spacy', 'project', 'run', 'all', '.', 
    "--vars.train", "train_test_splits/train_selected120_split_0.jsonl", 
    "--vars.dev", "train_test_splits/test_selected120_split_0.jsonl", 
    "--vars.output", "robertaCtiAll-final", 
    "--vars.config", "config-roberta-cti.cfg"
])

print("Training finished. Output:", result.returncode)
