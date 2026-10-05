from __future__ import annotations

import unittest
from pathlib import Path

from wingbox_analysis.analysis import analyse_project
from wingbox_analysis.calculations import (
    flight_condition,
    force_balance,
    percent_change,
    relative_difference_percent,
    root_resultants,
)


ROOT = Path(__file__).resolve().parents[1]


class CalculationTests(unittest.TestCase):
    def test_cruise_condition_matches_reference(self) -> None:
        result = flight_condition(
            altitude_m=37_000 * 0.3048,
            mach=0.85,
            reference_area_m2=383.74,
            lift_coefficient=0.5,
        )
        self.assertAlmostEqual(result["temperature_k"], 216.65, places=8)
        self.assertAlmostEqual(result["pressure_pa"], 21662.7083125, places=5)
        self.assertAlmostEqual(result["dynamic_pressure_pa"], 10955.9147290, places=5)
        self.assertAlmostEqual(result["half_aircraft_lift_n"], 1051055.679531, places=5)

    def test_percentage_helpers(self) -> None:
        self.assertAlmostEqual(relative_difference_percent(100.0, 104.0), 4.0)
        self.assertAlmostEqual(percent_change(100.0, 89.0), -11.0)

    def test_force_balance(self) -> None:
        loads = [{"force_n": 100.0}, {"force_n": -25.0}, {"force_n": -5.0}]
        self.assertEqual(force_balance(loads), 70.0)

    def test_discrete_root_resultants(self) -> None:
        loads = [
            {"force_n": 100.0, "span_m": 2.0, "chord_arm_m": 0.5},
            {"force_n": -20.0, "span_m": 1.0, "applied_torque_nm": 3.0},
        ]
        result = root_resultants(loads)
        self.assertEqual(result["root_shear_n"], 80.0)
        self.assertEqual(result["root_bending_moment_nm"], 180.0)
        self.assertEqual(result["root_torsion_nm"], 53.0)

    def test_project_regression_values(self) -> None:
        result = analyse_project(ROOT / "data")
        self.assertAlmostEqual(
            result["load_summary"]["net_vertical_load_n"],
            632210.1084986424,
            places=6,
        )
        self.assertAlmostEqual(
            result["correlation"]["deformation_difference_percent"],
            4.675465993,
            places=6,
        )
        self.assertAlmostEqual(
            result["sizing"]["actual_mass_reduction_percent"],
            11.138432292,
            places=6,
        )
        self.assertEqual(result["gates"]["deformation_correlation"], "PASS")
        self.assertTrue(result["gates"]["mesh_convergence"].startswith("PENDING"))


if __name__ == "__main__":
    unittest.main()
