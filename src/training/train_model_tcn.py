import numpy as np
import pandas as pd
from pathlib import Path
from sklearn.model_selection import train_test_split
import torch
import torch.nn as nn
from torch.utils.data import Dataset, DataLoader

# ==================================================
# PATH CONFIG
# ==================================================
PROJECT_ROOT = Path(__file__).resolve().parents[2]
DATA_PATH = PROJECT_ROOT / "data" / "processed" / "training" / "train_dataset.pkl"
MODEL_DIR = PROJECT_ROOT / "models"
MODEL_DIR.mkdir(exist_ok=True)

DEVICE = "cuda" if torch.cuda.is_available() else "cpu"

# ==================================================
# DATASET
# ==================================================
class TradingDataset(Dataset):
    def __init__(self, df):
        self.X = df["X"].values
        self.y = df["y"].values

    def __len__(self):
        return len(self.X)

    def __getitem__(self, idx):
        X = torch.tensor(self.X[idx]).permute(1, 0)  # (features, seq)
        y = torch.tensor(self.y[idx])
        return X, y


# ==================================================
# MODEL
# ==================================================
class TCN(nn.Module):
    def __init__(self, in_channels=4, hidden=64):
        super().__init__()
        self.net = nn.Sequential(
            nn.Conv1d(in_channels, hidden, kernel_size=3, padding=1),
            nn.ReLU(),
            nn.Conv1d(hidden, hidden, kernel_size=3, padding=1),
            nn.ReLU(),
            nn.AdaptiveAvgPool1d(1)
        )
        self.fc = nn.Linear(hidden, 6)

    def forward(self, x):
        x = self.net(x)
        x = x.squeeze(-1)
        return self.fc(x)


# ==================================================
# TRAINING LOOP
# ==================================================
def train():
    df = pd.read_pickle(DATA_PATH)

    train_df, val_df = train_test_split(
        df, test_size=0.2, random_state=42, shuffle=True
    )

    train_ds = TradingDataset(train_df)
    val_ds = TradingDataset(val_df)

    train_dl = DataLoader(train_ds, batch_size=64, shuffle=True)
    val_dl = DataLoader(val_ds, batch_size=64)

    model = TCN().to(DEVICE)
    optimizer = torch.optim.Adam(model.parameters(), lr=1e-3)
    criterion = nn.BCEWithLogitsLoss()

    for epoch in range(10):
        model.train()
        total_loss = 0

        for X, y in train_dl:
            X, y = X.to(DEVICE), y.to(DEVICE)

            optimizer.zero_grad()
            logits = model(X)
            loss = criterion(logits, y)
            loss.backward()
            optimizer.step()

            total_loss += loss.item()

        avg_loss = total_loss / len(train_dl)
        print(f"Epoch {epoch+1} | Train Loss: {avg_loss:.4f}")

    torch.save(model.state_dict(), MODEL_DIR / "tcn_trading_model.pt")
    print("✅ Model saved")


if __name__ == "__main__":
    train()
