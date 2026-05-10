import numpy as np
import pandas as pd
from pathlib import Path
from tqdm import tqdm
import pickle

# ==================================================
# PATH CONFIG
# ==================================================
PROJECT_ROOT = Path(__file__).resolve().parents[2]

LABELED_BASE = PROJECT_ROOT / "data" / "processed" / "labeled"
OUT_BASE = PROJECT_ROOT / "data" / "processed" / "training"

OUT_BASE.mkdir(parents=True, exist_ok=True)

# ==================================================
# LABEL ENCODING
# ==================================================
LABEL_MAP = {
    "TP_first": [1, 0, 0],
    "SL_first": [0, 1, 0],
    "NONE":     [0, 0, 1]
}

# ==================================================
# SAFE LOAD PICKLE
# ==================================================
def safe_load_pickle(path: Path):
    try:
        with open(path, "rb") as f:
            return pickle.load(f)
    except Exception as e:
        print(f"[SKIP] Corrupted file: {path.name} | {e}")
        return None


# ==================================================
# BUILD DATASET
# ==================================================
def build_dataset():
    rows = []

    files = list(LABELED_BASE.glob("*.pkl"))
    print(f"[INFO] Found {len(files)} labeled symbol files")

    skipped = 0

    for file in tqdm(files, desc="Building dataset"):
        data = safe_load_pickle(file)
        if data is None:
            skipped += 1
            continue

        for row in data:
            X = row["market_state"].astype("float32")

            y_long = LABEL_MAP[row["long_label"]]
            y_short = LABEL_MAP[row["short_label"]]
            y = np.array(y_long + y_short, dtype="float32")

            rows.append({
                "X": X,
                "y": y
            })

    df = pd.DataFrame(rows)

    out_path = OUT_BASE / "train_dataset.pkl"
    df.to_pickle(out_path)

    print("\n✅ DATASET BUILD COMPLETE")
    print(f"📊 Total samples  : {len(df)}")
    print(f"⚠️ Skipped files  : {skipped}")
    print(f"💾 Saved to       : {out_path}")


if __name__ == "__main__":
    build_dataset()
