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
TP_PCT = 0.02       # 2%
SL_PCT = 0.01       # 1%
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
# LABEL ONE SYMBOL
# ==================================================
def label_symbol(symbol):
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

    pd.to_pickle(labeled, OUT_BASE / f"{symbol}.pkl")


# ==================================================
# MAIN
# ==================================================
def main():
    symbols = [p.stem for p in ALIGNED_BASE.glob("*.pkl")]
    print(f"[INFO] Labeling LONG & SHORT for {len(symbols)} symbols")

    for s in tqdm(symbols, desc="Labeling LONG+SHORT"):
        label_symbol(s)


if __name__ == "__main__":
    main()
