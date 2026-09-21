"""Experiment orchestration extracted from ``04_modeladogeneral.py``."""

from __future__ import annotations

from typing import Any

import pandas as pd

from models.arima.model import fit as fit_arima
from models.arima.model import fit_auto as fit_auto_arima
from models.arima.model import forecast as forecast_arima
from models.sarima.model import fit_auto as fit_auto_sarima
from models.sarima.model import forecast as forecast_sarima
from src.lead.forecasting.evaluation import calculate_metrics, compare_models


def run_arima_experiment(
    train: pd.Series,
    test: pd.Series,
    *,
    manual_range: range = range(3),
) -> dict[str, Any]:
    """Run Auto ARIMA and the notebook's manual p/q grid."""

    results: list[dict[str, object]] = []
    predictions: dict[str, pd.Series] = {}
    models: dict[str, Any] = {}

    automatic = fit_auto_arima(train)
    automatic_prediction = forecast_arima(
        automatic,
        len(test),
        index=test.index,
    )
    automatic_order = automatic.order
    automatic_metrics = calculate_metrics(test, automatic_prediction)
    results.append(
        {
            "modelo": "Auto ARIMA",
            "orden": str(automatic_order),
            "p": automatic_order[0],
            "d": automatic_order[1],
            "q": automatic_order[2],
            **automatic_metrics,
            "AIC": automatic.aic(),
        }
    )
    predictions["Auto ARIMA"] = automatic_prediction
    models["Auto ARIMA"] = automatic

    for p in manual_range:
        for q in manual_range:
            order = (p, automatic_order[1], q)
            try:
                model = fit_arima(train, order)
                prediction = forecast_arima(
                    model,
                    len(test),
                    index=test.index,
                )
                name = f"ARIMA{order}"
                results.append(
                    {
                        "modelo": name,
                        "orden": str(order),
                        "p": p,
                        "d": automatic_order[1],
                        "q": q,
                        **calculate_metrics(test, prediction),
                        "AIC": model.aic,
                    }
                )
                predictions[name] = prediction
                models[name] = model
            except Exception:
                continue

    return {
        "results": compare_models(results),
        "predictions": predictions,
        "models": models,
    }


def run_sarima_experiment(
    train: pd.Series,
    test: pd.Series,
    *,
    seasonal_periods: tuple[int, ...] = (3, 4, 7),
) -> dict[str, Any]:
    """Run the notebook's SARIMA experiment for each seasonal period."""

    results: list[dict[str, object]] = []
    predictions: dict[str, pd.Series] = {}
    models: dict[str, Any] = {}

    for period in seasonal_periods:
        try:
            model = fit_auto_sarima(train, period)
            prediction = forecast_sarima(
                model,
                len(test),
                index=test.index,
            )
            name = f"SARIMA m={period}"
            results.append(
                {
                    "modelo": name,
                    "orden": str(model.order),
                    "orden_estacional": str(model.seasonal_order),
                    "periodo": period,
                    **calculate_metrics(test, prediction),
                    "AIC": model.aic(),
                }
            )
            predictions[name] = prediction
            models[name] = model
        except Exception:
            continue

    return {
        "results": compare_models(results),
        "predictions": predictions,
        "models": models,
    }
