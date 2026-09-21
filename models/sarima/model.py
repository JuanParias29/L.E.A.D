"""SARIMA fitting and forecasting primitives."""

from __future__ import annotations

from typing import Any

import pandas as pd
from pmdarima import auto_arima


def fit_auto(series: pd.Series, seasonal_period: int) -> Any:
    """Fit SARIMA using the notebook's exact search bounds."""

    return auto_arima(
        series,
        start_p=0,
        start_q=0,
        max_p=2,
        max_q=2,
        max_d=2,
        seasonal=True,
        m=seasonal_period,
        start_P=0,
        start_Q=0,
        max_P=1,
        max_Q=1,
        max_D=1,
        information_criterion="aic",
        stepwise=True,
        suppress_warnings=True,
        error_action="ignore",
        trace=False,
    )


def forecast(
    model: Any,
    horizon: int,
    *,
    index: pd.Index | None = None,
    clip_negative: bool = True,
) -> pd.Series:
    """Forecast a SARIMA model using the notebook's output convention."""

    prediction = model.predict(n_periods=horizon)
    result = pd.Series(prediction, index=index)
    return result.clip(lower=0) if clip_negative else result
