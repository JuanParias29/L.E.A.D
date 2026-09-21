"""Time-based train/test splitting used by the forecasting notebook."""

from __future__ import annotations

import pandas as pd


def split_last_months(
    series: pd.Series,
    *,
    months: int = 6,
) -> tuple[pd.Series, pd.Series, pd.Timestamp]:
    """Split a sorted series at its last ``months`` months."""

    data = series.sort_index()
    cutoff = data.index.max() - pd.DateOffset(months=months)
    train = data.loc[data.index <= cutoff]
    test = data.loc[data.index > cutoff]
    return train, test, cutoff
