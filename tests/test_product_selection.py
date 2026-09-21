"""Focused tests for the third refactoring stage."""

from __future__ import annotations

import unittest

import pandas as pd

from src.lead.data.product_selection import (
    brand_proportions,
    calculate_pareto,
    classify_abc_xyz,
    filter_product_origin,
    select_ax_rows,
    select_ax_pareto,
)


class ProductSelectionTests(unittest.TestCase):
    def setUp(self) -> None:
        self.frame = pd.DataFrame(
            {
                "FECHA": pd.to_datetime(
                    [
                        "2025-01-01",
                        "2025-01-08",
                        "2025-01-15",
                        "2025-01-01",
                        "2025-01-08",
                        "2025-01-15",
                        "2025-01-01",
                    ]
                ),
                "Producto": [
                    "PRODUCTO KAUDAL",
                    "PRODUCTO KAUDAL",
                    "PRODUCTO KAUDAL",
                    "PRODUCTO VIGOR",
                    "PRODUCTO VIGOR",
                    "PRODUCTO VIGOR",
                    "PRODUCTO OTRO",
                ],
                "VentaTotal": [
                    26.67,
                    26.67,
                    26.66,
                    5.0,
                    0.0,
                    15.0,
                    5.0,
                ],
                "Facturado": [10, 10, 10, 1, 0, 2, 1],
                "BackOrder": [0, 0, 0, 0, 0, 0, 0],
                "FlagImportado": [1, 1, 1, 1, 1, 1, 0],
            }
        )

    def test_calculates_pareto_and_ax_selection(self) -> None:
        imported = filter_product_origin(self.frame, imported=True)
        pareto, pareto_products = calculate_pareto(imported)
        summary = classify_abc_xyz(imported)
        selected = select_ax_pareto(summary, pareto_products, top_n=20)

        self.assertEqual(pareto.index[0], "PRODUCTO KAUDAL")
        self.assertIn("PRODUCTO KAUDAL", pareto_products.index)
        self.assertEqual(summary.loc["PRODUCTO KAUDAL", "ABC"], "A")
        self.assertEqual(summary.loc["PRODUCTO KAUDAL", "XYZ"], "X")
        self.assertEqual(list(selected.index), ["PRODUCTO KAUDAL"])

    def test_filters_national_products(self) -> None:
        national = filter_product_origin(self.frame, imported=False)

        self.assertEqual(list(national["Producto"]), ["PRODUCTO OTRO"])

    def test_select_ax_rows_preserves_source_columns(self) -> None:
        selected = select_ax_rows(self.frame, imported=True)

        self.assertEqual(len(selected), 3)
        self.assertEqual(selected["Producto"].nunique(), 1)
        self.assertTrue({"FECHA", "FlagImportado", "VentaTotal"}.issubset(selected.columns))
        self.assertTrue({"ABC", "XYZ", "Clase", "CV"}.issubset(selected.columns))

    def test_calculates_brand_proportions(self) -> None:
        result = brand_proportions(
            ["PRODUCTO KAUDAL", "PRODUCTO VIGOR", "PRODUCTO DESCONOCIDO"]
        )
        proportions = dict(zip(result["Línea"], result["Proporción (%)"]))

        self.assertAlmostEqual(proportions["KAUDAL"], 100 / 3)
        self.assertAlmostEqual(proportions["VIGOR"], 100 / 3)
        self.assertAlmostEqual(proportions["OTROS"], 100 / 3)


if __name__ == "__main__":
    unittest.main()
