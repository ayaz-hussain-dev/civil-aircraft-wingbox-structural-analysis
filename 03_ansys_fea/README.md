# ANSYS Mechanical results

The evidence is grouped by analysis stage:

- `baseline/` — baseline shell mesh, total deformation and equivalent stress;
- `buckling/` — first two baseline eigenvalue buckling modes;
- `sizing/` — baseline/reduced thickness and mass records, plus re-solved reduced-thickness static and buckling results.

## Result summary

| Metric | Baseline | Reduced-thickness |
|---|---:|---:|
| Shell-thickness scale | 1.00 | 0.89 |
| Mass | 9,679.1 kg | 8,601.0 kg |
| Maximum total deformation | 2.9277 m | 3.3068 m |
| Maximum von Mises stress | 201.87 MPa | 230.46 MPa |
| First buckling load factor | 0.45096 | 0.3562 |

The same values are available in `results_summary.csv`. Only the Windows taskbar has been cropped from the screenshots; the result legends, model trees, units, and tabular values remain visible.
