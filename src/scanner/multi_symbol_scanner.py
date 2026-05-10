from src.live.binance_data import fetch_klines
from src.preprocessing.online_features import build_features

RR = 2.0
SEQ_LEN = 264
INTERVAL = "5m"

def scan_symbols(symbols, ai, top_n=10):
    results = []

    for symbol in symbols:
        try:
            df = fetch_klines(symbol, INTERVAL, limit=SEQ_LEN + 50)
            X = build_features(df)

            if len(X) < SEQ_LEN:
                continue

            X_seq = X[-SEQ_LEN:]
            price = df["close"].iloc[-1]

            probs = ai.predict(X_seq)

            ev_long = probs["long"]["tp"] * RR - probs["long"]["sl"]
            ev_short = probs["short"]["tp"] * RR - probs["short"]["sl"]

            side = "LONG" if ev_long >= ev_short else "SHORT"
            ev = max(ev_long, ev_short)

            results.append({
                "symbol": symbol,
                "price": float(price),
                "side": side,
                "ev": float(ev),
                "ai_probs": probs,
                "ohlcv_df": df        # 🔑 INI KUNCI SEMUANYA
            })


        except Exception as e:
            print(f"{symbol} error: {e}")

    # ranking saja, tidak filter
    results = sorted(results, key=lambda x: x["ev"], reverse=True)
    return results[:top_n]
