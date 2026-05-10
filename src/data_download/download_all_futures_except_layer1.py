import requests
import pandas as pd
import time
from pathlib import Path
from tqdm import tqdm

# =========================
# BINANCE FUTURES ENDPOINTS
# =========================
BASE_URL = "https://fapi.binance.com"
KLINES_ENDPOINT = "/fapi/v1/klines"
EXCHANGE_INFO_ENDPOINT = "/fapi/v1/exchangeInfo"

# =========================
# TIMEFRAMES
# =========================
TIMEFRAMES = {
    "5m": "klines_5m",
    "15m": "klines_15m",
    "1h": "klines_1h"
}

# =========================
# SYMBOL EXCLUSION LIST
# =========================
EXCLUDED_SYMBOLS = {
    "BTCUSDT", "ETHUSDT",
    "SOLUSDT", "BNBUSDT", "AVAXUSDT", "ADAUSDT",
    "DOTUSDT", "ATOMUSDT", "NEARUSDT", "APTUSDT",
    "SUIUSDT", "ALGOUSDT", "FTMUSDT", "ICPUSDT",
    "XTZUSDT"
}

# =========================
# DOWNLOAD SETTINGS
# =========================
START_DATE = "2024-01-01"
END_DATE   = "2024-07-01"
LIMIT = 1500
SLEEP = 0.2


# =========================
# GET ALL FUTURES SYMBOLS
# =========================
def get_all_usdt_perpetual_symbols():
    url = BASE_URL + EXCHANGE_INFO_ENDPOINT
    r = requests.get(url)

    if r.status_code != 200:
        raise RuntimeError(f"ExchangeInfo error: {r.text}")

    data = r.json()

    symbols = []
    for s in data["symbols"]:
        if (
            s["contractType"] == "PERPETUAL"
            and s["quoteAsset"] == "USDT"
            and s["status"] == "TRADING"
        ):
            symbols.append(s["symbol"])

    return symbols


# =========================
# DOWNLOAD KLINES
# =========================
def download_klines(symbol, interval, start_ts, end_ts, save_path):
    all_data = []
    ts = start_ts

    while ts < end_ts:
        params = {
            "symbol": symbol,
            "interval": interval,
            "startTime": ts,
            "limit": LIMIT
        }

        r = requests.get(BASE_URL + KLINES_ENDPOINT, params=params)

        if r.status_code != 200:
            raise RuntimeError(f"HTTP {r.status_code}: {r.text}")

        data = r.json()

        if isinstance(data, dict):
            raise RuntimeError(f"Binance API error: {data}")

        if len(data) == 0:
            break

        all_data.extend(data)
        ts = data[-1][0] + 1
        time.sleep(SLEEP)

    if not all_data:
        return 0

    df = pd.DataFrame(all_data, columns=[
        "open_time", "open", "high", "low", "close", "volume",
        "close_time", "quote_volume", "trades",
        "taker_buy_base", "taker_buy_quote", "ignore"
    ])

    df = df[["open_time", "open", "high", "low", "close", "volume"]]
    df["open_time"] = pd.to_datetime(df["open_time"], unit="ms")
    df[["open", "high", "low", "close", "volume"]] = df[
        ["open", "high", "low", "close", "volume"]
    ].astype(float)

    save_path.parent.mkdir(parents=True, exist_ok=True)
    df.to_parquet(save_path, index=False)

    return len(df)


# =========================
# MAIN
# =========================
def main():
    print("🔍 Fetching all Binance Futures USDT-M symbols...")
    all_symbols = get_all_usdt_perpetual_symbols()

    target_symbols = [
        s for s in all_symbols if s not in EXCLUDED_SYMBOLS
    ]

    print(f"📊 Total symbols found      : {len(all_symbols)}")
    print(f"🚫 Excluded symbols         : {len(EXCLUDED_SYMBOLS)}")
    print(f"✅ Symbols to be downloaded : {len(target_symbols)}")

    start_ts = pd.Timestamp(START_DATE).value // 10**6
    end_ts = pd.Timestamp(END_DATE).value // 10**6

    for interval, folder in TIMEFRAMES.items():
        print(f"\n📥 Downloading timeframe: {interval}")

        for symbol in tqdm(target_symbols):
            save_path = Path(f"data/raw/{folder}/{symbol}.parquet")

            if save_path.exists():
                continue  # skip if already downloaded

            try:
                rows = download_klines(
                    symbol,
                    interval,
                    start_ts,
                    end_ts,
                    save_path
                )
                print(f"✅ {symbol} | {interval} | {rows} rows")
            except Exception as e:
                print(f"❌ {symbol} | {interval} | ERROR: {e}")


if __name__ == "__main__":
    main()
