"""Data loading and project-level wing-box analysis."""

from __future__ import annotations

import csv
import json
from pathlib import Path
from typing import Any

from .calculations import (
    factor_of_safety,
    flight_condition,
    force_balance,
    percent_change,
    relative_difference_percent,
)


def _read_csv(path: Path) -> list[dict[str, str]]:
    with path.open("r", encoding="utf-8-sig", newline="") as handle:
        return list(csv.DictReader(handle))


def _as_float(record: dict[str, str], key: str) -> float:
    try:
        return float(record[key])
    except (KeyError, TypeError, ValueError) as exc:
        raise ValueError(f"Invalid numeric value for {key!r}: {record}") from exc


def _as_int(record: dict[str, str], key: str) -> int:
    return int(_as_float(record, key))


def _load_inputs(data_dir: Path) -> dict[str, Any]:
    with (data_dir / "project_inputs.json").open("r", encoding="utf-8") as handle:
        config = json.load(handle)

    loads = []
    for row in _read_csv(data_dir / "load_components.csv"):
        loads.append(
            {
                "component": row["component"],
                "force_n": _as_float(row, "force_n"),
                "source_count": _as_int(row, "source_count"),
                "note": row["note"],
            }
        )

    fea_cases: dict[str, dict[str, Any]] = {}
    for row in _read_csv(data_dir / "fea_results.csv"):
        case = row["case"]
        fea_cases[case] = {
            "case": case,
            "description": row["description"],
            "mass_kg": _as_float(row, "mass_kg"),
            "max_total_deformation_m": _as_float(
                row, "max_total_deformation_m"
            ),
            "max_von_mises_stress_pa": _as_float(
                row, "max_von_mises_stress_pa"
            ),
            "buckling_mode_1_factor": _as_float(
                row, "buckling_mode_1_factor"
            ),
            "nodes": _as_int(row, "nodes"),
            "elements": _as_int(row, "elements"),
        }

    mesh_cases = []
    for row in _read_csv(data_dir / "mesh_results.csv"):
        mesh_cases.append(
            {
                "mesh": row["mesh"],
                "nodes": _as_int(row, "nodes"),
                "elements": _as_int(row, "elements"),
                "max_total_deformation_m": _as_float(
                    row, "max_total_deformation_m"
                ),
                "max_von_mises_stress_pa": _as_float(
                    row, "max_von_mises_stress_pa"
                ),
            }
        )

    spanwise = []
    for row in _read_csv(data_dir / "spanwise_handcalc.csv"):
        spanwise.append(
            {
                "eta": _as_float(row, "eta"),
                "total_deflection_m": _as_float(row, "total_deflection_m"),
                "bending_moment_mnm": _as_float(row, "bending_moment_mnm"),
            }
        )

    return {
        "config": config,
        "loads": loads,
        "fea_cases": fea_cases,
        "mesh_cases": mesh_cases,
        "spanwise": spanwise,
    }


def _gate(value: float, limit: float, *, lower_is_better: bool) -> str:
    passed = value <= limit if lower_is_better else value >= limit
    return "PASS" if passed else "REVIEW"


def analyse_project(data_dir: str | Path) -> dict[str, Any]:
    """Run all automated calculations and comparisons for the project."""

    data_path = Path(data_dir)
    inputs = _load_inputs(data_path)
    config = inputs["config"]
    checks = config["checks"]
    analytical = config["analytical_results"]
    material = config["material"]

    flight = config["flight_condition"]
    altitude_m = float(flight["altitude_ft"]) * 0.3048
    flight_results = flight_condition(
        altitude_m=altitude_m,
        mach=float(flight["mach"]),
        reference_area_m2=float(flight["reference_area_m2"]),
        lift_coefficient=float(flight["lift_coefficient"]),
    )

    aerodynamic_force_n = next(
        item["force_n"]
        for item in inputs["loads"]
        if item["component"] == "aerodynamic"
    )
    lift_difference_percent = relative_difference_percent(
        flight_results["half_aircraft_lift_n"], aerodynamic_force_n
    )
    net_vertical_load_n = force_balance(inputs["loads"])

    try:
        baseline = inputs["fea_cases"]["baseline"]
        reduced = inputs["fea_cases"]["reduced_thickness"]
    except KeyError as exc:
        raise ValueError(
            "fea_results.csv must contain baseline and reduced_thickness cases"
        ) from exc

    deformation_difference_percent = relative_difference_percent(
        float(analytical["tip_deformation_m"]),
        baseline["max_total_deformation_m"],
    )
    nominal_peak_stress_difference_percent = relative_difference_percent(
        float(analytical["peak_nominal_vm_stress_pa"]),
        baseline["max_von_mises_stress_pa"],
    )

    target_mass_reduction_percent = float(
        config["sizing"]["target_mass_reduction_percent"]
    )
    target_mass_kg = baseline["mass_kg"] * (
        1.0 - target_mass_reduction_percent / 100.0
    )
    sizing_changes = {
        "mass_percent": percent_change(baseline["mass_kg"], reduced["mass_kg"]),
        "deformation_percent": percent_change(
            baseline["max_total_deformation_m"],
            reduced["max_total_deformation_m"],
        ),
        "stress_percent": percent_change(
            baseline["max_von_mises_stress_pa"],
            reduced["max_von_mises_stress_pa"],
        ),
        "buckling_factor_percent": percent_change(
            baseline["buckling_mode_1_factor"],
            reduced["buckling_mode_1_factor"],
        ),
    }

    baseline_yield_fos = factor_of_safety(
        float(material["yield_strength_pa"]),
        baseline["max_von_mises_stress_pa"],
    )
    reduced_yield_fos = factor_of_safety(
        float(material["yield_strength_pa"]),
        reduced["max_von_mises_stress_pa"],
    )

    mesh_steps: list[dict[str, Any]] = []
    for index, mesh in enumerate(inputs["mesh_cases"]):
        row = dict(mesh)
        if index == 0:
            row["deformation_change_from_previous_percent"] = None
            row["stress_change_from_previous_percent"] = None
        else:
            previous = inputs["mesh_cases"][index - 1]
            row["deformation_change_from_previous_percent"] = percent_change(
                previous["max_total_deformation_m"],
                mesh["max_total_deformation_m"],
            )
            row["stress_change_from_previous_percent"] = percent_change(
                previous["max_von_mises_stress_pa"],
                mesh["max_von_mises_stress_pa"],
            )
        mesh_steps.append(row)

    if len(mesh_steps) < 3:
        mesh_status = "PENDING — add a third mesh before claiming convergence"
    else:
        latest = mesh_steps[-1]
        latest_max_change = max(
            abs(latest["deformation_change_from_previous_percent"]),
            abs(latest["stress_change_from_previous_percent"]),
        )
        mesh_status = _gate(
            latest_max_change,
            float(checks["mesh_latest_step_target_percent"]),
            lower_is_better=True,
        )

    gates = {
        "lift_equation_check": _gate(
            lift_difference_percent,
            float(checks["lift_difference_limit_percent"]),
            lower_is_better=True,
        ),
        "deformation_correlation": _gate(
            deformation_difference_percent,
            float(checks["structural_correlation_limit_percent"]),
            lower_is_better=True,
        ),
        "baseline_deflection": _gate(
            baseline["max_total_deformation_m"],
            float(checks["deflection_screen_m"]),
            lower_is_better=True,
        ),
        "reduced_deflection": _gate(
            reduced["max_total_deformation_m"],
            float(checks["deflection_screen_m"]),
            lower_is_better=True,
        ),
        "baseline_yield": _gate(baseline_yield_fos, 1.0, lower_is_better=False),
        "reduced_yield": _gate(reduced_yield_fos, 1.0, lower_is_better=False),
        "baseline_buckling": _gate(
            baseline["buckling_mode_1_factor"],
            float(checks["minimum_buckling_factor"]),
            lower_is_better=False,
        ),
        "reduced_buckling": _gate(
            reduced["buckling_mode_1_factor"],
            float(checks["minimum_buckling_factor"]),
            lower_is_better=False,
        ),
        "mesh_convergence": mesh_status,
    }

    calculated_root_load_n = float(analytical["root_vertical_load_n"])
    load_balance_error_n = net_vertical_load_n - calculated_root_load_n

    return {
        "project": config["project"],
        "flight_condition": flight_results,
        "loads": inputs["loads"],
        "load_summary": {
            "bdf_aerodynamic_half_wing_force_n": aerodynamic_force_n,
            "lift_difference_percent": lift_difference_percent,
            "net_vertical_load_n": net_vertical_load_n,
            "reference_root_vertical_load_n": calculated_root_load_n,
            "load_balance_error_n": load_balance_error_n,
            "root_bending_moment_nm": float(
                analytical["root_bending_moment_nm"]
            ),
            "root_torsion_nm": float(analytical["root_torsion_nm"]),
        },
        "correlation": {
            "analytical_tip_deformation_m": float(
                analytical["tip_deformation_m"]
            ),
            "fea_tip_deformation_m": baseline["max_total_deformation_m"],
            "deformation_difference_percent": deformation_difference_percent,
            "correlation_limit_percent": float(
                checks["structural_correlation_limit_percent"]
            ),
            "analytical_peak_nominal_vm_stress_pa": float(
                analytical["peak_nominal_vm_stress_pa"]
            ),
            "fea_peak_vm_stress_pa": baseline["max_von_mises_stress_pa"],
            "nominal_peak_stress_difference_percent": (
                nominal_peak_stress_difference_percent
            ),
        },
        "fea_cases": inputs["fea_cases"],
        "mesh_steps": mesh_steps,
        "spanwise_handcalc": inputs["spanwise"],
        "sizing": {
            "target_mass_reduction_percent": target_mass_reduction_percent,
            "target_mass_kg": target_mass_kg,
            "actual_mass_reduction_percent": -sizing_changes["mass_percent"],
            "mass_saved_kg": baseline["mass_kg"] - reduced["mass_kg"],
            "changes": sizing_changes,
            "baseline_yield_fos": baseline_yield_fos,
            "reduced_yield_fos": reduced_yield_fos,
        },
        "checks": checks,
        "gates": gates,
    }
