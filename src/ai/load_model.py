import torch
from src.training.tcn_model import TCN

def load_trained_model(
    model_path: str,
    device: str = "cpu"
):
    model = TCN(in_channels=4, hidden=64)
    state = torch.load(model_path, map_location=device)
    model.load_state_dict(state)
    model.to(device)
    model.eval()
    return model
