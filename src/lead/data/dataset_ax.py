"""Build the consolidated AX dataset without altering demand observations."""

from __future__ import annotations

from collections.abc import Iterable
from pathlib import Path

import pandas as pd

from .schema import SALES_COLUMNS


STOCKOUT_COLUMNS = ("IDProductos", "FechaInicial", "FechaFinal")
RAW_SALES_COLUMNS = (
    "FECHA",
    "Semana",
    "Bodega",
    "IDFactura",
    "IDProducto",
    "VlrUnitario",
    "Producto",
    "ClaseProducto",
    "DiasImportacion",
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
)


def load_sales_source(path: str | Path) -> pd.DataFrame:
    """Load a sales CSV whether it has the canonical header or no header."""

    source_path = Path(path)
    with source_path.open("r", encoding="utf-8-sig") as handle:
        first_line = handle.readline().strip().split(",")

    if set(SALES_COLUMNS).issubset(first_line):
        return pd.read_csv(source_path, sep=",", low_memory=False)

    return pd.read_csv(
        source_path,
        sep=",",
        header=None,
        names=RAW_SALES_COLUMNS,
        low_memory=False,
    )


def load_ax_product_ids(
    selection_paths: Iterable[str | Path],
) -> set[int]:
    """Return the product IDs present in the existing AX selections."""

    product_ids: set[int] = set()
    for path in selection_paths:
        selection = pd.read_csv(path, sep=";", usecols=["IDProducto"])
        product_ids.update(selection["IDProducto"].dropna().astype(int).tolist())
    return product_ids


def load_stockout_intervals(path: str | Path) -> pd.DataFrame:
    """Load and validate stockout intervals using the source's MM/DD/YYYY dates."""

    stockouts = pd.read_csv(path, sep=";", low_memory=False)
    missing = set(STOCKOUT_COLUMNS) - set(stockouts.columns)
    if missing:
        raise ValueError(f"Faltan columnas de stockout: {sorted(missing)}")

    stockouts = stockouts.loc[:, STOCKOUT_COLUMNS].copy()
    stockouts["IDProductos"] = pd.to_numeric(
        stockouts["IDProductos"], errors="raise"
    ).astype(int)
    for column in ("FechaInicial", "FechaFinal"):
        stockouts[column] = pd.to_datetime(
            stockouts[column], format="%m/%d/%Y", errors="raise"
        )
    if (stockouts["FechaFinal"] < stockouts["FechaInicial"]).any():
        raise ValueError("Existen intervalos de stockout con fecha final anterior")
    return stockouts


def _merge_intervals(intervals: pd.DataFrame) -> list[tuple[pd.Timestamp, pd.Timestamp]]:
    merged: list[tuple[pd.Timestamp, pd.Timestamp]] = []
    for start, end in intervals.sort_values("FechaInicial")[["FechaInicial", "FechaFinal"]].itertuples(index=False):
        if not merged or start > merged[-1][1] + pd.Timedelta(days=1):
            merged.append((start, end))
        else:
            merged[-1] = (merged[-1][0], max(merged[-1][1], end))
    return merged


def mark_stockouts(
    sales: pd.DataFrame,
    stockouts: pd.DataFrame,
    *,
    product_column: str = "IDProducto",
    date_column: str = "FECHA",
) -> pd.DataFrame:
    """Mark sales rows whose date falls inside a product stockout interval."""

    result = sales.copy()
    result[date_column] = pd.to_datetime(result[date_column], errors="coerce")
    result["stockout"] = False
    result["fecha_inicio_stockout"] = pd.NaT
    result["fecha_fin_stockout"] = pd.NaT

    for product_id, intervals_for_product in stockouts.groupby("IDProductos"):
        row_positions = result.index[result[product_column] == product_id]
        if len(row_positions) == 0:
            continue
        merged = _merge_intervals(intervals_for_product)
        dates = result.loc[row_positions, date_column]
        for start, end in merged:
            affected = dates.between(start, end, inclusive="both")
            affected_positions = dates.index[affected]
            result.loc[affected_positions, "stockout"] = True
            result.loc[affected_positions, "fecha_inicio_stockout"] = start
            result.loc[affected_positions, "fecha_fin_stockout"] = end

    return result


def build_dataset_ax(
    national_path: str | Path,
    imported_path: str | Path,
    national_selection_path: str | Path,
    imported_selection_path: str | Path,
    stockout_path: str | Path,
) -> pd.DataFrame:
    """Filter both origins to AX and add evidence-based stockout markers."""

    ax_ids = load_ax_product_ids(
        [national_selection_path, imported_selection_path]
    )
    national = load_sales_source(national_path)
    imported = load_sales_source(imported_path)
    national["tipo_producto"] = "nacional"
    imported["tipo_producto"] = "importado"
    combined = pd.concat([national, imported], ignore_index=True)
    combined["IDProducto"] = pd.to_numeric(combined["IDProducto"], errors="raise").astype(int)
    combined = combined.loc[combined["IDProducto"].isin(ax_ids)].copy()
    combined = mark_stockouts(combined, load_stockout_intervals(stockout_path))
    return combined