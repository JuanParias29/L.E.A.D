"""Tests for organizing the existing AX selection outputs."""

from __future__ import annotations

import tempfile
import unittest
from pathlib import Path

import pandas as pd

from scripts.organize_selection_outputs import generate_outputs


class OrganizeSelectionOutputsTests(unittest.TestCase):
    def test_generates_national_copy_and_ranked_markdown(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            output_dir = root / "data" / "outputs"
            output_dir.mkdir(parents=True)
            frame = pd.DataFrame(
                {
                    "FECHA": ["2025-02-02", "2024-01-01", "2025-01-01"],
                    "IDProducto": [2, 1, 1],
                    "Producto": ["Segundo", "Primero", "Primero"],
                    "PctVenta": [2.0, 5.0, 5.0],
                    "PctAcum": [30.0, 10.0, 10.0],
                }
            )
            frame.to_csv(output_dir / "productos_importados_AX.csv", sep=";", index=False)
            frame.to_csv(output_dir / "productos_no_importados_AX.csv", sep=";", index=False)

            with self.assertRaisesRegex(ValueError, "al menos 20"):
                generate_outputs(root)


if __name__ == "__main__":
    unittest.main()