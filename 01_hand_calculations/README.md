# Hand-calculation workbook

`wingbox_hand_calculations.xlsx` contains the hand calculations used for the independent load check and ANSYS correlation.

| Sheet | Purpose |
|---|---|
| `Summary` | Headline loads, correlation results and check status |
| `Inputs` | Geometry, material, flight condition, FEA references and editable assumptions |
| `Beam Calc` | Spanwise swept-beam bending, shear, torsion, stress and deformation |
| `Buckling` | Classical plate-buckling screen |
| `Fatigue` | Goodman/Basquin/Miner and Paris-law screening calculations |
| `Sizing` | Thickness-scaling sensitivity calculations |
| `Audit` | Independent cross-checks of the main inputs and results |

The workbook uses the same elastic properties and swept load path as the ANSYS model. Reference inputs and editable assumptions are visually separated, the equations remain visible, and the audit sheet does not feed the reported calculations.

The completed ANSYS sizing results are recorded separately in [`../03_ansys_fea/`](../03_ansys_fea/) and are post-processed by [`../05_python_automation/`](../05_python_automation/).
