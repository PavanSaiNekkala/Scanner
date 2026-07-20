import numpy as np
import pandas as pd


def safe_numeric(series):
    return pd.to_numeric(series, errors="coerce")


def coefficient_of_variation(series):
    series = series.dropna()

    if len(series) == 0:
        return np.nan

    mean = series.mean()

    if mean == 0:
        return np.nan

    return (series.std() / mean) * 100


def normalize(series):
    minimum = series.min()

    maximum = series.max()

    if maximum == minimum:
        return pd.Series(np.ones(len(series)) * 50, index=series.index)

    return ((series - minimum) / (maximum - minimum)) * 100
