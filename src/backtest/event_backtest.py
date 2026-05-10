import torch
import numpy as np
import pandas as pd
from pathlib import Path
from tqdm import tqdm

# ==================================================
# PATH CONFIG
# ==================================================
PROJECT_ROOT = Path(__file__).resolve().parents[2]

DATA_PATH = PROJECT_ROOT / "data" / "processed" / "training" / "train_dataset.pkl"
MODEL_PATH = PROJECT_ROOT / "models" / "tcn_trading_model.pt"

# ==================================================
# BACKTEST PARAMS
# ==================================================
RR = 2.0                 # Risk:Reward
EV_THRESHOLD = 0.2       # Minimum EV to take trade

DEVICE = "cuda" if torch.cuda.is_available() else "cpu"

# ==================================================
# MODEL (SAME AS TRAINING)
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
        return self.fc(self.net(x).squeeze(-1))


# ==================================================
# LOAD MODEL
# ==================================================
def load_model():
    model = TCN().to(DEVICE)
    model.load_state_dict(torch.load(MODEL_PATH, map_location=DEVICE))
    model.eval()
    return model


# ==================================================
# BACKTEST ENGINE
# ==================================================
def run_backtest():
    print("[INFO] Loading dataset...")
    df = pd.read_pickle(DATA_PATH)
    print(f"[INFO] Total samples: {len(df)}")

    model = load_model()

    equity = 0.0
    peak_equity = 0.0
    max_drawdown = 0.0

    trade_results = []

    print("[INFO] Running backtest...")

    for _, row in tqdm(df.iterrows(), total=len(df)):
        # ===== model inference =====
        X = torch.tensor(row["X"], dtype=torch.float32) \
                .permute(1, 0).unsqueeze(0).to(DEVICE)

        with torch.no_grad():
            probs = torch.sigmoid(model(X)).cpu().numpy()[0]

        # ===== unpack probabilities =====
        long_tp, long_sl, long_none = probs[:3]
        short_tp, short_sl, short_none = probs[3:]

        # ===== expected value =====
        ev_long = long_tp * RR - long_sl
        ev_short = short_tp * RR - short_sl

        # ===== decision =====
        if max(ev_long, ev_short) < EV_THRESHOLD:
            continue

        if ev_long > ev_short:
            side = "LONG"
            label = row["y"][:3]    # LONG label
        else:
            side = "SHORT"
            label = row["y"][3:]    # SHORT label

        # ===== realized R =====
        if label[0] == 1:       # TP_first
            r = RR
        elif label[1] == 1:     # SL_first
            r = -1
        else:                   # NONE
            r = 0

        equity += r
        peak_equity = max(peak_equity, equity)
        max_drawdown = min(max_drawdown, equity - peak_equity)

        trade_results.append(r)

    # ===== results =====
    trade_results = np.array(trade_results)

    print("\n====== BACKTEST RESULT ======")
    print(f"Total Trades       : {len(trade_results)}")
    print(f"Winrate            : {(trade_results > 0).mean():.2%}")
    print(f"Average R / trade  : {trade_results.mean():.3f}")
    print(f"Total R            : {trade_results.sum():.2f}")
    print(f"Max Drawdown (R)   : {max_drawdown:.2f}")

    if trade_results.mean() > 0:
        print("✅ Model has POSITIVE expectancy")
    else:
        print("❌ Model expectancy NEGATIVE")


# ==================================================
# MAIN
# ==================================================
if __name__ == "__main__":
    run_backtest()
