"""Temporal preprocessing extracted from ``03_preprocesamiento.py``."""

from __future__ import annotations

from collections.abc import Iterable

import pandas as pd


def prepare_temporal_frame(
    frame: pd.DataFrame,
    *,
    date_column: str = "FECHA",
    numeric_columns: Iterable[str] = ("Facturado", "BackOrder"),
    drop_invalid_dates: bool = False,
) -> pd.DataFrame:
    """Convert temporal fields using the notebook's preprocessing rules."""

    data = frame.copy()
    data[date_column] = pd.to_datetime(data[date_column], errors="coerce")
    for column in numeric_columns:
        data[column] = pd.to_numeric(data[column], errors="coerce")

    if drop_invalid_dates:
        data = data.dropna(subset=[date_column]).copy()
    return data


def add_observed_demand(
    frame: pd.DataFrame,
    *,
    facturado_column: str = "Facturado",
    backorder_column: str = "BackOrder",
    output_column: str = "demanda_observada",
) -> pd.DataFrame:
    """Create the observed-demand proxy used by the temporal notebook."""

    data = frame.copy()
    data[output_column] = (
        data[facturado_column] + data[backorder_column]
    )
    return data


def aggregate_weekly_demand(
    frame: pd.DataFrame,
    *,
    value_columns: Iterable[str] = ("Facturado", "BackOrder"),
    date_column: str = "FECHA",
    frequency: str = "W",
) -> pd.DataFrame:
    """Aggregate selected numeric columns by calendar week and fill zeros."""

    columns = list(value_columns)
    data = prepare_temporal_frame(
        frame,
        date_column=date_column,
        numeric_columns=columns,
    ).dropna(subset=[date_column] + columns)
    return data.resample(frequency, on=date_column)[columns].sum().fillna(0)


def aggregate_weekly_by_group(
    frame: pd.DataFrame,
    *,
    group_column: str,
    value_column: str = "demanda_observada",
    date_column: str = "FECHA",
    frequency: str = "W",
) -> pd.DataFrame:
    """Aggregate a value weekly and pivot the selected grouping column."""

    data = prepare_temporal_frame(
        frame,
        date_column=date_column,
        numeric_columns=(value_column,),
        drop_invalid_dates=True,
    ).dropna(subset=[group_column, value_column])
    return (
        data.groupby(
            [pd.Grouper(key=date_column, freq=frequency), group_column],
            observed=False,
        )[value_column]
        .sum()
        .unstack(fill_value=0)
    )


def _zero_demand_intervals(
    daily_demand: pd.Series,
    *,
    product: object,
) -> list[dict[str, object]]:
    """Return continuous zero-demand intervals for one product."""

    if daily_demand.empty:
        return []

    full_date_range = pd.date_range(
        start=daily_demand.index.min(),
        end=daily_demand.index.max(),
    )
    daily_demand = daily_demand.reindex(full_date_range, fill_value=0)
    zero_demand_mask = daily_demand == 0

    padded_mask = pd.concat(
        [
            pd.Series(
                [False],
                index=[daily_demand.index.min() - pd.Timedelta(days=1)],
            ),
            zero_demand_mask,
            pd.Series(
                [False],
                index=[daily_demand.index.max() + pd.Timedelta(days=1)],
            ),
        ]
    )
    changes = padded_mask.astype(int).diff()
    starts = changes.index[changes == 1].tolist()
    ends = changes.index[changes == -1].tolist()

    intervals = []
    for start_date, end_date in zip(starts, ends):
        final_date = end_date - pd.Timedelta(days=1)
        if start_date <= final_date:
            intervals.append(
                {
                    "Producto": product,
                    "Fecha_Inicio_Sin_Inventario": start_date.strftime("%Y-%m-%d"),
                    "Fecha_Fin_Sin_Inventario": final_date.strftime("%Y-%m-%d"),
                }
            )
    return intervals


def find_zero_demand_periods(
    frame: pd.DataFrame,
    *,
    products: Iterable[object] | None = None,
    product_column: str = "Producto",
    date_column: str = "FECHA",
    facturado_column: str = "Facturado",
    backorder_column: str = "BackOrder",
) -> pd.DataFrame:
    """Find continuous periods with zero observed demand per product.

    This preserves the notebook's definition: missing dates inside each
    product's observed date range are reindexed as zero demand.
    """

    data = prepare_temporal_frame(
        frame,
        date_column=date_column,
        numeric_columns=(facturado_column, backorder_column),
        drop_invalid_dates=True,
    )
    data[facturado_column] = data[facturado_column].fillna(0)
    data[backorder_column] = data[backorder_column].fillna(0)
    data = add_observed_demand(
        data,
        facturado_column=facturado_column,
        backorder_column=backorder_column,
    )

    if products is not None:
        data = data.loc[data[product_column].isin(products)].copy()

    periods: list[dict[str, object]] = []
    for product, product_data in data.groupby(product_column, sort=False):
        daily_demand = product_data.groupby(date_column)["demanda_observada"].sum()
        periods.extend(_zero_demand_intervals(daily_demand, product=product))

    return pd.DataFrame(
        periods,
        columns=[
            "Producto",
            "Fecha_Inicio_Sin_Inventario",
            "Fecha_Fin_Sin_Inventario",
        ],
    )


def group_department(department: object) -> str:
    """Apply the department grouping used by the notebook."""

    normalized = str(department).upper()
    if "BOGOTA" in normalized:
        return "Bogota D.C."
    if "CUNDINAMARCA" in normalized:
        return "CUNDINAMARCA"
    return "RESTO DE DEPARTAMENTOS"
