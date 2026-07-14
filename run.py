import pandas as pd

df = pd.read_csv("2026-07-14T07-31_export.csv")

print(df.columns.tolist())
print(df.head())