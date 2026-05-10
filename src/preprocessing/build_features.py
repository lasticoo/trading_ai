import pandas as pd
import numpy as np
from pathlib import Path
from tqdm import tqdm

# ==================================================
# ABSOLUTE PATH BASED ON PROJECT ROOT
# ==================================================
PROJECT_ROOT = Path(__file__).resolve().parents[2]

RAW_BASE = PROJECT_ROOT / "src" / "data_download" / "data" / "raw"
OUT_BASE = PROJECT_ROOT / "data" / "processed" / "features"

# =========================
# FEATURE ENGINEERING
# =========================
def build_features(df: pd.DataFrame) -> pd.DataFrame:
    df = df.sort_values("open_time").reset_index(drop=True)

    df["log_return"] = np.log(df["close"] / df["close"].shift(1))
    df["range"] = (df["high"] - df["low"]) / df["close"]
    df["close_position"] = (df["close"] - df["low"]) / (df["high"] - df["low"])
    df["volume_norm"] = df["volume"] / df["volume"].rolling(20).mean()

    df = df.replace([np.inf, -np.inf], np.nan)
    df = df.dropna().reset_index(drop=True)

    return df


def process_timeframe(tf: str):
    input_dir = RAW_BASE / f"klines_{tf}"
    output_dir = OUT_BASE / tf
    output_dir.mkdir(parents=True, exist_ok=True)

    if not input_dir.exists():
        raise FileNotFoundError(f"Input directory not found: {input_dir}")

    files = list(input_dir.glob("*.parquet"))

    print(f"[INFO] {tf}: found {len(files)} parquet files")

    for file in tqdm(files, desc=f"Feature Engineering {tf}"):
        df = pd.read_parquet(file)
        df_feat = build_features(df)
        df_feat.to_parquet(output_dir / file.name, index=False)


if __name__ == "__main__":
    for tf in ["5m", "15m", "1h"]:
        process_timeframe(tf)
