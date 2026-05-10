import torch
import numpy as np
import pandas as pd
from pathlib import Path
from tqdm import tqdm

PROJECT_ROOT = Path(__file__).resolve().parents[2]
DATA_PATH = PROJECT_ROOT / "data" / "processed" / "training" / "train_dataset.pkl"
MODEL_PATH = PROJECT_ROOT / "models" / "tcn_trading_model.pt"

RR = 2.0
DEVICE = "cuda" if torch.cuda.is_available() else "cpu"

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

df = pd.read_pickle(DATA_PATH)

def run(threshold):
    equity = 0
    peak = 0
    dd = 0
    trades = []

    for _, row in df.iterrows():
        X = torch.tensor(row["X"], dtype=torch.float32)\
                .permute(1,0).unsqueeze(0).to(DEVICE)

        with torch.no_grad():
            probs = torch.sigmoid(model(X)).cpu().numpy()[0]

        long_tp, long_sl, _ = probs[:3]
        short_tp, short_sl, _ = probs[3:]

        ev_long = long_tp * RR - long_sl
        ev_short = short_tp * RR - short_sl

        if max(ev_long, ev_short) < threshold:
            continue

        if ev_long > ev_short:
            label = row["y"][:3]
        else:
            label = row["y"][3:]

        if label[0] == 1:
            r = RR
        elif label[1] == 1:
            r = -1
        else:
            r = 0

        equity += r
        peak = max(peak, equity)
        dd = min(dd, equity - peak)
        trades.append(r)

    if not trades:
        return None

    return {
        "threshold": threshold,
        "trades": len(trades),
        "avg_R": np.mean(trades),
        "max_dd": dd
    }

print("\n=== THRESHOLD SCAN ===")
for th in [0.2, 0.3, 0.4, 0.5, 0.6]:
    res = run(th)
    if res:
        print(res)
