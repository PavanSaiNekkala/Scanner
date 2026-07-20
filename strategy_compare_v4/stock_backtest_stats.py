from pathlib import Path

import numpy as np
import pandas as pd

ROOT = Path("/workspaces/Scanner/strategy_compare_v3")

# Every backtest_* directory
backtest_dirs = sorted(ROOT.glob("backtest_*"))

for folder in backtest_dirs:
    print(f"\nProcessing {folder.name}")

    csv_files = sorted(folder.glob("*.csv"))

    if not csv_files:
        continue

    output_excel = folder / f"{folder.name}_Statistics.xlsx"

    with pd.ExcelWriter(output_excel, engine="openpyxl") as writer:
        for csv in csv_files:
            print(f"   {csv.name}")

            df = pd.read_csv(csv)

            numeric = df.select_dtypes(include=np.number)

            if numeric.empty:
                continue

            stats = pd.DataFrame(index=numeric.columns)

            stats["Count"] = numeric.count()
            stats["Missing"] = numeric.isna().sum()
            stats["Sum"] = numeric.sum()
            stats["Mean"] = numeric.mean()
            stats["Median"] = numeric.median()
            stats["Mode"] = numeric.mode().iloc[0]
            stats["Variance"] = numeric.var()
            stats["Std Dev"] = numeric.std()
            stats["Min"] = numeric.min()
            stats["25%"] = numeric.quantile(0.25)
            stats["50%"] = numeric.quantile(0.50)
            stats["75%"] = numeric.quantile(0.75)
            stats["Max"] = numeric.max()
            stats["Range"] = stats["Max"] - stats["Min"]
            stats["IQR"] = stats["75%"] - stats["25%"]
            stats["Skewness"] = numeric.skew()
            stats["Kurtosis"] = numeric.kurt()
            stats["CV %"] = np.where(
                stats["Mean"] != 0,
                stats["Std Dev"] / stats["Mean"] * 100,
                np.nan,
            )
            stats["Std Error"] = stats["Std Dev"] / np.sqrt(stats["Count"])

            stats["5%"] = numeric.quantile(0.05)
            stats["10%"] = numeric.quantile(0.10)
            stats["90%"] = numeric.quantile(0.90)
            stats["95%"] = numeric.quantile(0.95)
            stats["99%"] = numeric.quantile(0.99)

            stats = stats.round(4)

            # Sheet name = Stock name
            sheet = csv.stem.replace("_backtest_", "_")

            # Excel limit = 31 chars
            sheet = sheet[:31]

            stats.to_excel(writer, sheet_name=sheet)

    print(f"Saved -> {output_excel}")

print("\nAll folders completed.")
