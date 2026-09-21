"""Product selection rules extracted from the product-selection notebook."""

from __future__ import annotations

from collections.abc import Iterable

import numpy as np
import pandas as pd

from .temporal import add_observed_demand


DEFAULT_BRANDS = ("CORONEL", "KAUDAL", "VIGOR", "LOGIPAINT")


def filter_product_origin(
    frame: pd.DataFrame,
    *,
    imported: bool,
    flag_column: str = "FlagImportado",
) -> pd.DataFrame:
    """Filter imported or national products using ``FlagImportado``."""

    expected_flag = 1 if imported else 0
    return frame.loc[frame[flag_column] == expected_flag].copy()


def calculate_pareto(
    frame: pd.DataFrame,
    *,
    product_column: str = "Producto",
    value_column: str = "VentaTotal",
    threshold: float = 80.0,
) -> tuple[pd.DataFrame, pd.DataFrame]:
    """Calculate product sales participation and the Pareto subset.

    Returns the complete ordered table and the rows whose cumulative share is
    at most ``threshold``, matching the notebook's ``<= 80`` filter.
    """

    sales = (
        frame.groupby(product_column, observed=False)[value_column]
        .sum()
        .sort_values(ascending=False)
    )
    pareto = sales.to_frame(name=value_column)
    total = pareto[value_column].sum()
    pareto["PorcentajeVentaTotal"] = pareto[value_column] / total * 100
    pareto["PorcentajeAcumulado"] = pareto["PorcentajeVentaTotal"].cumsum()
    selected = pareto.loc[
        pareto["PorcentajeAcumulado"] <= threshold
    ].copy()
    return pareto, selected


def classify_abc(cumulative_share: float) -> str:
    """Apply the notebook's ABC thresholds."""

    if cumulative_share <= 80:
        return "A"
    if cumulative_share <= 95:
        return "B"
    return "C"


def classify_xyz(coefficient_of_variation: float) -> str:
    """Apply the notebook's XYZ thresholds."""

    if pd.isna(coefficient_of_variation):
        return "Z"
    if coefficient_of_variation <= 0.5:
        return "X"
    if coefficient_of_variation <= 1.0:
        return "Y"
    return "Z"


def classify_abc_xyz(
    frame: pd.DataFrame,
    *,
    product_column: str = "Producto",
    date_column: str = "FECHA",
    value_column: str = "VentaTotal",
    facturado_column: str = "Facturado",
    backorder_column: str = "BackOrder",
) -> pd.DataFrame:
    """Build the ABC-XYZ summary used by the notebook.

    Weekly demand includes zero-demand weeks between the first and last valid
    dates, preserving the notebook's treatment of intermittency.
    """

    data = add_observed_demand(
        frame,
        facturado_column=facturado_column,
        backorder_column=backorder_column,
    )
    data[date_column] = pd.to_datetime(data[date_column], errors="coerce")

    sales = (
        data.groupby(product_column, observed=False)[value_column]
        .sum()
        .sort_values(ascending=False)
    )
    sales_pct = sales / sales.sum() * 100
    cumulative_sales_pct = sales_pct.cumsum()
    abc = cumulative_sales_pct.apply(classify_abc)

    dated_data = data.dropna(subset=[date_column]).copy()
    full_weeks = pd.date_range(
        dated_data[date_column].min(),
        dated_data[date_column].max(),
        freq="W",
    )
    weekly = (
        dated_data.groupby(
            [pd.Grouper(key=date_column, freq="W"), product_column],
            observed=False,
        )["demanda_observada"]
        .sum()
        .unstack(fill_value=0)
    )
    weekly = weekly.reindex(full_weeks, fill_value=0)

    mean_weekly = weekly.mean()
    standard_deviation_weekly = weekly.std()
    coefficient_of_variation = (
        standard_deviation_weekly / mean_weekly
    ).replace([np.inf, -np.inf], np.nan)
    xyz = coefficient_of_variation.apply(classify_xyz)

    summary = pd.DataFrame(
        {
            "VentaTotal": sales,
            "PctVenta": sales_pct,
            "PctAcum": cumulative_sales_pct,
            "ABC": abc,
            "DemandaSemanalProm": mean_weekly,
            "CV": coefficient_of_variation,
            "XYZ": xyz,
        }
    ).dropna(subset=["ABC"])
    summary["Clase"] = summary["ABC"] + summary["XYZ"]
    return summary.sort_values("VentaTotal", ascending=False)


def select_ax_pareto(
    summary: pd.DataFrame,
    pareto_products: pd.DataFrame,
    *,
    top_n: int = 20,
) -> pd.DataFrame:
    """Select the first ``top_n`` products that are both AX and Pareto."""

    ax_products = summary.loc[summary["Clase"] == "AX"]
    selected = ax_products.loc[
        ax_products.index.isin(pareto_products.index)
    ]
    return selected.head(top_n).copy()


def select_ax_rows(
    frame: pd.DataFrame,
    *,
    imported: bool,
    top_n: int = 20,
    product_column: str = "Producto",
) -> pd.DataFrame:
    """Return all source rows for the selected AX Pareto products."""

    origin_frame = filter_product_origin(frame, imported=imported)
    _, pareto_products = calculate_pareto(
        origin_frame,
        product_column=product_column,
    )
    summary = classify_abc_xyz(
        origin_frame,
        product_column=product_column,
    )
    selected = select_ax_pareto(summary, pareto_products, top_n=top_n)
    classification = (
        selected.drop(columns=["VentaTotal"], errors="ignore")
        .rename_axis(product_column)
        .reset_index()
    )
    selected_rows = origin_frame.loc[
        origin_frame[product_column].isin(selected.index)
    ].copy()
    return selected_rows.merge(
        classification,
        on=product_column,
        how="left",
        validate="many_to_one",
    )


def assign_brand(
    product_name: object,
    brands: Iterable[str] = DEFAULT_BRANDS,
) -> str:
    """Assign a product to the first matching brand, or ``OTROS``."""

    normalized_name = str(product_name).lower()
    for brand in brands:
        if brand.lower() in normalized_name:
            return brand
    return "OTROS"


def brand_proportions(
    products: Iterable[object],
    brands: Iterable[str] = DEFAULT_BRANDS,
) -> pd.DataFrame:
    """Count and calculate proportions by product-name brand matching."""

    products = list(products)
    brands = tuple(brands)
    counts = {brand: 0 for brand in brands}
    counts["OTROS"] = 0

    for product in products:
        brand = assign_brand(product, brands)
        counts[brand] += 1

    result = pd.DataFrame(
        list(counts.items()),
        columns=["Línea", "Cantidad de Productos"],
    )
    total = len(list(products))
    result["Proporción (%)"] = (
        result["Cantidad de Productos"] / total * 100
        if total
        else 0.0
    )
    return result.sort_values(
        "Proporción (%)",
        ascending=False,
    ).reset_index(drop=True)
