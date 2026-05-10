import websocket
import json
import numpy as np
import torch
from pathlib import Path
from datetime import datetime

# =========================
# CONFIG
# =========================
SYMBOL = "btcusdt"
INTERVAL = "15m"
RR = 2.0
EV_THRESHOLD = 0.30

PROJECT_ROOT = Path(__file__).resolve().parents[2]
MODEL_PATH = PROJECT_ROOT / "models" / "tcn_trading_model.pt"

DEVICE = "cuda" if torch.cuda.is_available() else "cpu"

# =========================
# MODEL
# =========================
class TCN(torch.nn.Module):
    def __init__(self):
        super().__init__()
        self.net = torch.nn.Sequential(
            torch.nn.Conv1d(4, 64, 3, padding=1),
            torch.nn.ReLU(),
            torch.nn.Conv1d(64, 64, 3, padding=1),
            torch.nn.ReLU(),
            torch.nn.AdaptiveAvgPool1d(1)
        )
        self.fc = torch.nn.Linear(64, 6)

    def forward(self, x):
        return self.fc(self.net(x).squeeze(-1))

model = TCN().to(DEVICE)
model.load_state_dict(torch.load(MODEL_PATH, map_location=DEVICE))
model.eval()

# =========================
# BUFFER
# =========================
buffer = []

# =========================
# FEATURE FUNCTION
# =========================
def build_features(arr):
    close = arr[:,0]
    high = arr[:,1]
    low = arr[:,2]
    volume = arr[:,3]

    log_return = np.diff(np.log(close), prepend=0)
    range_ = (high - low) / close
    close_pos = (close - low) / (high - low + 1e-6)
    vol_norm = volume / (np.mean(volume) + 1e-6)

    return np.stack([log_return, range_, close_pos, vol_norm], axis=1)

# =========================
# WS CALLBACK
# =========================
def on_message(ws, message):
    global buffer
    data = json.loads(message)
    k = data["k"]

    if not k["x"]:
        return  # candle not closed

    close = float(k["c"])
    high = float(k["h"])
    low = float(k["l"])
    volume = float(k["v"])

    buffer.append([close, high, low, volume])
    if len(buffer) > 300:
        buffer.pop(0)

    if len(buffer) < 264:
        print("⏳ Collecting data...", len(buffer))
        return

    arr = np.array(buffer[-264:])
    X = build_features(arr)

    X = torch.tensor(X, dtype=torch.float32)\
             .permute(1,0)\
             .unsqueeze(0)\
             .to(DEVICE)

    with torch.no_grad():
        probs = torch.sigmoid(model(X)).cpu().numpy()[0]

    long_tp, long_sl, _ = probs[:3]
    short_tp, short_sl, _ = probs[3:]

    ev_long = long_tp * RR - long_sl
    ev_short = short_tp * RR - short_sl

    if max(ev_long, ev_short) < EV_THRESHOLD:
        decision = "NO TRADE"
    elif ev_long > ev_short:
        decision = "LONG"
    else:
        decision = "SHORT"

    print(f"[{datetime.utcnow()}] "
          f"EV_LONG={ev_long:.2f} EV_SHORT={ev_short:.2f} → {decision}")

# =========================
# START WS
# =========================
ws = websocket.WebSocketApp(
    f"wss://fstream.binance.com/ws/{SYMBOL}@kline_{INTERVAL}",
    on_message=on_message
)

print("🚀 Paper trading LIVE started...")
ws.run_forever()
