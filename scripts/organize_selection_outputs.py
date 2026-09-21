"""Organize the existing AX product-selection outputs."""

from __future__ import annotations

import shutil
from pathlib import Path

import pandas as pd


PROJECT_ROOT = Path(__file__).resolve().parents[1]
OUTPUT_DIR = PROJECT_ROOT / "data" / "outputs"
IMPORTED_INPUT = OUTPUT_DIR / "productos_importados_AX.csv"
NATIONAL_INPUT = OUTPUT_DIR / "productos_no_importados_AX.csv"
NATIONAL_OUTPUT = OUTPUT_DIR / "productos_nacionales_AX.csv"
MARKDOWN_OUTPUT = OUTPUT_DIR / "productos_AX.md"
REQUIRED_COLUMNS = {
    "FECHA",
    "IDProducto",
    "Producto",
    "PctVenta",
    "PctAcum",
}


def _read_selection(path: Path, *, exclude_supermastick: bool = False) -> pd.DataFrame:
    if not path.exists():
        raise FileNotFoundError(f"No existe el archivo de entrada: {path}")

    frame = pd.read_csv(path, sep=";", encoding="utf-8")
    missing = REQUIRED_COLUMNS.difference(frame.columns)
    if missing:
        columns = ", ".join(sorted(missing))
        raise ValueError(f"{path.name} no contiene las columnas requeridas: {columns}")

    frame["FECHA"] = pd.to_datetime(frame["FECHA"], errors="coerce")
    if frame["FECHA"].isna().any():
        raise ValueError(f"{path.name} contiene fechas inválidas en FECHA")

    if frame["Producto"].isna().any() or frame["IDProducto"].isna().any():
        raise ValueError(f"{path.name} contiene productos sin código o descripción")

    ordered = frame.sort_values(
        ["PctAcum", "PctVenta"], ascending=[True, False], kind="stable"
    )
    products = ordered.drop_duplicates("Producto", keep="first").copy()
    if len(products) < 20:
        raise ValueError(
            f"{path.name} contiene {len(products)} productos; se requieren al menos 20."
        )

    identifiers_per_product = frame.groupby("Producto", observed=False)["IDProducto"].nunique()
    inconsistent = identifiers_per_product[identifiers_per_product != 1]
    if not inconsistent.empty:
        raise ValueError(
            f"{path.name} tiene varios códigos para: {', '.join(inconsistent.index.astype(str))}"
        )

    if exclude_supermastick:
        products = products.loc[
            ~products["Producto"].str.contains("supermastick", case=False, na=False)
        ]

    dates = frame.groupby("Producto", observed=False)["FECHA"].agg(
        first_date="min", last_date="max"
    )
    return products.merge(
        dates, left_on="Producto", right_index=True, how="left"
    ).head(20)


def _format_product_code(value: object) -> str:
    if isinstance(value, float) and value.is_integer():
        return str(int(value))
    return str(value)


def _escape_markdown(value: object) -> str:
    return str(value).replace("|", "\\|").replace("\n", " ").replace("\r", " ")


def _markdown_section(title: str, products: pd.DataFrame) -> list[str]:
    lines = [
        f"## {title}",
        "",
        "| # | Código producto | Producto | Periodo registro |",
        "|---|---|---|---|",
    ]
    for number, (_, product) in enumerate(products.iterrows(), start=1):
        first_date = product["first_date"].strftime("%d/%m/%Y")
        last_date = product["last_date"].strftime("%d/%m/%Y")
        lines.append(
            f"| {number} | {_escape_markdown(_format_product_code(product['IDProducto']))} | "
            f"{_escape_markdown(product['Producto'])} | {first_date} - {last_date} |"
        )
    return lines


def generate_outputs(project_root: Path = PROJECT_ROOT) -> Path:
    output_dir = project_root / "data" / "outputs"
    imported_input = output_dir / "productos_importados_AX.csv"
    national_input = output_dir / "productos_no_importados_AX.csv"
    national_output = output_dir / "productos_nacionales_AX.csv"
    markdown_output = output_dir / "productos_AX.md"

    imported = _read_selection(imported_input)
    national = _read_selection(national_input, exclude_supermastick=True)

    shutil.copyfile(national_input, national_output)

    markdown = [
        "# Productos seleccionados AX",
        "",
        *_markdown_section("Productos importados", imported),
        "",
        *_markdown_section("Productos nacionales", national),
        "",
    ]
    markdown_output.write_text("\n".join(markdown), encoding="utf-8")
    return markdown_output


if __name__ == "__main__":
    generated = generate_outputs()
    print(f"Markdown generado: {generated.relative_to(PROJECT_ROOT)}")
    print(f"CSV nacional generado: {NATIONAL_OUTPUT.relative_to(PROJECT_ROOT)}")