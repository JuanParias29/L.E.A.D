"""SARIMAX fitting, forecasting and interval primitives."""

from __future__ import annotations

from typing import Any

import pandas as pd
from statsmodels.tsa.statespace.sarimax import SARIMAX


DEFAULT_ORDER = (0, 0, 1)
DEFAULT_SEASONAL_ORDER = (0, 0, 0, 0)


def fit(
    series: pd.Series,
    *,
    exog: pd.DataFrame | None = None,
    order: tuple[int, int, int] = DEFAULT_ORDER,
    seasonal_order: tuple[int, int, int, int] = DEFAULT_SEASONAL_ORDER,
    trend: str = "c",
    enforce_stationarity: bool = False,
    enforce_invertibility: bool = False,
) -> Any:
    """Fit SARIMAX with the configuration used by the notebook."""

    return SARIMAX(
        series,
        exog=exog,
        order=order,
        seasonal_order=seasonal_order,
        trend=trend,
        enforce_stationarity=enforce_stationarity,
        enforce_invertibility=enforce_invertibility,
    ).fit(disp=False)


def forecast(
    model: Any,
    horizon: int,
    *,
    exog: pd.DataFrame | None = None,
    index: pd.Index | None = None,
    clip_negative: bool = True,
) -> pd.Series:
    """Generate an out-of-sample SARIMAX forecast."""

    prediction = model.get_forecast(steps=horizon, exog=exog).predicted_mean
    result = pd.Series(prediction, index=index)
    return result.clip(lower=0) if clip_negative else result


def forecast_with_intervals(
    model: Any,
    horizon: int,
    *,
    exog: pd.DataFrame | None = None,
    index: pd.Index | None = None,
    alpha: float = 0.05,
    clip_negative: bool = True,
) -> pd.DataFrame:
    """Return forecast, lower and upper prediction bounds."""

    forecast_result = model.get_forecast(steps=horizon, exog=exog)
    prediction = pd.Series(forecast_result.predicted_mean, index=index)
    intervals = forecast_result.conf_int(alpha=alpha)
    intervals.index = index if index is not None else intervals.index
    result = pd.DataFrame(
        {
            "prediccion": prediction,
            "limite_inferior": intervals.iloc[:, 0],
            "limite_superior": intervals.iloc[:, 1],
        }
    )
    if clip_negative:
        result[["prediccion", "limite_inferior", "limite_superior"]] = result[
            ["prediccion", "limite_inferior", "limite_superior"]
        ].clip(lower=0)
    return result
