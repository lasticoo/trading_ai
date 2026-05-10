import requests
import pandas as pd

BASE_URL = "https://fapi.binance.com/fapi/v1/klines"

def fetch_klines(symbol, interval="15m", limit=300):
    params = {
        "symbol": symbol,
        "interval": interval,
        "limit": limit
    }
    r = requests.get(BASE_URL, params=params, timeout=10)
    r.raise_for_status()
    data = r.json()

    df = pd.DataFrame(data, columns=[
        "open_time","open","high","low","close","volume",
        "close_time","q","n","taker_base","taker_quote","ignore"
    ])

    df = df[["open_time","open","high","low","close","volume"]]
    df["open_time"] = pd.to_datetime(df["open_time"], unit="ms")
    df[["open","high","low","close","volume"]] = df[
        ["open","high","low","close","volume"]
    ].astype(float)

    return df
