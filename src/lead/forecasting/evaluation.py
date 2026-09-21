"""Forecast metrics and model comparison utilities."""

from __future__ import annotations

import numpy as np
import pandas as pd
from sklearn.metrics import mean_absolute_error, mean_squared_error


def calculate_metrics(
    real: pd.Series,
    prediction: pd.Series,
) -> dict[str, float]:
    """Calculate the notebook's MAE, RMSE and WAPE metrics."""

    mae = mean_absolute_error(real, prediction)
    rmse = np.sqrt(mean_squared_error(real, prediction))
    wape = np.sum(np.abs(real - prediction)) / np.sum(np.abs(real)) * 100
    return {"MAE": mae, "RMSE": rmse, "WAPE_%": wape}


def evaluate_model(
    name: str,
    real: pd.Series,
    prediction: pd.Series,
    model: object,
) -> dict[str, float | str]:
    """Add model name and AIC to the notebook's forecast metrics."""

    result: dict[str, float | str] = {"modelo": name}
    result.update(calculate_metrics(real, prediction))
    result["AIC"] = float(model.aic)
    return result


def compare_models(results: list[dict[str, object]]) -> pd.DataFrame:
    """Sort model results by RMSE and then MAE, as in the notebook."""

    return pd.DataFrame(results).sort_values(
        ["RMSE", "MAE"],
        ascending=True,
    ).reset_index(drop=True)
