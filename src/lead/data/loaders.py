"""Input readers for L.E.A.D. datasets."""

from __future__ import annotations

from pathlib import Path
from typing import Literal

import pandas as pd

from .schema import SALES_COLUMNS, validate_required_columns
from .validation import ensure_file_exists


BadLinesPolicy = Literal["error", "warn", "skip"]


def load_sales_transactions(
    path: str | Path,
    *,
    sep: str = ";",
    on_bad_lines: BadLinesPolicy = "skip",
    validate_schema: bool = True,
) -> pd.DataFrame:
    """Load the raw transaction dataset used by the EDA notebook.

    The function intentionally does not clean or cast columns. Those operations
    belong to the cleaning stage and should remain explicit in the pipeline.
    The defaults preserve the notebook's CSV options and Colab behavior while
    accepting a local or configured filesystem path.
    """

    input_path = ensure_file_exists(path)

    data = pd.read_csv(
        input_path,
        sep=sep,
        on_bad_lines=on_bad_lines,
    )

    if validate_schema:
        validate_required_columns(data.columns, required=SALES_COLUMNS)

    return data
