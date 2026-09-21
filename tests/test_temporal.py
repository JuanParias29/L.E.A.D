"""Focused tests for the fourth refactoring stage."""

from __future__ import annotations

import unittest

import pandas as pd

from src.lead.data.temporal import (
    add_observed_demand,
    aggregate_weekly_by_group,
    aggregate_weekly_demand,
    find_zero_demand_periods,
    group_department,
)


class TemporalPreprocessingTests(unittest.TestCase):
    def test_creates_observed_demand_and_weekly_aggregation(self) -> None:
        frame = pd.DataFrame(
            {
                "FECHA": ["2025-01-01", "2025-01-03"],
                "Producto": ["P1", "P1"],
                "Facturado": [2, 3],
                "BackOrder": [1, 0],
            }
        )

        prepared = add_observed_demand(frame)
        weekly = aggregate_weekly_demand(
            prepared,
            value_columns=["Facturado", "BackOrder", "demanda_observada"],
        )

        self.assertEqual(prepared["demanda_observada"].tolist(), [3, 3])
        self.assertEqual(weekly.iloc[0]["Facturado"], 5)
        self.assertEqual(weekly.iloc[0]["BackOrder"], 1)
        self.assertEqual(weekly.iloc[0]["demanda_observada"], 6)

    def test_finds_continuous_zero_demand_period(self) -> None:
        frame = pd.DataFrame(
            {
                "FECHA": ["2025-01-01", "2025-01-05", "2025-01-06"],
                "Producto": ["P1", "P1", "P1"],
                "Facturado": [1, 0, 2],
                "BackOrder": [0, 0, 0],
            }
        )

        periods = find_zero_demand_periods(frame, products=["P1"])

        self.assertEqual(len(periods), 1)
        self.assertEqual(periods.iloc[0]["Fecha_Inicio_Sin_Inventario"], "2025-01-02")
        self.assertEqual(periods.iloc[0]["Fecha_Fin_Sin_Inventario"], "2025-01-05")

    def test_aggregates_by_group_and_groups_departments(self) -> None:
        frame = pd.DataFrame(
            {
                "FECHA": ["2025-01-01", "2025-01-02"],
                "Departamento": ["BOGOTA D.C.", "CUNDINAMARCA"],
                "demanda_observada": [2, 3],
            }
        )

        weekly = aggregate_weekly_by_group(
            frame,
            group_column="Departamento",
        )

        self.assertEqual(weekly.iloc[0]["BOGOTA D.C."], 2)
        self.assertEqual(weekly.iloc[0]["CUNDINAMARCA"], 3)
        self.assertEqual(group_department("Bogota Norte"), "Bogota D.C.")
        self.assertEqual(group_department("Cundinamarca"), "CUNDINAMARCA")
        self.assertEqual(group_department("ATLANTICO"), "RESTO DE DEPARTAMENTOS")


if __name__ == "__main__":
    unittest.main()
