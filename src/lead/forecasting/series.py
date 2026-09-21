"""Preparation of weekly product series for forecasting."""

from __future__ import annotations

from collections.abc import Iterable
from dataclasses import dataclass

import pandas as pd


DEFAULT_EVENTS = (
    (2025, 1, "Vacaciones"),
    (2024, 13, "SemanaSanta"),
    (2025, 16, "SemanaSanta"),
    (2025, 20, "RuedaNegocios"),
    (2024, 37, "Feria"),
    (2025, 39, "Feria"),
)


@dataclass(frozen=True)
class ForecastingSplit:
    """Chronological data and event features for one product forecast."""

    train: pd.DataFrame
    test: pd.DataFrame
    y_train: pd.Series
    y_test: pd.Series
    X_train: pd.DataFrame
    X_test: pd.DataFrame
    feature_columns: tuple[str, ...]


def _event_dates(events: Iterable[tuple[int, int, str]]) -> list[tuple[pd.Timestamp, str]]:
    return [
        (
            pd.to_datetime(f"{year}-W{week:02d}-1", format="%G-W%V-%u"),
            name,
        )
        for year, week, name in events
    ]


def prepare_product_weekly_series(
    product_frame: pd.DataFrame,
    stockouts: pd.DataFrame,
    *,
    events: Iterable[tuple[int, int, str]] = DEFAULT_EVENTS,
    excluded_weeks: tuple[int, ...] = (52, 53),
    minimum_weeks: int = 70,
) -> pd.DataFrame:
    """Build the weekly forecasting frame used by the notebook's model loop."""

    required_product_columns = {"FECHA", "Facturado", "BackOrder", "VlrUnitario"}
    missing_product = required_product_columns.difference(product_frame.columns)
    if missing_product:
        raise ValueError(
            "Faltan columnas del producto: " + ", ".join(sorted(missing_product))
        )

    required_stockout_columns = {"IDProductos", "FechaInicial", "FechaFinal"}
    missing_stockout = required_stockout_columns.difference(stockouts.columns)
    if missing_stockout:
        raise ValueError(
            "Faltan columnas de quiebres: " + ", ".join(sorted(missing_stockout))
        )

    data = product_frame.copy()
    data["FECHA"] = pd.to_datetime(data["FECHA"], errors="coerce")
    data = data.dropna(subset=["FECHA"]).set_index("FECHA").sort_index()
    weekly = data.resample("W-MON").agg(
        {
            "Facturado": "sum",
            "BackOrder": "sum",
            "VlrUnitario": "mean",
        }
    )
    weekly["demanda_observada"] = weekly["Facturado"] + weekly["BackOrder"]
    weekly["VlrUnitario"] = weekly["VlrUnitario"].interpolate().ffill().bfill()

    event_dates = _event_dates(events)
    event_names = list(dict.fromkeys(name for _, name in event_dates))
    for name in event_names:
        weekly[f"Evento_{name}"] = 0.0
    for date, name in event_dates:
        if date in weekly.index:
            weekly.loc[date, f"Evento_{name}"] = 1.0

    weekly["Evento_QuiebreInventario"] = 0.0
    product_id = str(product_frame["IDProducto"].dropna().iloc[0]) if "IDProducto" in product_frame else None
    product_stockouts = stockouts
    if product_id is not None:
        product_stockouts = stockouts.loc[
            stockouts["IDProductos"].astype(str) == product_id
        ].copy()
    product_stockouts["FechaInicial"] = pd.to_datetime(
        product_stockouts["FechaInicial"], errors="coerce"
    )
    product_stockouts["FechaFinal"] = pd.to_datetime(
        product_stockouts["FechaFinal"], errors="coerce"
    )

    for week_end in weekly.index:
        if week_end.isocalendar().week in excluded_weeks:
            continue
        week_start = week_end - pd.Timedelta(weeks=1)
        overlaps = (
            (product_stockouts["FechaInicial"] <= week_end)
            & (product_stockouts["FechaFinal"] > week_start)
        )
        if overlaps.any():
            weekly.loc[week_end, "Evento_QuiebreInventario"] = 1.0

    if len(weekly) < minimum_weeks:
        raise ValueError(f"Solo tiene {len(weekly)} semanas")

    weekly["Precio_lag1"] = weekly["VlrUnitario"].shift(1)
    return weekly.dropna(subset=["Precio_lag1"])


def prepare_forecasting_split(
    weekly: pd.DataFrame,
    cutoff: pd.Timestamp,
    *,
    target_column: str = "demanda_real",
    feature_prefix: str = "Evento_",
    minimum_train: int = 40,
    minimum_test: int = 8,
) -> ForecastingSplit:
    """Split a weekly product frame and select variable event features."""

    if target_column not in weekly.columns:
        raise ValueError(f"Falta la columna objetivo: {target_column}")
    if not isinstance(weekly.index, pd.DatetimeIndex):
        raise TypeError("La serie semanal debe tener un DatetimeIndex")

    data = weekly.sort_index().copy()
    cutoff = pd.Timestamp(cutoff)
    train = data.loc[data.index <= cutoff]
    test = data.loc[data.index > cutoff]
    if len(train) < minimum_train or len(test) < minimum_test:
        raise ValueError(
            "No tiene suficientes datos de entrenamiento o prueba "
            f"({len(train)} y {len(test)})"
        )

    feature_columns = tuple(
        column
        for column in data.columns
        if column.startswith(feature_prefix)
        and train[column].nunique(dropna=False) > 1
    )
    X_train = train.loc[:, feature_columns].astype(float)
    X_test = test.loc[:, feature_columns].astype(float)
    return ForecastingSplit(
        train=train,
        test=test,
        y_train=train[target_column].astype(float),
        y_test=test[target_column].astype(float),
        X_train=X_train,
        X_test=X_test,
        feature_columns=feature_columns,
    )


def standardize_lagged_price(
    weekly: pd.DataFrame,
    cutoff: pd.Timestamp,
    *,
    input_column: str = "Precio_lag1",
    output_column: str = "Precio_std",
) -> tuple[pd.DataFrame, float, float]:
    """Standardize lagged price using training-period statistics only."""

    if input_column not in weekly.columns:
        raise ValueError(f"Falta la columna de precio: {input_column}")
    if not isinstance(weekly.index, pd.DatetimeIndex):
        raise TypeError("La serie semanal debe tener un DatetimeIndex")

    data = weekly.sort_index().copy()
    training = data.loc[data.index <= pd.Timestamp(cutoff), input_column]
    mean = float(training.mean())
    standard_deviation = float(training.std())
    if pd.isna(standard_deviation) or standard_deviation <= 0:
        raise ValueError("El precio no cambia durante el entrenamiento.")

    data[output_column] = (data[input_column] - mean) / standard_deviation
    return data, mean, standard_deviation