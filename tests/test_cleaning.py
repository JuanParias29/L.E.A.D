"""Focused tests for the second refactoring stage."""

from __future__ import annotations

import unittest

import pandas as pd

from src.lead.data.cleaning import clean_sales_transactions


class SalesCleaningTests(unittest.TestCase):
    def test_preserves_current_cleaning_rules_and_creates_amounts(self) -> None:
        frame = pd.DataFrame(
            {
                "FECHA": ["2025-01-01", "invalid", "2025-01-03", "2025-01-04"],
                "Bodega": ["B1"] * 4,
                "IDFactura": [1, 2, 3, 4],
                "IDProducto": [10, 11, 12, 13],
                "VlrUnitario": ["10,50", None, "20", "30"],
                "Producto": ["P1", "P2", "P3", "P4"],
                "ClaseProducto": ["C"] * 4,
                "TipoProducto": ["T"] * 4,
                "FlagImportado": [0] * 4,
                "Cliente": ["Cliente válido", "Cliente válido", "Mostrador Sur", "Cliente válido"],
                "Municipio": ["M"] * 4,
                "Departamento": ["D"] * 4,
                "Vendedor": ["Vendedor válido", "Vendedor válido", "Vendedor válido", "Mercado Libre"],
                "Facturado": ["2", "3", "4", "5"],
                "BackOrder": ["1", "0", "0", "2"],
                "ClaseVenta": ["NORMAL"] * 4,
                "ProductoObsequio": [None] * 4,
                "CantidadObsequio": ["0"] * 4,
                "DiasImportacion": [10] * 4,
            }
        )

        cleaned = clean_sales_transactions(frame)

        self.assertEqual(len(cleaned), 1)
        self.assertEqual(cleaned.iloc[0]["Producto"], "P1")
        self.assertTrue(pd.isna(cleaned.iloc[0]["FECHA"]) is False)
        self.assertEqual(cleaned.iloc[0]["Facturado"], 2)
        self.assertEqual(cleaned.iloc[0]["BackOrder"], 1)
        self.assertEqual(cleaned.iloc[0]["VentaTotal"], 21.0)
        self.assertEqual(cleaned.iloc[0]["VentaReal"], 21.0)
        self.assertEqual(cleaned.iloc[0]["BackOrderValue"], 10.5)

    def test_does_not_mutate_input_frame(self) -> None:
        frame = pd.DataFrame(
            {
                "FECHA": ["2025-01-01"],
                "Bodega": ["B1"],
                "IDFactura": [1],
                "IDProducto": [10],
                "VlrUnitario": ["10,50"],
                "Producto": ["P1"],
                "ClaseProducto": ["C"],
                "TipoProducto": ["T"],
                "FlagImportado": [0],
                "Cliente": ["Cliente válido"],
                "Municipio": ["M"],
                "Departamento": ["D"],
                "Vendedor": ["Vendedor válido"],
                "Facturado": ["2"],
                "BackOrder": ["1"],
                "ClaseVenta": ["NORMAL"],
                "ProductoObsequio": [None],
                "CantidadObsequio": ["0"],
                "DiasImportacion": [10],
            }
        )
        original = frame.copy(deep=True)

        clean_sales_transactions(frame)

        pd.testing.assert_frame_equal(frame, original)


if __name__ == "__main__":
    unittest.main()
