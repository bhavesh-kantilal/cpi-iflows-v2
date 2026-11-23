# I2023_P_Equipment_COD_EQUIPMENT_SAVE_COD_EQUIPMENT_SAVE01_MSAP_IDocToJMS

Parent (package MSAPControllingMasterData): IDoc COD_EQUIPMENT_SAVE from MSAP → receiver determination (FSAP, SmarTeam) → JMS.

- Source: `iflows/SmarTeam/source/MSAPControllingMasterData_artifacts (4).zip → I2023_P_… (1.0.6)` (Bhavesh's export, 2026-11-23)
- Build: `py -I tools/iflow_build_smarteam.py --only I2023_P_Equipment_COD_EQUIPMENT_SAVE_COD_EQUIPMENT_SAVE01_MSAP_IDocToJMS` (config in `CHILDREN` / `PARENTS`)

## Decisions
| Date | Question | Answer | Impact |
|---|---|---|---|
| 2026-11-23 | Same round as I2050 (L2, user: "change the remaining iFlows") | Applied | Removed 8 unused parameters: `AttachmentName`, `CompressStoredMessage`, `Encryptstoredmessage`, `Expirationperiod`, `HTTP_Adress`, `JMS_TransferexchangeProperties`, `RetentionThreshold`, `TransferexchangeProperties`. The iflw file name was already right |

## Open points (not changed)
- "Error End" in Main Process (`EndEvent_961984`): left as is (intended failure path?)
