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
| 2026-11-23 | Step name of the logCustomHeaders.groovy step (L2, user, screenshot: "LogCustomHeaders" for all iFlows) | `LogCustomHeaders` | 1.0.9: renamed from 'Log Custom Headers'. The build names every such step this way and fails on any other name |
| 2026-11-23 | Name of the JMS send step (L2, user: all parents) | "Send To JMS" | 1.0.10: was "Send TO CI". Build rule `name_jms_send_step` |
| 2026-11-23 | Remaining fixed adapter settings (L2, user: "all of them") | Externalize; defaults = old values | 1.0.11: `PD_Address` (ProcessDirect sender address, default `/<iFlow name>`; keep it equal to what its callers use); `HTTPS_Address` (retrigger path, default `/<iFlow name>`); `HTTPS_BodySize` (40), `HTTPS_CSRF_Protected` (0); JMS receiver: `JMS_CompressStoredMessage` (1), `JMS_Encryptstoredmessage` (1), `JMS_TransferExchangeProperties` (0), names as in I2023_P. Build check `fixed_adapter_values` |
| 2026-11-23 | Role of the HTTPS sender in a parent (L2, user) | Parents keep their role, except when the HTTPS sender is only a retrigger (IDoc-based parent): then `SSAB_MessagingSend_InternalOperations` | 1.0.12: `HTTPS_Userrole` = `SSAB_MessagingSend_InternalOperations` (was `ESBMessaging.send`) |

## Open points (not changed)
- "Error End " in Main Process (`EndEvent_961984`): left as is (intended failure path?)
