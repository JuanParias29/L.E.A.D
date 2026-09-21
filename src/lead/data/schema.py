"""Schema definitions for the transaction datasets used by L.E.A.D."""

from __future__ import annotations

from collections.abc import Iterable

# Columns documented in notebooks/01_eda_general.py for the sales dataset.
SALES_COLUMNS = (
    "FECHA",
    "Bodega",
    "IDFactura",
    "IDProducto",
    "VlrUnitario",
    "Producto",
    "ClaseProducto",
    "TipoProducto",
    "FlagImportado",
    "Cliente",
    "Municipio",
    "Departamento",
    "Vendedor",
    "Facturado",
    "BackOrder",
    "ClaseVenta",
    "ProductoObsequio",
    "CantidadObsequio",
    "DiasImportacion",
)


class DataSchemaError(ValueError):
    """Raised when an input dataset does not meet its structural contract."""


def validate_required_columns(
    columns: Iterable[str],
    required: Iterable[str] = SALES_COLUMNS,
) -> None:
    """Raise ``DataSchemaError`` when required columns are absent."""

    available = set(columns)
    missing = [column for column in required if column not in available]
    if missing:
        missing_text = ", ".join(missing)
        raise DataSchemaError(
            f"El dataset no contiene las columnas requeridas: {missing_text}"
        )
