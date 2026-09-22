"""Generate the local consolidated AX dataset."""

from __future__ import annotations

import argparse
from pathlib import Path
import sys

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from src.lead.data.dataset_ax import build_dataset_ax


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--root", type=Path, default=Path.cwd())
    parser.add_argument("--output", type=Path, default=Path("data/processed/dataset_ax.csv"))
    args = parser.parse_args()
    root = args.root.resolve()
    output = args.output if args.output.is_absolute() else root / args.output

    dataset = build_dataset_ax(
        root / "data/inputs/Dataset_Nacionales.csv",
        root / "data/inputs/Dataset_Importados.csv",
        root / "data/outputs/productos_nacionales_AX.csv",
        root / "data/outputs/productos_importados_AX.csv",
        root / "data/inputs/Stockout_productos.csv",
    )
    output.parent.mkdir(parents=True, exist_ok=True)
    dataset.to_csv(output, sep=";", index=False)
    print(f"Generado: {output}")
    print(f"Registros: {len(dataset)}")
    print(f"Columnas: {len(dataset.columns)}")
    print(f"Productos: {dataset['IDProducto'].nunique()}")
    print(f"Stockouts marcados: {int(dataset['stockout'].sum())}")


if __name__ == "__main__":
    main()