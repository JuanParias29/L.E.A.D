"""Equivalence tests for extracted forecasting model primitives."""

from __future__ import annotations

import unittest

import numpy as np
import pandas as pd
from statsmodels.tsa.arima.model import ARIMA
from statsmodels.tsa.statespace.sarimax import SARIMAX

from models.arima.model import fit as fit_arima
from models.arima.model import forecast as forecast_arima
from models.sarima.model import fit_auto as fit_auto_sarima
from models.sarima.model import forecast as forecast_sarima
from models.sarimax.model import fit as fit_sarimax
from models.sarimax.model import forecast as forecast_sarimax
from models.sarimax.model import forecast_with_intervals
from src.lead.forecasting.evaluation import calculate_metrics, compare_models
from src.lead.forecasting.split import split_last_months
from src.lead.preprocessing.stockouts import impute_stockout_demand


class ForecastingModelEquivalenceTests(unittest.TestCase):
    def setUp(self) -> None:
        index = pd.date_range("2024-01-01", periods=40, freq="W-MON")
        self.series = pd.Series(
            100 + np.sin(np.arange(40) / 3) * 5 + np.arange(40) * 0.1,
            index=index,
            dtype=float,
        )
        self.future_index = pd.date_range(
            index[-1] + pd.Timedelta(weeks=1),
            periods=6,
            freq="W-MON",
        )

    def test_arima_matches_direct_statsmodels_implementation(self) -> None:
        order = (0, 0, 1)
        direct = ARIMA(self.series, order=order).fit()
        modular = fit_arima(self.series, order)

        expected = direct.forecast(steps=6).clip(lower=0)
        actual = forecast_arima(
            modular,
            6,
            index=self.future_index,
        )

        np.testing.assert_allclose(expected.to_numpy(), actual.to_numpy())
        self.assertAlmostEqual(float(direct.aic), float(modular.aic))

    def test_sarimax_matches_direct_statsmodels_implementation(self) -> None:
        exog = pd.DataFrame(
            {"evento": (np.arange(40) % 5 == 0).astype(float)},
            index=self.series.index,
        )
        future_exog = pd.DataFrame(
            {"evento": [0.0, 1.0, 0.0, 0.0, 1.0, 0.0]},
            index=self.future_index,
        )
        kwargs = {
            "order": (0, 0, 1),
            "seasonal_order": (0, 0, 0, 0),
            "trend": "c",
            "enforce_stationarity": False,
            "enforce_invertibility": False,
        }
        direct = SARIMAX(self.series, exog=exog, **kwargs).fit(disp=False)
        modular = fit_sarimax(self.series, exog=exog, **kwargs)

        expected = direct.get_forecast(steps=6, exog=future_exog).predicted_mean.clip(lower=0)
        actual = forecast_sarimax(
            modular,
            6,
            exog=future_exog,
            index=self.future_index,
        )

        np.testing.assert_allclose(expected.to_numpy(), actual.to_numpy())
        self.assertAlmostEqual(float(direct.aic), float(modular.aic))

    def test_sarimax_intervals_match_direct_result(self) -> None:
        direct = SARIMAX(
            self.series,
            order=(0, 0, 1),
            seasonal_order=(0, 0, 0, 0),
            trend="c",
            enforce_stationarity=False,
            enforce_invertibility=False,
        ).fit(disp=False)
        modular = fit_sarimax(
            self.series,
            order=(0, 0, 1),
            seasonal_order=(0, 0, 0, 0),
            trend="c",
            enforce_stationarity=False,
            enforce_invertibility=False,
        )

        expected = direct.get_forecast(steps=6).conf_int(alpha=0.05).clip(lower=0)
        actual = forecast_with_intervals(
            modular,
            6,
            index=self.future_index,
        )

        np.testing.assert_allclose(
            expected.iloc[:, 0].to_numpy(),
            actual["limite_inferior"].to_numpy(),
        )
        np.testing.assert_allclose(
            expected.iloc[:, 1].to_numpy(),
            actual["limite_superior"].to_numpy(),
        )

    def test_sarima_wrapper_preserves_horizon_and_nonnegative_clipping(self) -> None:
        model = fit_auto_sarima(self.series, seasonal_period=3)
        prediction = forecast_sarima(
            model,
            4,
            index=self.future_index[:4],
        )

        self.assertEqual(len(prediction), 4)
        self.assertTrue((prediction >= 0).all())

    def test_stockout_imputation_returns_separate_outputs(self) -> None:
        mask = pd.Series(False, index=self.series.index)
        mask.iloc[5] = True
        mask.iloc[10] = True
        observed = self.series.copy()
        observed.iloc[5] = 0
        observed.iloc[10] = 5

        result = impute_stockout_demand(observed, mask)

        self.assertEqual(result.method.iloc[5], "SARIMAX-Kalman: demanda cero")
        self.assertEqual(result.method.iloc[10], "Contrafactual restringido")
        self.assertEqual(len(result.counterfactual), len(observed))
        self.assertTrue((result.imputed >= 0).all())

    def test_split_and_metrics_preserve_notebook_contract(self) -> None:
        train, test, cutoff = split_last_months(self.series, months=6)
        self.assertEqual(cutoff, self.series.index.max() - pd.DateOffset(months=6))
        self.assertTrue((train.index <= cutoff).all())
        self.assertTrue((test.index > cutoff).all())

        metrics = calculate_metrics(test, test + 1)
        self.assertAlmostEqual(metrics["MAE"], 1.0)
        self.assertAlmostEqual(metrics["RMSE"], 1.0)
        self.assertAlmostEqual(metrics["WAPE_%"], 100 / test.abs().sum() * len(test))

        comparison = compare_models(
            [
                {"modelo": "B", "RMSE": 2.0, "MAE": 1.0},
                {"modelo": "A", "RMSE": 1.0, "MAE": 2.0},
            ]
        )
        self.assertEqual(comparison.iloc[0]["modelo"], "A")


if __name__ == "__main__":
    unittest.main()
