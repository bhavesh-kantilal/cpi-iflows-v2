# I2018_P_Material_MSAP_SOAPToJMS

Parent (package MSAPControllingMasterData): SOAP ProductMDMBulkReplicate from MSAP → receiver determination (FSAP, PSI, PATER, SmarTeam) → JMS.

- Source: `iflows/SmarTeam/source/MSAPControllingMasterData_artifacts (4).zip → I2018_P_Material_MSAP_SOAPToJMS (1.0.16)` (Bhavesh's export, 2026-11-23)
- Build: `py -I tools/iflow_build_smarteam.py --only I2018_P_Material_MSAP_SOAPToJMS` (config in `CHILDREN` / `PARENTS`)

## Decisions
| Date | Question | Answer | Impact |
|---|---|---|---|
| 2026-11-23 | Same round as I2050 (L2, user: "change the remaining iFlows") | Applied | Set Monitoring Identifiers XPaths without local-name(): CH_Material = `/*/ProductMDMReplicateRequestMessage/Product/ProductInternalID`, CH_MessageID = `/*/MessageHeader/ID` (only the root element has a namespace) |
| 2026-11-23 | Same round as I2050 (L2, user: "change the remaining iFlows") | Applied | iflw file `I2017_P_Material_ASAP_FSAP_SOAPToJMS.iflw` → `I2018_P_Material_MSAP_SOAPToJMS.iflw`. No unused parameters |
| 2026-11-23 | Step name of the logCustomHeaders.groovy step (L2, user, screenshot: "LogCustomHeaders" for all iFlows) | `LogCustomHeaders` | 1.0.18: renamed from 'Log Custom Header'. The build names every such step this way and fails on any other name |
| 2026-11-23 | Name of the JMS send step (L2, user: all parents) | "Send To JMS" | 1.0.19: was "Send". Build rule `name_jms_send_step` |
| 2026-11-23 | Remaining fixed adapter settings (L2, user: "all of them") | Externalize; defaults = old values | 1.0.20: `PD_Address` (ProcessDirect sender address, default `/<iFlow name>`; keep it equal to what its callers use); `HTTPS_Address` (retrigger path, default `/<iFlow name>`). Build check `fixed_adapter_values` |
| 2026-11-23 | Role of the HTTPS sender in a parent (L2, user) | Parents keep their role, except when the HTTPS sender is only a retrigger (SOAP-based parent): then `SSAB_MessagingSend_InternalOperations` | 1.0.21: `HTTP_UserRole` = `SSAB_MessagingSend_InternalOperations` (was `ESBMessaging.send`) |

## Open points (not changed)
- "Error End" in Main Process (`EndEvent_682`): left as is, it looks like the intended failure path (I2050_P uses an escalation end there)
- Parameter `SAP_MESSAGETYPE` (capitals) differs from `SAP_MessageType` in the other flows
