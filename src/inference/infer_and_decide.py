import torch
import numpy as np
import pandas as pd
from pathlib import Path

# ==================================================
# PATH CONFIG
# ==================================================
PROJECT_ROOT = Path(__file__).resolve().parents[2]

MODEL_PATH = PROJECT_ROOT / "models" / "tcn_trading_model.pt"
SAMPLE_DATA = PROJECT_ROOT / "data" / "processed" / "training" / "train_dataset.pkl"

DEVICE = "cuda" if torch.cuda.is_available() else "cpu"
RR = 2.0
EV_THRESHOLD = 0.2

# ==================================================
# MODEL
# ==================================================
class TCN(torch.nn.Module):
    def __init__(self, in_channels=4, hidden=64):
        super().__init__()
        self.net = torch.nn.Sequential(
            torch.nn.Conv1d(in_channels, hidden, 3, padding=1),
            torch.nn.ReLU(),
            torch.nn.Conv1d(hidden, hidden, 3, padding=1),
            torch.nn.ReLU(),
            torch.nn.AdaptiveAvgPool1d(1)
        )
        self.fc = torch.nn.Linear(hidden, 6)

    def forward(self, x):
        x = self.net(x)
        return self.fc(x.squeeze(-1))


# ==================================================
# INFERENCE
# ==================================================
def infer_one():
    df = pd.read_pickle(SAMPLE_DATA)
    row = df.sample(1).iloc[0]

    X = torch.tensor(row["X"]).permute(1, 0).unsqueeze(0).to(DEVICE)

    model = TCN().to(DEVICE)
    model.load_state_dict(torch.load(MODEL_PATH, map_location=DEVICE))
    model.eval()

    with torch.no_grad():
        logits = model(X)
        probs = torch.sigmoid(logits).cpu().numpy()[0]

    long_tp, long_sl, long_none = probs[:3]
    short_tp, short_sl, short_none = probs[3:]

    ev_long = long_tp * RR - long_sl
    ev_short = short_tp * RR - short_sl

    if max(ev_long, ev_short) < EV_THRESHOLD:
        decision = "NO TRADE"
    elif ev_long > ev_short:
        decision = "LONG"
    else:
        decision = "SHORT"

    print("=== MODEL OUTPUT ===")
    print(f"LONG  TP:{long_tp:.2f} SL:{long_sl:.2f} NONE:{long_none:.2f}")
    print(f"SHORT TP:{short_tp:.2f} SL:{short_sl:.2f} NONE:{short_none:.2f}")
    print(f"EV_LONG : {ev_long:.2f}")
    print(f"EV_SHORT: {ev_short:.2f}")
    print(f"👉 DECISION: {decision}")


if __name__ == "__main__":
    infer_one()
