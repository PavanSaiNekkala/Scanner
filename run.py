import pandas as pd
import glob

files = glob.glob(
    "strategy_compare_v4/output/*.csv"
)

for f in files:
    df = pd.read_csv(f)

    cols = [
        "Total Return %",
        "Annual Return %",
        "CAGR %",
        "Maximum Drawdown %",
    ]

    existing = [
        c for c in cols
        if c in df.columns
    ]

    if existing:
        print("\nFILE:", f)
        print(df[existing].describe())