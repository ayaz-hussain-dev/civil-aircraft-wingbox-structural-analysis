# Wing-Box Automated Analysis Summary

Generated 2026-10-05 00:07 UTC.

## Load calculations

| Metric | Result |
|---|---:|
| Dynamic pressure at Mach 0.85, 37,000 ft | 10.956 kPa |
| Theoretical half-wing lift | 1051.056 kN |
| BDF aerodynamic half-wing force | 967.011 kN |
| Aerodynamic load difference | 7.996% |
| Net root vertical load | 632.210 kN |
| Root bending moment | 10.846 MN·m |
| Root torsion | -0.295 MN·m |

## Analytical–FEA correlation

| Result | Analytical | ANSYS | Difference | Status |
|---|---:|---:|---:|---|
| Total deformation | 2.7969 m | 2.9277 m | 4.68% | PASS |
| Stress comparison* | 174.45 MPa | 201.87 MPa | 15.72% | Reference |

*The analytical value is a nominal beam stress; the FEA value is a local peak.

## Sizing trade study

| Metric | Baseline | Reduced-thickness | Change |
|---|---:|---:|---:|
| Mass | 9679.1 kg | 8601.0 kg | -11.14% |
| Maximum deformation | 2.9277 m | 3.3068 m | +12.95% |
| Maximum von Mises stress | 201.87 MPa | 230.46 MPa | +14.16% |
| First buckling factor | 0.45096 | 0.3562 | -21.01% |

**Outcome:** the solved reduced-thickness case achieved an 11.14% mass reduction (1078.1 kg). The response changes are reported for the next sizing iteration.

## Mesh sensitivity

| Mesh | Nodes | Elements | Max deformation | Max stress |
|---|---:|---:|---:|---:|
| Coarse | 6,647 | 8,159 | 0.14527 m | 10.663 MPa |
| Refined | 52,357 | 57,260 | 0.16319 m | 11.954 MPa |

Latest deformation change: **+12.34%**; latest stress change: **+12.11%**.

**Mesh status:** PENDING — add a third mesh before claiming convergence.

## Automated check status

| Check | Status |
|---|---|
| Lift Equation Check | PASS |
| Deformation Correlation | PASS |
| Baseline Deflection | PASS |
| Reduced Deflection | REVIEW |
| Baseline Yield | PASS |
| Reduced Yield | PASS |
| Baseline Buckling | REVIEW |
| Reduced Buckling | REVIEW |
| Mesh Convergence | PENDING — add a third mesh before claiming convergence |
