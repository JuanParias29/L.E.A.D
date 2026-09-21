"""Focused tests for the first refactoring stage."""

from __future__ import annotations

import tempfile
import unittest
from pathlib import Path

from src.lead.data.loaders import load_sales_transactions
from src.lead.data.schema import DataSchemaError, SALES_COLUMNS


class SalesIngestionTests(unittest.TestCase):
    def test_loads_semicolon_csv_and_skips_bad_lines(self) -> None:
        valid_row = ";".join(["2025-01-01"] + ["value"] * (len(SALES_COLUMNS) - 1))
        header = ";".join(SALES_COLUMNS)
        malformed_row = ";".join(["bad"] * (len(SALES_COLUMNS) + 1))
        content = f"{header}\n{valid_row}\n{malformed_row}\n"

        with tempfile.TemporaryDirectory() as directory:
            path = Path(directory) / "sales.csv"
            path.write_text(content, encoding="utf-8")

            data = load_sales_transactions(path)

        self.assertEqual(len(data), 1)
        self.assertEqual(list(data.columns), list(SALES_COLUMNS))
        self.assertEqual(data.iloc[0]["FECHA"], "2025-01-01")

    def test_reports_missing_required_columns(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            path = Path(directory) / "incomplete.csv"
            path.write_text("FECHA;Producto\n2025-01-01;Producto A\n", encoding="utf-8")

            with self.assertRaises(DataSchemaError):
                load_sales_transactions(path)

    def test_reports_missing_file(self) -> None:
        with self.assertRaises(FileNotFoundError):
            load_sales_transactions("does-not-exist.csv")


if __name__ == "__main__":
    unittest.main()
