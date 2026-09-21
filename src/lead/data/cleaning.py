"""Cleaning and type transformations extracted from the EDA notebook."""

from __future__ import annotations

from collections.abc import Iterable

import pandas as pd


CATEGORY_COLUMNS = (
    "Bodega",
    "Producto",
    "ClaseProducto",
    "TipoProducto",
    "Cliente",
    "Municipio",
    "Departamento",
    "ClaseVenta",
    "ProductoObsequio",
)

INTEGER_COLUMNS = (
    "Facturado",
    "BackOrder",
    "CantidadObsequio",
)

ATYPICAL_CLIENT_PATTERNS = (
    "MOSTRADOR",
    "CONTADOR",
    "CONTADO",
    "LOGISTICA FERRETERA BARRANQUILLA",
)

INVALID_SELLER_PATTERNS = (
    "MOSTRADOR",
    "MERCADO LIBRE",
    "LICITACIONES",
    "ADMINISTRATIVO",
    "MGIL-NOUSAR",
    "TRANSFERENCIAS",
)


def convert_sales_types(
    frame: pd.DataFrame,
    *,
    copy: bool = True,
) -> pd.DataFrame:
    """Apply the initial type conversions from ``01_eda_general.py``."""

    data = frame.copy() if copy else frame
    data["FECHA"] = pd.to_datetime(data["FECHA"], errors="coerce")

    for column in CATEGORY_COLUMNS:
        data[column] = data[column].astype("category")

    data["IDFactura"] = data["IDFactura"].astype("int64")

    for column in INTEGER_COLUMNS:
        if data[column].dtype == object:
            data[column] = (
                data[column]
                .str.replace(",", ".")
                .astype(float)
                .fillna(0)
                .astype("int64")
            )
        else:
            data[column] = data[column].fillna(0).astype("int64")

    return data


def drop_missing_unit_prices(
    frame: pd.DataFrame,
    *,
    copy: bool = True,
) -> pd.DataFrame:
    """Remove rows with a null ``VlrUnitario`` as done in the notebook."""

    data = frame.dropna(subset=["VlrUnitario"])
    return data.copy() if copy else data


def _remove_rows_matching(
    frame: pd.DataFrame,
    column: str,
    patterns: Iterable[str],
) -> pd.DataFrame:
    data = frame.copy()
    data[column] = data[column].astype(str).str.strip().str.upper()
    pattern = "|".join(patterns)
    mask = data[column].str.contains(pattern, na=False, regex=True)
    return data.loc[~mask].copy()


def remove_atypical_clients(
    frame: pd.DataFrame,
    *,
    patterns: Iterable[str] = ATYPICAL_CLIENT_PATTERNS,
) -> pd.DataFrame:
    """Remove client names classified as atypical in the EDA notebook."""

    data = _remove_rows_matching(frame, "Cliente", patterns)
    data["Cliente"] = data["Cliente"].astype("category")
    return data


def remove_logistica_ferretera_clients(frame: pd.DataFrame) -> pd.DataFrame:
    """Apply the notebook's second, broader logistics-client filter."""

    data = _remove_rows_matching(frame, "Cliente", ("LOGISTICA FERRETERA",))
    data["Cliente"] = data["Cliente"].astype("category")
    return data


def add_sales_amounts(frame: pd.DataFrame) -> pd.DataFrame:
    """Create ``VentaTotal``, ``VentaReal`` and ``BackOrderValue``."""

    data = frame.copy()
    for column in ("VlrUnitario", "Facturado"):
        if not pd.api.types.is_numeric_dtype(data[column]):
            data[column] = (
                data[column]
                .astype(str)
                .str.replace(",", ".", regex=False)
                .astype(float)
            )

    data["VentaTotal"] = data["VlrUnitario"] * data["Facturado"]
    data["VentaReal"] = data["Facturado"] * data["VlrUnitario"]
    data["BackOrderValue"] = data["BackOrder"] * data["VlrUnitario"]
    return data


def remove_invalid_sellers(
    frame: pd.DataFrame,
    *,
    patterns: Iterable[str] = INVALID_SELLER_PATTERNS,
) -> pd.DataFrame:
    """Remove seller/channel values excluded by the current notebook rules."""

    return _remove_rows_matching(frame, "Vendedor", patterns)


def clean_sales_transactions(frame: pd.DataFrame) -> pd.DataFrame:
    """Run the current notebook cleaning sequence without changing its rules."""

    data = convert_sales_types(frame)
    data = drop_missing_unit_prices(data)
    data = remove_atypical_clients(data)
    data = remove_logistica_ferretera_clients(data)
    data = add_sales_amounts(data)
    return remove_invalid_sellers(data)
