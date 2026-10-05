# Wing-Box Python Automation

Python scripts for the **Civil Aircraft Wing-Box Structural Design and FEA** project. They automate the repeatable calculations and post-processing used in the project:

- ISA cruise-condition and `qSCL` lift calculations;
- signed half-wing load balance;
- analytical-to-ANSYS deformation correlation;
- baseline/reduced-thickness FEA comparison;
- mesh-sensitivity calculations;
- CSV, JSON, Markdown, and chart generation.

## Verified result snapshot

| Result | Value |
|---|---:|
| Analytical tip deformation | 2.7969 m |
| ANSYS baseline deformation | 2.9277 m |
| Analytical–FEA difference | **4.68%** |
| Baseline mass | 9,679.1 kg |
| Reduced-thickness mass | 8,601.0 kg |
| Solved mass reduction | **11.14%** |
| Coarse mesh | 8,159 elements |
| Refined mesh | 57,260 elements |

The mesh dataset currently contains two solved levels. A third level can be added as another row when it has been solved.

## Run

Requires Python 3.10 or newer.

```bash
python -m pip install -r requirements.txt
python run_analysis.py
```

On Windows, `run_analysis.bat` can be used after installing the requirement.

The generated files appear in `outputs/`:

- `analysis_summary.md` and `analysis_summary.json`;
- calculation and comparison CSV files;
- five PNG charts.

Run the regression checks with:

```bash
python -m unittest discover -s tests -v
```

## Input files

| File | Purpose |
|---|---|
| `project_inputs.json` | Geometry, flight condition, material, analytical references, and check limits |
| `load_components.csv` | Signed aerodynamic and inertia loads |
| `fea_results.csv` | Baseline and reduced-thickness ANSYS results |
| `mesh_results.csv` | Mesh levels and response values |
| `spanwise_handcalc.csv` | Root-to-tip analytical response used for plotting |
| `evidence_manifest.csv` | Mapping from original screenshots to consistent repository names |

To add the third mesh, append one row to `data/mesh_results.csv` and rerun the script. The step changes and convergence status will update automatically.

## Data provenance

The numerical FEA values were taken from the ANSYS result screenshots, while the analytical values come from the hand-calculation workbook. The native project archives are stored separately.
