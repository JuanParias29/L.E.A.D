"""Tests for weekly forecasting-series preparation."""

from __future__ import annotations

import unittest

import pandas as pd

from src.lead.forecasting.series import (
    prepare_forecasting_split,
    prepare_product_weekly_series,
)


class ForecastingSeriesTests(unittest.TestCase):
    def test_builds_weekly_demand_events_stockout_and_lagged_price(self) -> None:
        dates = pd.date_range("2024-01-01", periods=4, freq="W-MON")
        product = pd.DataFrame(
            {
                "FECHA": dates,
                "IDProducto": [10] * 4,
                "Facturado": [2, 3, 4, 5],
                "BackOrder": [1, 0, 1, 0],
                "VlrUnitario": [100.0, None, 120.0, 130.0],
            }
        )
        stockouts = pd.DataFrame(
            {
                "IDProductos": [10],
                "FechaInicial": ["2024-01-07"],
                "FechaFinal": ["2024-01-09"],
            }
        )

        result = prepare_product_weekly_series(
            product,
            stockouts,
            events=((2024, 2, "Feria"),),
            minimum_weeks=1,
        )

        self.assertEqual(result.index.freqstr, "W-MON")
        self.assertEqual(result["demanda_observada"].tolist(), [3, 5, 5])
        self.assertEqual(result["Evento_Feria"].sum(), 1.0)
        self.assertEqual(result["Evento_QuiebreInventario"].sum(), 2.0)
        self.assertTrue(result["Precio_lag1"].notna().all())

    def test_rejects_short_series(self) -> None:
        product = pd.DataFrame(
            {
                "FECHA": ["2024-01-01"],
                "Facturado": [1],
                "BackOrder": [0],
                "VlrUnitario": [10.0],
            }
        )
        stockouts = pd.DataFrame(
            columns=["IDProductos", "FechaInicial", "FechaFinal"]
        )

        with self.assertRaisesRegex(ValueError, "Solo tiene"):
            prepare_product_weekly_series(product, stockouts)

    def test_splits_by_cutoff_and_drops_constant_event_features(self) -> None:
        index = pd.date_range("2024-01-01", periods=50, freq="W-MON")
        weekly = pd.DataFrame(
            {
                "demanda_real": range(50),
                "Evento_Feria": [0] * 20 + [1] * 10 + [0] * 20,
                "Evento_Constante": [0] * 50,
            },
            index=index,
        )

        result = prepare_forecasting_split(
            weekly,
            index[41],
            minimum_train=40,
            minimum_test=8,
        )

        self.assertEqual(len(result.train), 42)
        self.assertEqual(len(result.test), 8)
        self.assertEqual(result.feature_columns, ("Evento_Feria",))
        self.assertEqual(result.X_train.columns.tolist(), ["Evento_Feria"])
        self.assertEqual(result.y_test.iloc[0], 42.0)

    def test_rejects_missing_target_column(self) -> None:
        weekly = pd.DataFrame(
            {"Evento_Feria": [0, 1]},
            index=pd.date_range("2024-01-01", periods=2, freq="W-MON"),
        )

        with self.assertRaisesRegex(ValueError, "columna objetivo"):
            prepare_forecasting_split(weekly, weekly.index[0])


if __name__ == "__main__":
    unittest.main()