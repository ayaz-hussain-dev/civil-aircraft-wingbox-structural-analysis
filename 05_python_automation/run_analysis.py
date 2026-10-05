#!/usr/bin/env python3
"""Command-line entry point for the wing-box analysis."""

from __future__ import annotations

import argparse
from pathlib import Path

from wingbox_analysis import analyse_project
from wingbox_analysis.reporting import write_outputs


def parse_args() -> argparse.Namespace:
    project_root = Path(__file__).resolve().parent
    parser = argparse.ArgumentParser(
        description="Run the wing-box load calculations and FEA post-processing."
    )
    parser.add_argument(
        "--data-dir",
        type=Path,
        default=project_root / "data",
        help="Directory containing the project JSON and CSV inputs.",
    )
    parser.add_argument(
        "--output-dir",
        type=Path,
        default=project_root / "outputs",
        help="Destination for generated tables, report, JSON, and charts.",
    )
    parser.add_argument(
        "--no-plots",
        action="store_true",
        help="Generate only JSON, CSV, and Markdown outputs.",
    )
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    result = analyse_project(args.data_dir)
    files = write_outputs(result, args.output_dir, make_plots=not args.no_plots)

    print("Wing-box analysis complete")
    print(
        "  deformation correlation: "
        f'{result["correlation"]["deformation_difference_percent"]:.2f}% '
        f'({result["gates"]["deformation_correlation"]})'
    )
    print(
        "  solved mass reduction:   "
        f'{result["sizing"]["actual_mass_reduction_percent"]:.2f}%'
    )
    print(f'  mesh status:             {result["gates"]["mesh_convergence"]}')
    print(f"  outputs written:         {len(files)} files in {args.output_dir}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
