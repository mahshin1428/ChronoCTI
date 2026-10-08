import subprocess
import os
import shutil

def purge():
    modelNames = ['w2vAll', 'lgAll', 'trfAll', 'robertaBaseAll', 'robertaCtiAll']
    path = os.path.abspath("bagging_models")
    dump_path = os.path.join(path, "dump")
    os.makedirs(dump_path, exist_ok=True)

    for i in range(0, 5):
        for model in modelNames:
            entry = f"{model}-{i}"
            entry_path = os.path.join(path, entry)
            if os.path.exists(entry_path):
                src_metrics = os.path.join(entry_path, "metrics.json")
                dst_metrics = os.path.join(dump_path, f"metrics-{model}-{i}.json")
                if os.path.exists(src_metrics):
                    shutil.copy2(src_metrics, dst_metrics)

                src_meta = os.path.join(entry_path, "model-best/meta.json")
                dst_meta = os.path.join(dump_path, f"meta-{model}-{i}.json")
                if os.path.exists(src_meta):
                    shutil.copy2(src_meta, dst_meta)

models_to_train = [
    ("lgAll", "config-lg.cfg"),
    ("w2vAll", "config-w2v.cfg"),
    ("trfAll", "config-trf.cfg"),
    ("robertaBaseAll", "config-roberta-base.cfg"),
    ("robertaCtiAll", "config-roberta-cti.cfg")
]

print("Starting 5-Fold Cross Validation Training for Sentence-to-Asset Classifier...")

for i in range(5):
    print(f"\n=================== FOLD {i} ===================")
    train_file = f"train_test_splits/train_assets_split_{i}.jsonl"
    test_file = f"train_test_splits/test_assets_split_{i}.jsonl"

    for model_name, cfg_file in models_to_train:
        cfg_path = os.path.join("configs", cfg_file)
        if not os.path.exists(cfg_path):
            print(f"Skipping {model_name}: {cfg_path} not found.")
            continue

        print(f"\n[Fold {i}] Training {model_name} with {cfg_file}...")
        result = subprocess.run([
            "spacy", "project", "run", "all", ".",
            "--vars.train", train_file,
            "--vars.dev", test_file,
            "--vars.output", f"{model_name}-{i}",
            "--vars.config", cfg_file
        ])
        print(f"Finished {model_name}-{i} with exit code {result.returncode}")
        purge()

print("\nAll models trained and metrics saved to bagging_models/dump/!")
