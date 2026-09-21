"""ARIMA fitting and forecasting primitives."""

from __future__ import annotations

from typing import Any

import pandas as pd
from pmdarima import auto_arima
from statsmodels.tsa.arima.model import ARIMA


def fit_auto(series: pd.Series) -> Any:
    """Fit Auto ARIMA with the notebook's exact search configuration."""

    return auto_arima(
        series,
        start_p=0,
        start_q=0,
        max_p=5,
        max_q=5,
        max_d=2,
        seasonal=False,
        stepwise=True,
        information_criterion="aic",
        suppress_warnings=True,
        error_action="ignore",
        trace=True,
    )


def fit(series: pd.Series, order: tuple[int, int, int]) -> Any:
    """Fit a statsmodels ARIMA with the notebook's default fit behavior."""

    return ARIMA(series, order=order).fit()


def forecast(
    model: Any,
    horizon: int,
    *,
    index: pd.Index | None = None,
    clip_negative: bool = True,
) -> pd.Series:
    """Forecast an ARIMA model and optionally apply the notebook's clipping."""

    if hasattr(model, "forecast"):
        prediction = model.forecast(steps=horizon)
    else:
        prediction = model.predict(n_periods=horizon)
    result = pd.Series(prediction, index=index)
    return result.clip(lower=0) if clip_negative else result
