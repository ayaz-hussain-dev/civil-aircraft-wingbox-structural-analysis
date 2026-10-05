"""CSV, Markdown, JSON, and chart generation for the CRM analysis."""

from __future__ import annotations

import csv
import json
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Iterable

import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt  # noqa: E402


NAVY = "#17365D"
BLUE = "#2F75B5"
LIGHT_BLUE = "#9DC3E6"
ORANGE = "#ED7D31"
GREEN = "#70AD47"
RED = "#C00000"
GREY = "#6B7280"


def _write_csv(path: Path, fieldnames: list[str], rows: Iterable[dict[str, Any]]) -> None:
    with path.open("w", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(rows)


def _style_axes(ax: plt.Axes) -> None:
    ax.spines["top"].set_visible(False)
    ax.spines["right"].set_visible(False)
    ax.grid(axis="y", color="#D9E2F3", linewidth=0.8, alpha=0.8)
    ax.set_axisbelow(True)


def _save_load_balance(result: dict[str, Any], path: Path) -> None:
    loads = result["loads"]
    label_map = {
        "aerodynamic": "Aerodynamic",
        "wingbox_weight": "Wing-box weight",
        "leading_trailing_edge_weight": "Leading/trailing-edge weight",
        "engine_weight": "Engine weight",
        "fuel_20_percent_weight": "20% fuel weight",
    }
    labels = [label_map.get(item["component"], item["component"]) for item in loads]
    values_kn = [item["force_n"] / 1_000.0 for item in loads]
    colors = [BLUE if value >= 0.0 else ORANGE for value in values_kn]

    fig, ax = plt.subplots(figsize=(9.2, 5.2))
    bars = ax.barh(labels, values_kn, color=colors)
    ax.axvline(0.0, color=NAVY, linewidth=1.0)
    ax.set_xlabel("Vertical force (kN)")
    ax.set_title("Half-wing load balance", loc="left", color=NAVY, weight="bold")
    ax.invert_yaxis()
    ax.grid(axis="x", color="#D9E2F3", linewidth=0.8, alpha=0.8)
    ax.spines["top"].set_visible(False)
    ax.spines["right"].set_visible(False)
    for bar, value in zip(bars, values_kn):
        if value >= 0:
            x_position, alignment, text_color = value - 15.0, "right", "white"
        elif abs(value) < 60.0:
            x_position, alignment, text_color = value - 8.0, "right", NAVY
        else:
            x_position, alignment, text_color = value / 2.0, "center", "white"
        ax.text(
            x_position,
            bar.get_y() + bar.get_height() / 2,
            f"{value:,.1f}",
            va="center",
            ha=alignment,
            color=text_color,
            fontsize=9,
            weight="bold",
        )
    fig.tight_layout()
    fig.savefig(path, dpi=180, bbox_inches="tight")
    plt.close(fig)


def _save_correlation(result: dict[str, Any], path: Path) -> None:
    correlation = result["correlation"]
    values = [
        correlation["analytical_tip_deformation_m"],
        correlation["fea_tip_deformation_m"],
    ]
    fig, ax = plt.subplots(figsize=(7.4, 5.2))
    bars = ax.bar(["Analytical", "ANSYS"], values, color=[BLUE, ORANGE], width=0.58)
    ax.axhline(
        result["checks"]["deflection_screen_m"],
        color=GREY,
        linestyle="--",
        linewidth=1.2,
        label=f'{result["checks"]["deflection_screen_m"]:.1f} m screen',
    )
    ax.set_ylabel("Maximum total deformation (m)")
    ax.set_title("Analytical–FEA deformation correlation", loc="left", color=NAVY, weight="bold")
    _style_axes(ax)
    ax.legend(frameon=False, loc="upper left")
    ax.set_ylim(0.0, max(values + [result["checks"]["deflection_screen_m"]]) * 1.18)
    for bar, value in zip(bars, values):
        ax.text(
            bar.get_x() + bar.get_width() / 2,
            value + 0.04,
            f"{value:.4f} m",
            ha="center",
            va="bottom",
            weight="bold",
        )
    ax.text(
        0.5,
        0.93,
        f'Difference: {correlation["deformation_difference_percent"]:.2f}%',
        transform=ax.transAxes,
        ha="center",
        color=NAVY,
        weight="bold",
    )
    fig.tight_layout()
    fig.savefig(path, dpi=180, bbox_inches="tight")
    plt.close(fig)


def _save_mesh_sensitivity(result: dict[str, Any], path: Path) -> None:
    mesh = result["mesh_steps"]
    elements = [row["elements"] for row in mesh]
    deformation = [row["max_total_deformation_m"] for row in mesh]
    stress_mpa = [row["max_von_mises_stress_pa"] / 1e6 for row in mesh]
    labels = [row["mesh"].title() for row in mesh]

    fig, axes = plt.subplots(1, 2, figsize=(11.4, 4.7))
    axes[0].plot(elements, deformation, color=BLUE, marker="o", linewidth=2.0)
    axes[0].set_ylabel("Maximum deformation (m)")
    axes[0].set_title("Deformation", loc="left", color=NAVY, weight="bold")
    axes[1].plot(elements, stress_mpa, color=ORANGE, marker="o", linewidth=2.0)
    axes[1].set_ylabel("Maximum von Mises stress (MPa)")
    axes[1].set_title("Stress", loc="left", color=NAVY, weight="bold")
    for ax, values in zip(axes, [deformation, stress_mpa]):
        ax.set_xscale("log")
        ax.set_xlabel("Element count (log scale)")
        _style_axes(ax)
        for x, y, label in zip(elements, values, labels):
            ax.annotate(
                f"{label}\n{x:,}",
                (x, y),
                xytext=(0, 9),
                textcoords="offset points",
                ha="center",
                fontsize=8,
            )
    fig.suptitle("Mesh sensitivity", x=0.06, ha="left", color=NAVY, weight="bold", fontsize=14)
    fig.tight_layout(rect=(0, 0, 1, 0.93))
    fig.savefig(path, dpi=180, bbox_inches="tight")
    plt.close(fig)


def _save_sizing_tradeoff(result: dict[str, Any], path: Path) -> None:
    changes = result["sizing"]["changes"]
    labels = ["Mass", "Deformation", "Stress", "Buckling factor"]
    values = [
        changes["mass_percent"],
        changes["deformation_percent"],
        changes["stress_percent"],
        changes["buckling_factor_percent"],
    ]
    colors = [GREEN, ORANGE, ORANGE, RED]
    fig, ax = plt.subplots(figsize=(9.0, 5.2))
    bars = ax.bar(labels, values, color=colors, width=0.62)
    ax.axhline(0.0, color=NAVY, linewidth=1.0)
    ax.set_ylabel("Change from baseline (%)")
    ax.set_title("Reduced-thickness sizing trade study", loc="left", color=NAVY, weight="bold")
    _style_axes(ax)
    lower = min(values) - 7
    upper = max(values) + 7
    ax.set_ylim(lower, upper)
    for bar, value in zip(bars, values):
        vertical = 0.8 if value >= 0 else -0.8
        ax.text(
            bar.get_x() + bar.get_width() / 2,
            value + vertical,
            f"{value:+.2f}%",
            ha="center",
            va="bottom" if value >= 0 else "top",
            weight="bold",
        )
    fig.tight_layout()
    fig.savefig(path, dpi=180, bbox_inches="tight")
    plt.close(fig)


def _save_spanwise_response(result: dict[str, Any], path: Path) -> None:
    rows = result["spanwise_handcalc"]
    eta = [row["eta"] for row in rows]
    deflection = [row["total_deflection_m"] for row in rows]
    moment = [row["bending_moment_mnm"] for row in rows]

    fig, axes = plt.subplots(1, 2, figsize=(11.4, 4.7))
    axes[0].plot(eta, deflection, color=BLUE, marker="o", linewidth=2.0)
    axes[0].set_ylabel("Total deflection (m)")
    axes[0].set_title("Analytical deflection", loc="left", color=NAVY, weight="bold")
    axes[1].plot(eta, moment, color=ORANGE, marker="o", linewidth=2.0)
    axes[1].set_ylabel("Bending moment (MN·m)")
    axes[1].set_title("Root-to-tip bending moment", loc="left", color=NAVY, weight="bold")
    for ax in axes:
        ax.set_xlabel("Span ratio, η")
        ax.set_xlim(0.0, 1.0)
        _style_axes(ax)
    fig.suptitle("Spanwise analytical response", x=0.06, ha="left", color=NAVY, weight="bold", fontsize=14)
    fig.tight_layout(rect=(0, 0, 1, 0.93))
    fig.savefig(path, dpi=180, bbox_inches="tight")
    plt.close(fig)


def _write_tables(result: dict[str, Any], output_dir: Path) -> None:
    flight_rows = [
        {"metric": key, "value": value}
        for key, value in result["flight_condition"].items()
    ]
    _write_csv(output_dir / "flight_condition.csv", ["metric", "value"], flight_rows)

    summary_rows = [
        {"metric": "Half-aircraft lift", "value": result["flight_condition"]["half_aircraft_lift_n"], "unit": "N"},
        {"metric": "BDF aerodynamic force", "value": result["load_summary"]["bdf_aerodynamic_half_wing_force_n"], "unit": "N"},
        {"metric": "Lift difference", "value": result["load_summary"]["lift_difference_percent"], "unit": "%"},
        {"metric": "Net root vertical load", "value": result["load_summary"]["net_vertical_load_n"], "unit": "N"},
        {"metric": "Root bending moment", "value": result["load_summary"]["root_bending_moment_nm"], "unit": "N m"},
        {"metric": "Root torsion", "value": result["load_summary"]["root_torsion_nm"], "unit": "N m"},
        {"metric": "Analytical tip deformation", "value": result["correlation"]["analytical_tip_deformation_m"], "unit": "m"},
        {"metric": "ANSYS baseline deformation", "value": result["correlation"]["fea_tip_deformation_m"], "unit": "m"},
        {"metric": "Deformation difference", "value": result["correlation"]["deformation_difference_percent"], "unit": "%"},
        {"metric": "Actual mass reduction", "value": result["sizing"]["actual_mass_reduction_percent"], "unit": "%"},
        {"metric": "Mass saved", "value": result["sizing"]["mass_saved_kg"], "unit": "kg"},
    ]
    _write_csv(output_dir / "summary_metrics.csv", ["metric", "value", "unit"], summary_rows)

    mesh_rows = []
    for row in result["mesh_steps"]:
        mesh_rows.append(
            {
                "mesh": row["mesh"],
                "nodes": row["nodes"],
                "elements": row["elements"],
                "max_total_deformation_m": row["max_total_deformation_m"],
                "max_von_mises_stress_mpa": row["max_von_mises_stress_pa"] / 1e6,
                "deformation_change_from_previous_percent": row["deformation_change_from_previous_percent"],
                "stress_change_from_previous_percent": row["stress_change_from_previous_percent"],
            }
        )
    _write_csv(
        output_dir / "mesh_sensitivity.csv",
        [
            "mesh",
            "nodes",
            "elements",
            "max_total_deformation_m",
            "max_von_mises_stress_mpa",
            "deformation_change_from_previous_percent",
            "stress_change_from_previous_percent",
        ],
        mesh_rows,
    )

    baseline = result["fea_cases"]["baseline"]
    reduced = result["fea_cases"]["reduced_thickness"]
    sizing_rows = [
        {
            "metric": "Mass (kg)",
            "baseline": baseline["mass_kg"],
            "reduced": reduced["mass_kg"],
            "change_percent": result["sizing"]["changes"]["mass_percent"],
        },
        {
            "metric": "Maximum deformation (m)",
            "baseline": baseline["max_total_deformation_m"],
            "reduced": reduced["max_total_deformation_m"],
            "change_percent": result["sizing"]["changes"]["deformation_percent"],
        },
        {
            "metric": "Maximum stress (MPa)",
            "baseline": baseline["max_von_mises_stress_pa"] / 1e6,
            "reduced": reduced["max_von_mises_stress_pa"] / 1e6,
            "change_percent": result["sizing"]["changes"]["stress_percent"],
        },
        {
            "metric": "First buckling factor",
            "baseline": baseline["buckling_mode_1_factor"],
            "reduced": reduced["buckling_mode_1_factor"],
            "change_percent": result["sizing"]["changes"]["buckling_factor_percent"],
        },
        {
            "metric": "Yield factor of safety",
            "baseline": result["sizing"]["baseline_yield_fos"],
            "reduced": result["sizing"]["reduced_yield_fos"],
            "change_percent": (
                (result["sizing"]["reduced_yield_fos"] / result["sizing"]["baseline_yield_fos"] - 1.0)
                * 100.0
            ),
        },
    ]
    _write_csv(
        output_dir / "sizing_trade_study.csv",
        ["metric", "baseline", "reduced", "change_percent"],
        sizing_rows,
    )

    gate_rows = [{"check": key, "status": value} for key, value in result["gates"].items()]
    _write_csv(output_dir / "check_status.csv", ["check", "status"], gate_rows)


def _write_markdown(result: dict[str, Any], path: Path) -> None:
    baseline = result["fea_cases"]["baseline"]
    reduced = result["fea_cases"]["reduced_thickness"]
    correlation = result["correlation"]
    sizing = result["sizing"]
    mesh = result["mesh_steps"]
    latest_mesh = mesh[-1]
    lines = [
        "# Wing-Box Automated Analysis Summary",
        "",
        f"Generated {datetime.now(timezone.utc).strftime('%Y-%m-%d %H:%M UTC')}.",
        "",
        "## Load calculations",
        "",
        "| Metric | Result |",
        "|---|---:|",
        f'| Dynamic pressure at Mach {result["flight_condition"]["mach"]:.2f}, 37,000 ft | {result["flight_condition"]["dynamic_pressure_pa"] / 1000:.3f} kPa |',
        f'| Theoretical half-wing lift | {result["flight_condition"]["half_aircraft_lift_n"] / 1000:.3f} kN |',
        f'| BDF aerodynamic half-wing force | {result["load_summary"]["bdf_aerodynamic_half_wing_force_n"] / 1000:.3f} kN |',
        f'| Aerodynamic load difference | {result["load_summary"]["lift_difference_percent"]:.3f}% |',
        f'| Net root vertical load | {result["load_summary"]["net_vertical_load_n"] / 1000:.3f} kN |',
        f'| Root bending moment | {result["load_summary"]["root_bending_moment_nm"] / 1e6:.3f} MN·m |',
        f'| Root torsion | {result["load_summary"]["root_torsion_nm"] / 1e6:.3f} MN·m |',
        "",
        "## Analytical–FEA correlation",
        "",
        "| Result | Analytical | ANSYS | Difference | Status |",
        "|---|---:|---:|---:|---|",
        f'| Total deformation | {correlation["analytical_tip_deformation_m"]:.4f} m | {correlation["fea_tip_deformation_m"]:.4f} m | {correlation["deformation_difference_percent"]:.2f}% | {result["gates"]["deformation_correlation"]} |',
        f'| Stress comparison* | {correlation["analytical_peak_nominal_vm_stress_pa"] / 1e6:.2f} MPa | {correlation["fea_peak_vm_stress_pa"] / 1e6:.2f} MPa | {correlation["nominal_peak_stress_difference_percent"]:.2f}% | Reference |',
        "",
        "*The analytical value is a nominal beam stress; the FEA value is a local peak.",
        "",
        "## Sizing trade study",
        "",
        "| Metric | Baseline | Reduced-thickness | Change |",
        "|---|---:|---:|---:|",
        f'| Mass | {baseline["mass_kg"]:.1f} kg | {reduced["mass_kg"]:.1f} kg | {sizing["changes"]["mass_percent"]:+.2f}% |',
        f'| Maximum deformation | {baseline["max_total_deformation_m"]:.4f} m | {reduced["max_total_deformation_m"]:.4f} m | {sizing["changes"]["deformation_percent"]:+.2f}% |',
        f'| Maximum von Mises stress | {baseline["max_von_mises_stress_pa"] / 1e6:.2f} MPa | {reduced["max_von_mises_stress_pa"] / 1e6:.2f} MPa | {sizing["changes"]["stress_percent"]:+.2f}% |',
        f'| First buckling factor | {baseline["buckling_mode_1_factor"]:.5f} | {reduced["buckling_mode_1_factor"]:.4f} | {sizing["changes"]["buckling_factor_percent"]:+.2f}% |',
        "",
        f'**Outcome:** the solved reduced-thickness case achieved an {sizing["actual_mass_reduction_percent"]:.2f}% mass reduction ({sizing["mass_saved_kg"]:.1f} kg). The response changes are reported for the next sizing iteration.',
        "",
        "## Mesh sensitivity",
        "",
        "| Mesh | Nodes | Elements | Max deformation | Max stress |",
        "|---|---:|---:|---:|---:|",
    ]
    for row in mesh:
        lines.append(
            f'| {row["mesh"].title()} | {row["nodes"]:,} | {row["elements"]:,} | '
            f'{row["max_total_deformation_m"]:.5f} m | '
            f'{row["max_von_mises_stress_pa"] / 1e6:.3f} MPa |'
        )
    if latest_mesh["deformation_change_from_previous_percent"] is not None:
        lines.extend(
            [
                "",
                f'Latest deformation change: **{latest_mesh["deformation_change_from_previous_percent"]:+.2f}%**; '
                f'latest stress change: **{latest_mesh["stress_change_from_previous_percent"]:+.2f}%**.',
            ]
        )
    lines.extend(
        [
            "",
            f'**Mesh status:** {result["gates"]["mesh_convergence"]}.',
            "",
            "## Automated check status",
            "",
            "| Check | Status |",
            "|---|---|",
        ]
    )
    for check, status in result["gates"].items():
        lines.append(f'| {check.replace("_", " ").title()} | {status} |')
    path.write_text("\n".join(lines) + "\n", encoding="utf-8")


def write_outputs(
    result: dict[str, Any],
    output_dir: str | Path,
    *,
    make_plots: bool = True,
) -> list[Path]:
    """Write the machine-readable tables, report, and charts."""

    destination = Path(output_dir)
    destination.mkdir(parents=True, exist_ok=True)

    summary_json = destination / "analysis_summary.json"
    summary_json.write_text(
        json.dumps(result, indent=2, sort_keys=True) + "\n", encoding="utf-8"
    )
    _write_tables(result, destination)
    _write_markdown(result, destination / "analysis_summary.md")

    if make_plots:
        _save_load_balance(result, destination / "01_load_balance.png")
        _save_correlation(result, destination / "02_deformation_correlation.png")
        _save_mesh_sensitivity(result, destination / "03_mesh_sensitivity.png")
        _save_sizing_tradeoff(result, destination / "04_sizing_tradeoff.png")
        _save_spanwise_response(result, destination / "05_spanwise_response.png")

    return sorted(path for path in destination.iterdir() if path.is_file())
