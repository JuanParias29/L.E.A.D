"""Small validation helpers for data ingestion."""

from __future__ import annotations

from pathlib import Path


def ensure_file_exists(path: str | Path) -> Path:
    """Return a file path or raise a clear input error."""

    input_path = Path(path)
    if not input_path.is_file():
        raise FileNotFoundError(f"No existe el archivo de entrada: {input_path}")
    return input_path
