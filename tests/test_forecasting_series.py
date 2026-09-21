"""Tests for weekly forecasting-series preparation."""

from __future__ import annotations

import unittest

import pandas as pd

from src.lead.forecasting.series import prepare_product_weekly_series


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


if __name__ == "__main__":
    unittest.main()