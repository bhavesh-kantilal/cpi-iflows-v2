# I2024_P_FunctionLocation_COD_FUNCTIONAL_LOCATION_SAVE_COD_FUNCTIONAL_LOCATION_SAVE01_MSAP_IDocToJMS

Parent (package MSAPControllingMasterData): IDoc COD_FUNCTIONAL_LOCATION_SAVE from MSAP → receiver determination (FSAP, SmarTeam) → JMS.

- Source: `iflows/SmarTeam/source/MSAPControllingMasterData_artifacts (4).zip → I2024_P_… (1.0.7)` (Bhavesh's export, 2026-11-23)
- Build: `py -I tools/iflow_build_smarteam.py --only I2024_P_FunctionLocation_COD_FUNCTIONAL_LOCATION_SAVE_COD_FUNCTIONAL_LOCATION_SAVE01_MSAP_IDocToJMS` (config in `CHILDREN` / `PARENTS`)

## Decisions
| Date | Question | Answer | Impact |
|---|---|---|---|
| 2026-11-23 | Same round as I2050 (L2, user: "change the remaining iFlows") | Applied | `SAP_MessageType` held the value twice (`COD_FUNCTIONAL_LOCATION_SAVE.COD_FUNCTIONAL_LOCATION_SAVE01COD_FUNCTIONAL_…`) → `COD_FUNCTIONAL_LOCATION_SAVE.COD_FUNCTIONAL_LOCATION_SAVE01` |
| 2026-11-23 | Same round as I2050 (L2, user: "change the remaining iFlows") | Applied | Removed unused parameter `AttachmentName` |
| 2026-11-23 | Same round as I2050 (L2, user: "change the remaining iFlows") | Applied | iflw file `I2023_P_Equipment_…_IDocToJMS.iflw` → `I2024_P_FunctionLocation_…_IDocToJMS.iflw` |

## Open points (not changed)
- "Error End " in Main Process (`EndEvent_961984`): left as is (intended failure path?)
