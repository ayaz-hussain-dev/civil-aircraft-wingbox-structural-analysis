# Evidence index

This index maps each headline claim to its numerical source and visual evidence.

| Claim / result | Numerical source | Visual evidence |
|---|---|---|
| 7.996% aerodynamic load difference | `01_hand_calculations/wingbox_hand_calculations.xlsx`; `05_python_automation/outputs/flight_condition.csv` | `05_python_automation/outputs/01_load_balance.png` |
| 4.68% analytical–FEA deformation difference | Workbook `Summary` and `Beam Calc`; `05_python_automation/outputs/summary_metrics.csv` | `03_ansys_fea/baseline/baseline_total_deformation.png`; `05_python_automation/outputs/02_deformation_correlation.png` |
| Baseline 201.87 MPa von Mises stress | `03_ansys_fea/results_summary.csv` | `03_ansys_fea/baseline/baseline_von_mises_stress.png` |
| Baseline buckling factors 0.45096 and 0.96238 | ANSYS result captures | `03_ansys_fea/buckling/` |
| 11.14% mass reduction | `03_ansys_fea/results_summary.csv`; `05_python_automation/outputs/sizing_trade_study.csv` | `03_ansys_fea/sizing/baseline_mass.png`; `03_ansys_fea/sizing/reduced_mass.png` |
| Re-solved sizing response | `03_ansys_fea/results_summary.csv` | `03_ansys_fea/sizing/reduced_total_deformation.png`; `reduced_von_mises_stress.png`; `reduced_buckling_mode_01.png` |
| Two-level mesh sensitivity | `04_mesh_sensitivity/mesh_results.csv` | `04_mesh_sensitivity/screenshots/`; `05_python_automation/outputs/03_mesh_sensitivity.png` |
| CATIA component assembly | Product-tree captures | `02_catia_cad/screenshots/catia_wingbox_assembly.png`; `catia_internal_structure.png` |
| Parametric skin feature | CATIA feature capture | `02_catia_cad/screenshots/catia_parametric_skin_feature.png` |

The source CATIA and ANSYS project archives are intentionally kept outside this portfolio repository. The included workbook, code, CSV files, charts, and full-resolution captures preserve the review trail without committing large native working files.
