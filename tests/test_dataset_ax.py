from __future__ import annotations

import tempfile
import unittest
from pathlib import Path

import pandas as pd

from src.lead.data.dataset_ax import build_dataset_ax


class DatasetAxTests(unittest.TestCase):
    def test_builds_ax_rows_and_marks_stockout_without_duplication(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            national = root / "national.csv"
            imported = root / "imported.csv"
            national_selection = root / "national_ax.csv"
            imported_selection = root / "imported_ax.csv"
            stockouts = root / "stockouts.csv"
            columns = [
                "2025-01-06", 1, "BODEGA", 1, 10, 2.0, "N", "Clase", "5", "Tipo", 0,
                "Cliente", "Municipio", "Departamento", "Vendedor", 3, 0, "NORMAL", "", 0,
            ]
            pd.DataFrame([columns]).to_csv(national, index=False, header=False)
            imported_columns = columns.copy()
            imported_columns[4] = 20
            imported_columns[10] = 1
            pd.DataFrame([imported_columns]).to_csv(imported, index=False, header=False)
            pd.DataFrame({"IDProducto": [10]}).to_csv(national_selection, sep=";", index=False)
            pd.DataFrame({"IDProducto": [20]}).to_csv(imported_selection, sep=";", index=False)
            pd.DataFrame(
                {"IDProductos": [10], "FechaInicial": ["01/05/2025"], "FechaFinal": ["01/07/2025"]}
            ).to_csv(stockouts, sep=";", index=False)

            result = build_dataset_ax(
                national, imported, national_selection, imported_selection, stockouts
            )

            self.assertEqual(len(result), 2)
            self.assertEqual(set(result["tipo_producto"]), {"nacional", "importado"})
            self.assertEqual(result["stockout"].sum(), 1)
            self.assertEqual(result["IDProducto"].nunique(), 2)


if __name__ == "__main__":
    unittest.main()