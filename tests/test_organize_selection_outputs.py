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
            rows = []
            for product_number in range(20):
                rows.extend(
                    [
                        {
                            "FECHA": "2025-02-02",
                            "IDProducto": product_number,
                            "Producto": f"Producto {product_number}",
                            "PctVenta": 20 - product_number,
                            "PctAcum": 20 - product_number,
                        },
                        {
                            "FECHA": "2024-01-01",
                            "IDProducto": product_number,
                            "Producto": f"Producto {product_number}",
                            "PctVenta": 20 - product_number,
                            "PctAcum": 20 - product_number,
                        },
                    ]
                )
            frame = pd.DataFrame(rows)
            frame.to_csv(output_dir / "productos_importados_AX.csv", sep=";", index=False)
            frame.to_csv(output_dir / "productos_no_importados_AX.csv", sep=";", index=False)

            markdown_path = generate_outputs(root)
            markdown = markdown_path.read_text(encoding="utf-8")
            self.assertIn(
                "| 1 | 19 | Producto 19 | 01/01/2024 - 02/02/2025 |", markdown
            )
            product_rows = [line for line in markdown.splitlines() if line.startswith("| ")]
            self.assertEqual(len(product_rows), 42)
            self.assertEqual(
                (output_dir / "productos_nacionales_AX.csv").read_bytes(),
                (output_dir / "productos_no_importados_AX.csv").read_bytes(),
            )

    def test_rejects_fewer_than_twenty_products(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            output_dir = root / "data" / "outputs"
            output_dir.mkdir(parents=True)
            frame = pd.DataFrame(
                {
                    "FECHA": ["2025-02-02"],
                    "IDProducto": [1],
                    "Producto": ["Producto único"],
                    "PctVenta": [1.0],
                    "PctAcum": [1.0],
                }
            )
            frame.to_csv(output_dir / "productos_importados_AX.csv", sep=";", index=False)
            frame.to_csv(output_dir / "productos_no_importados_AX.csv", sep=";", index=False)

            with self.assertRaisesRegex(ValueError, "al menos 20"):
                generate_outputs(root)


if __name__ == "__main__":
    unittest.main()