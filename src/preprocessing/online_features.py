import numpy as np
import pandas as pd

def build_features(df: pd.DataFrame):
    df = df.copy()

    df["log_return"] = np.log(df["close"] / df["close"].shift(1))
    df["range"] = (df["high"] - df["low"]) / df["close"]
    df["close_position"] = (df["close"] - df["low"]) / (df["high"] - df["low"])
    df["volume_norm"] = df["volume"] / df["volume"].rolling(20).mean()

    df = df.replace([np.inf, -np.inf], np.nan).dropna()

    features = df[
        ["log_return", "range", "close_position", "volume_norm"]
    ].values

    return features
