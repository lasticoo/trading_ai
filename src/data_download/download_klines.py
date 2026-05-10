import requests
import pandas as pd
import time
from pathlib import Path
from tqdm import tqdm

BASE_URL = "https://fapi.binance.com/fapi/v1/klines"

def download_klines(symbol, interval, start_ts, end_ts, save_path):
    all_data = []
    limit = 1500
    ts = start_ts

    while ts < end_ts:
        params = {
            "symbol": symbol,
            "interval": interval,
            "startTime": ts,
            "limit": limit
        }
        r = requests.get(BASE_URL, params=params)
        data = r.json()

        if not data:
            break

        all_data.extend(data)
        ts = data[-1][0] + 1
        time.sleep(0.2)  # anti rate limit

    df = pd.DataFrame(all_data, columns=[
        "open_time", "open", "high", "low", "close", "volume",
        "close_time", "quote_volume", "trades",
        "taker_buy_base", "taker_buy_quote", "ignore"
    ])

    df = df[["open_time", "open", "high", "low", "close", "volume"]]
    df["open_time"] = pd.to_datetime(df["open_time"], unit="ms")
    df = df.astype({
        "open": float,
        "high": float,
        "low": float,
        "close": float,
        "volume": float
    })

    save_path.parent.mkdir(parents=True, exist_ok=True)
    df.to_parquet(save_path, index=False)

    return df

if __name__ == "__main__":
    symbol = "ETHUSDT"
    interval = "15m"

    start = pd.Timestamp("2024-01-01").value // 10**6
    end = pd.Timestamp("2024-07-01").value // 10**6

    save_path = Path(f"data/raw/klines_15m/{symbol}.parquet")

    download_klines(symbol, interval, start, end, save_path)
