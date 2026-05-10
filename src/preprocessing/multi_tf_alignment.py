import pandas as pd
import numpy as np
from pathlib import Path
from tqdm import tqdm

# ==================================================
# PATH CONFIG (ABSOLUTE, ANTI ERROR)
# ==================================================
PROJECT_ROOT = Path(__file__).resolve().parents[2]

FEATURE_BASE = PROJECT_ROOT / "data" / "processed" / "features"
OUT_BASE = PROJECT_ROOT / "data" / "processed" / "aligned"

# ==================================================
# CONFIG
# ==================================================
WINDOWS = {
    "5m": 120,
    "15m": 96,
    "1h": 48
}

FEATURE_COLS = [
    "log_return",
    "range",
    "close_position",
    "volume_norm"
]


# ==================================================
# LOAD FEATURE DATA
# ==================================================
def load_features(symbol: str):
    dfs = {}
    for tf in ["5m", "15m", "1h"]:
        path = FEATURE_BASE / tf / f"{symbol}.parquet"
        if not path.exists():
            return None

        df = pd.read_parquet(path)
        df = df.sort_values("open_time").set_index("open_time")
        dfs[tf] = df

    return dfs


# ==================================================
# BUILD SINGLE MARKET STATE
# ==================================================
def build_market_state(dfs, timestamp):
    state_blocks = []

    for tf in ["1h", "15m", "5m"]:
        df = dfs[tf]
        window = WINDOWS[tf]

        past = df[df.index <= timestamp].tail(window)

        if len(past) < window:
            return None

        state_blocks.append(past[FEATURE_COLS].values)

    return np.concatenate(state_blocks, axis=0)


# ==================================================
# ALIGN ONE SYMBOL
# ==================================================
def align_symbol(symbol: str):
    dfs = load_features(symbol)
    if dfs is None:
        return

    base_df = dfs["15m"]
    aligned_rows = []

    for ts in base_df.index:
        market_state = build_market_state(dfs, ts)
        if market_state is None:
            continue

        aligned_rows.append({
            "symbol": symbol,
            "timestamp": ts,
            "market_state": market_state
        })

    OUT_BASE.mkdir(parents=True, exist_ok=True)
    pd.to_pickle(aligned_rows, OUT_BASE / f"{symbol}.pkl")


# ==================================================
# MAIN
# ==================================================
def main():
    symbols = [
        p.stem for p in (FEATURE_BASE / "15m").glob("*.parquet")
    ]

    print(f"[INFO] Aligning {len(symbols)} symbols")

    for symbol in tqdm(symbols, desc="Multi-TF Alignment"):
        align_symbol(symbol)


if __name__ == "__main__":
    main()
