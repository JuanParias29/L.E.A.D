"""Experiment orchestration extracted from ``04_modeladogeneral.py``."""

from __future__ import annotations

from typing import Any

import pandas as pd

from models.arima.model import fit as fit_arima
from models.arima.model import fit_auto as fit_auto_arima
from models.arima.model import forecast as forecast_arima
from models.sarima.model import fit_auto as fit_auto_sarima
from models.sarima.model import forecast as forecast_sarima
from models.sarimax.model import fit as fit_sarimax
from models.sarimax.model import forecast as forecast_sarimax
from src.lead.forecasting.evaluation import calculate_metrics, compare_models
from src.lead.forecasting.evaluation import evaluate_model


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


def run_sarimax_experiment(
    train: pd.Series,
    test: pd.Series,
    *,
    base_train_exog: pd.DataFrame | None = None,
    base_test_exog: pd.DataFrame | None = None,
    price_train_exog: pd.DataFrame | None = None,
    price_test_exog: pd.DataFrame | None = None,
    order: tuple[int, int, int] = (0, 0, 1),
    seasonal_order: tuple[int, int, int, int] = (0, 0, 0, 0),
    trend: str = "c",
) -> dict[str, Any]:
    """Compare SARIMAX with base exogenous variables and optional price."""

    variants: list[
        tuple[str, pd.DataFrame | None, pd.DataFrame | None]
    ] = [
        ("SARIMAX sin precio", base_train_exog, base_test_exog),
    ]
    if price_train_exog is not None or price_test_exog is not None:
        if price_train_exog is None or price_test_exog is None:
            raise ValueError(
                "Las exógenas con precio requieren entrenamiento y prueba."
            )
        variants.append(
            ("SARIMAX con precio", price_train_exog, price_test_exog)
        )

    results: list[dict[str, object]] = []
    predictions: dict[str, pd.Series] = {}
    models: dict[str, Any] = {}

    for name, train_exog, test_exog in variants:
        model = fit_sarimax(
            train,
            exog=train_exog,
            order=order,
            seasonal_order=seasonal_order,
            trend=trend,
            enforce_stationarity=False,
            enforce_invertibility=False,
        )
        prediction = forecast_sarimax(
            model,
            len(test),
            exog=test_exog,
            index=test.index,
        )
        results.append(evaluate_model(name, test, prediction, model))
        predictions[name] = prediction
        models[name] = model

    return {
        "results": compare_models(results),
        "predictions": predictions,
        "models": models,
    }
