# Mesh sensitivity study

A separate verification load case was solved on the original and refined shell meshes.

| Mesh | Nodes | Elements | Deformation | Stress |
|---|---:|---:|---:|---:|
| Coarse | 6,647 | 8,159 | 0.14527 m | 10.663 MPa |
| Refined | 52,357 | 57,260 | 0.16319 m | 11.954 MPa |
| Step change | — | — | +12.34% | +12.11% |

The two solved levels show the response change with refinement. A third level is planned before formal mesh convergence is claimed.

`mesh_results.csv` contains the source values. `screenshots/` contains deformation and equivalent-stress contours for both meshes.
