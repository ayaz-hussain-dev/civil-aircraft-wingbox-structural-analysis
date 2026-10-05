"""Core engineering calculations used by the wing-box analysis.

The functions in this module are intentionally small and independent of ANSYS.
They can therefore be unit-tested and reused when additional FEA cases are added.
"""

from __future__ import annotations

from math import exp, sqrt
from typing import Iterable, Mapping


STANDARD_GRAVITY_M_S2 = 9.80665
AIR_GAS_CONSTANT_J_KG_K = 287.05287
AIR_HEAT_CAPACITY_RATIO = 1.4
SEA_LEVEL_TEMPERATURE_K = 288.15
SEA_LEVEL_PRESSURE_PA = 101_325.0
TROPOSPHERE_LAPSE_RATE_K_M = -0.0065
TROPOPAUSE_ALTITUDE_M = 11_000.0


def isa_atmosphere(altitude_m: float) -> dict[str, float]:
    """Return ISA temperature, pressure, density, and speed of sound.

    The implementation covers the troposphere and the isothermal layer from
    11 km to 20 km, which includes the project's 37,000 ft cruise condition.
    """

    if not 0.0 <= altitude_m <= 20_000.0:
        raise ValueError("altitude_m must be between 0 and 20,000 m")

    if altitude_m <= TROPOPAUSE_ALTITUDE_M:
        temperature_k = (
            SEA_LEVEL_TEMPERATURE_K
            + TROPOSPHERE_LAPSE_RATE_K_M * altitude_m
        )
        pressure_pa = SEA_LEVEL_PRESSURE_PA * (
            temperature_k / SEA_LEVEL_TEMPERATURE_K
        ) ** (
            -STANDARD_GRAVITY_M_S2
            / (TROPOSPHERE_LAPSE_RATE_K_M * AIR_GAS_CONSTANT_J_KG_K)
        )
    else:
        temperature_k = (
            SEA_LEVEL_TEMPERATURE_K
            + TROPOSPHERE_LAPSE_RATE_K_M * TROPOPAUSE_ALTITUDE_M
        )
        pressure_at_11km_pa = SEA_LEVEL_PRESSURE_PA * (
            temperature_k / SEA_LEVEL_TEMPERATURE_K
        ) ** (
            -STANDARD_GRAVITY_M_S2
            / (TROPOSPHERE_LAPSE_RATE_K_M * AIR_GAS_CONSTANT_J_KG_K)
        )
        pressure_pa = pressure_at_11km_pa * exp(
            -STANDARD_GRAVITY_M_S2
            * (altitude_m - TROPOPAUSE_ALTITUDE_M)
            / (AIR_GAS_CONSTANT_J_KG_K * temperature_k)
        )

    density_kg_m3 = pressure_pa / (AIR_GAS_CONSTANT_J_KG_K * temperature_k)
    speed_of_sound_m_s = sqrt(
        AIR_HEAT_CAPACITY_RATIO * AIR_GAS_CONSTANT_J_KG_K * temperature_k
    )
    return {
        "temperature_k": temperature_k,
        "pressure_pa": pressure_pa,
        "density_kg_m3": density_kg_m3,
        "speed_of_sound_m_s": speed_of_sound_m_s,
    }


def flight_condition(
    *,
    altitude_m: float,
    mach: float,
    reference_area_m2: float,
    lift_coefficient: float,
) -> dict[str, float]:
    """Calculate atmospheric and aerodynamic reference quantities."""

    if mach <= 0.0:
        raise ValueError("mach must be positive")
    if reference_area_m2 <= 0.0:
        raise ValueError("reference_area_m2 must be positive")

    atmosphere = isa_atmosphere(altitude_m)
    true_airspeed_m_s = mach * atmosphere["speed_of_sound_m_s"]
    dynamic_pressure_pa = (
        0.5 * atmosphere["density_kg_m3"] * true_airspeed_m_s**2
    )
    full_aircraft_lift_n = (
        dynamic_pressure_pa * reference_area_m2 * lift_coefficient
    )
    return {
        "altitude_m": altitude_m,
        "mach": mach,
        **atmosphere,
        "true_airspeed_m_s": true_airspeed_m_s,
        "dynamic_pressure_pa": dynamic_pressure_pa,
        "full_aircraft_lift_n": full_aircraft_lift_n,
        "half_aircraft_lift_n": 0.5 * full_aircraft_lift_n,
    }


def relative_difference_percent(reference: float, comparison: float) -> float:
    """Return absolute difference as a percentage of ``reference``."""

    if reference == 0.0:
        raise ValueError("reference must be non-zero")
    return abs(comparison - reference) / abs(reference) * 100.0


def percent_change(baseline: float, candidate: float) -> float:
    """Return signed percentage change from baseline to candidate."""

    if baseline == 0.0:
        raise ValueError("baseline must be non-zero")
    return (candidate - baseline) / abs(baseline) * 100.0


def force_balance(loads: Iterable[Mapping[str, float]]) -> float:
    """Sum signed vertical forces from a sequence of load records."""

    return sum(float(load["force_n"]) for load in loads)


def root_resultants(
    loads: Iterable[Mapping[str, float]],
) -> dict[str, float]:
    """Calculate root shear, bending moment, and torsion for discrete loads.

    Each record must contain ``force_n`` and may contain ``span_m``,
    ``chord_arm_m``, and ``applied_torque_nm``. This helper is ready for a
    future exported nodal-load table without tying the package to one solver.
    """

    shear_n = 0.0
    bending_moment_nm = 0.0
    torsion_nm = 0.0
    for load in loads:
        force_n = float(load["force_n"])
        span_m = float(load.get("span_m", 0.0))
        chord_arm_m = float(load.get("chord_arm_m", 0.0))
        applied_torque_nm = float(load.get("applied_torque_nm", 0.0))
        shear_n += force_n
        bending_moment_nm += force_n * span_m
        torsion_nm += force_n * chord_arm_m + applied_torque_nm
    return {
        "root_shear_n": shear_n,
        "root_bending_moment_nm": bending_moment_nm,
        "root_torsion_nm": torsion_nm,
    }


def factor_of_safety(allowable: float, demand: float) -> float:
    """Return an allowable-to-demand factor of safety."""

    if demand <= 0.0:
        raise ValueError("demand must be positive")
    return allowable / demand
