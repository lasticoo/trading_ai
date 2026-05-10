import pandas as pd
from pathlib import Path
from tqdm import tqdm

# ==================================================
# PATH CONFIG
# ==================================================
PROJECT_ROOT = Path(__file__).resolve().parents[2]

RAW_15M = PROJECT_ROOT / "src" / "data_download" / "data" / "raw" / "klines_15m"
ALIGNED_BASE = PROJECT_ROOT / "data" / "processed" / "aligned"
OUT_BASE = PROJECT_ROOT / "data" / "processed" / "labeled"

OUT_BASE.mkdir(parents=True, exist_ok=True)

# ==================================================
# LABEL PARAMETERS
# ==================================================
TP_PCT = 0.02
SL_PCT = 0.01
HORIZON_MIN = 90
BASE_TF_MIN = 15
HORIZON_BARS = HORIZON_MIN // BASE_TF_MIN


# ==================================================
# EVENT CHECKERS
# ==================================================
def label_long(entry, future):
    tp = entry * (1 + TP_PCT)
    sl = entry * (1 - SL_PCT)

    for _, r in future.iterrows():
        if r["low"] <= sl:
            return "SL_first"
        if r["high"] >= tp:
            return "TP_first"
    return "NONE"


def label_short(entry, future):
    tp = entry * (1 - TP_PCT)
    sl = entry * (1 + SL_PCT)

    for _, r in future.iterrows():
        if r["high"] >= sl:
            return "SL_first"
        if r["low"] <= tp:
            return "TP_first"
    return "NONE"


# ==================================================
# LABEL ONE SYMBOL (SAFE)
# ==================================================
def label_symbol(symbol):
    out_file = OUT_BASE / f"{symbol}.pkl"
    if out_file.exists():
        return  # ✅ SKIP ALREADY LABELED

    aligned_path = ALIGNED_BASE / f"{symbol}.pkl"
    raw_path = RAW_15M / f"{symbol}.parquet"

    if not aligned_path.exists() or not raw_path.exists():
        return

    aligned = pd.read_pickle(aligned_path)
    raw = pd.read_parquet(raw_path)
    raw = raw.sort_values("open_time").set_index("open_time")

    labeled = []

    for row in aligned:
        ts = row["timestamp"]
        if ts not in raw.index:
            continue

        entry = raw.loc[ts]["close"]
        future = raw.loc[ts:].iloc[1:HORIZON_BARS + 1]
        if len(future) < HORIZON_BARS:
            continue

        labeled.append({
            "symbol": symbol,
            "timestamp": ts,
            "market_state": row["market_state"],
            "long_label": label_long(entry, future),
            "short_label": label_short(entry, future)
        })

    # ✅ SAVE PER SYMBOL (CHECKPOINT)
    pd.to_pickle(labeled, out_file)


# ==================================================
# MAIN (RESUMABLE)
# ==================================================
def main():
    all_symbols = [p.stem for p in ALIGNED_BASE.glob("*.pkl")]
    done_symbols = {p.stem for p in OUT_BASE.glob("*.pkl")}

    remaining = [s for s in all_symbols if s not in done_symbols]

    print(f"[INFO] Total symbols     : {len(all_symbols)}")
    print(f"[INFO] Already labeled  : {len(done_symbols)}")
    print(f"[INFO] Remaining        : {len(remaining)}")

    for s in tqdm(remaining, desc="Labeling (resume-safe)"):
        label_symbol(s)


if __name__ == "__main__":
    main()
