# Civil Aircraft Wing-Box Structural Design, FEA & Damage-Tolerance Study

> Supporting technical information, calculations, figures and project files are being consolidated and will be added as they are organised.

## Overview

This repository documents the design and assessment of a representative semi-monocoque civil-aircraft wing box using CATIA, ANSYS Mechanical and Python. The structural arrangement includes upper and lower skins, front and rear spars, ribs and longitudinal stiffening, with analytical and finite-element methods used to evaluate its behaviour under representative civil-aircraft loading.

## Technical scope

- Parametric CAD definition and structural idealisation.
- First-principles spanwise loading, shear-force, bending-moment and torsional-load calculations.
- Analytical bending-stress, shear-stress and deflection predictions.
- Static structural FEA, load-path assessment and mesh-convergence study.
- Linear buckling analysis and structural sizing iterations.
- Comparison of mass, stiffness, stress and buckling performance across configurations.
- Preliminary fatigue-life and crack-growth/damage-tolerance assessment at a critical location.
- Python automation for load calculations, design comparisons, post-processing and plots.

## Validation and design comparison

The project compares analytical and FEA predictions for clearly defined quantities and assesses structural-mass reduction while retaining the selected strength, stiffness and buckling requirements. Supporting calculations, convergence evidence and verified numerical results will be added as the project material is consolidated.

## Repository structure

- `cad/` — CATIA models and neutral CAD exports.
- `calculations/` — analytical calculations and loading data.
- `ansys/` — analysis setup and packaged project files.
- `scripts/` — Python automation and post-processing.
- `results/` — processed numerical results and comparison data.
- `images/` — CAD, mesh, boundary-condition and result figures.
- `docs/` — assumptions, methodology, limitations and conclusions.

## Software

- CATIA
- ANSYS Mechanical
- Python
