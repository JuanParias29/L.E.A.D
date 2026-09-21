"""Stockout imputation kept separate from forecasting model primitives."""

from __future__ import annotations

from dataclasses import dataclass

import numpy as np
import pandas as pd

from models.sarimax.model import fit as fit_sarimax


@dataclass(frozen=True)
class StockoutImputationResult:
    """Outputs produced by the notebook's counterfactual imputation."""

    observed: pd.Series
    counterfactual: pd.Series
    imputed: pd.Series
    omitted: pd.Series
    lower_bound: pd.Series
    upper_bound: pd.Series
    method: pd.Series
    model: object


def impute_stockout_demand(
    observed: pd.Series,
    stockout_mask: pd.Series,
    *,
    exog: pd.DataFrame | None = None,
    order: tuple[int, int, int] = (0, 0, 1),
    seasonal_order: tuple[int, int, int, int] = (0, 0, 0, 0),
    trend: str = "c",
) -> StockoutImputationResult:
    """Impute demand during stockouts using the current SARIMAX procedure.

    Observations marked as stockouts are hidden before fitting. The smoothed
    prediction is used as the counterfactual; positive observed demand remains
    a lower bound, while zero observed demand is replaced by the counterfactual.
    """

    complete = observed.astype(float).copy()
    mask = stockout_mask.astype(bool).reindex(complete.index, fill_value=False)
    censored = complete.copy()
    censored.loc[mask] = np.nan

    model = fit_sarimax(
        censored,
        exog=exog,
        order=order,
        seasonal_order=seasonal_order,
        trend=trend,
    )
    prediction = model.get_prediction(
        start=0,
        end=len(censored) - 1,
        information_set="smoothed",
    )
    counterfactual = prediction.predicted_mean.clip(lower=0)
    intervals = prediction.conf_int()
    lower_bound = intervals.iloc[:, 0].clip(lower=0)
    upper_bound = intervals.iloc[:, 1].clip(lower=0)

    imputed = complete.copy()
    zero_stockout = mask & (complete == 0)
    positive_stockout = mask & (complete > 0)
    imputed.loc[zero_stockout] = counterfactual.loc[zero_stockout]
    imputed.loc[positive_stockout] = np.maximum(
        complete.loc[positive_stockout],
        counterfactual.loc[positive_stockout],
    )

    omitted = (imputed - complete).clip(lower=0)
    method = pd.Series("Sin imputación", index=complete.index, dtype="object")
    method.loc[zero_stockout] = "SARIMAX-Kalman: demanda cero"
    method.loc[positive_stockout] = "Contrafactual restringido"

    return StockoutImputationResult(
        observed=complete,
        counterfactual=counterfactual,
        imputed=imputed,
        omitted=omitted,
        lower_bound=lower_bound,
        upper_bound=upper_bound,
        method=method,
        model=model,
    )
