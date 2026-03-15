# ============================================================
# model_training/dataset_loader.py
# ============================================================
import os, json
from datasets import Dataset

def load_cn_dataset():
    base_dir  = os.path.dirname(os.path.abspath(__file__))
    data_path = os.path.join(base_dir, "data", "cndataset.json")

    if not os.path.exists(data_path):
        raise FileNotFoundError(f"Dataset not found: {data_path}")

    with open(data_path, "r", encoding="utf-8") as f:
        raw = json.load(f)

    # Validate format
    valid = []
    for i, item in enumerate(raw):
        if "input" not in item or "output" not in item:
            print(f"[Loader] Skipping item {i} — missing input/output keys")
            continue
        output = item["output"]
        # Must have A) B) C) D) and Answer:
        if not all(f"{x})" in output for x in ["A", "B", "C", "D"]):
            print(f"[Loader] Skipping item {i} — missing options")
            continue
        if "Answer:" not in output:
            print(f"[Loader] Skipping item {i} — missing Answer:")
            continue
        valid.append(item)

    print(f"[Loader] Loaded {len(valid)}/{len(raw)} valid examples")
    return Dataset.from_list(valid)