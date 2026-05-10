import pandas as pd

df = pd.read_parquet("data/raw/klines_15m/SOLUSDT.parquet")
print(df.head())
print(df.tail())
print(df.shape)
