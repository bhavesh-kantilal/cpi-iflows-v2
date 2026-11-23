# I2049_P_MaterialBOM_MSAP_AMQPToJMS

Parent (package MSAPPlantMaintenanceMasterData): Event Mesh (AMQP) → BOM lookup in MSAP (OData) → receiver determination → JMS `I0700_SmarTeam`.

- Source: `iflows/SmarTeam/source/MSAPPlantMaintenanceMasterData_artifacts (1).zip → I2049_P_MaterialBOM_MSAP_AMQPToJMS (1.0.3)` (Bhavesh's export, 2026-11-23)
- Build: `py -I tools/iflow_build_smarteam.py --only I2049_P_MaterialBOM_MSAP_AMQPToJMS` (config in `CHILDREN` / `PARENTS`)

## Decisions
| Date | Question | Answer | Impact |
|---|---|---|---|
| 2026-11-23 | Same round as I2050 (L2, user: "change the remaining iFlows") | Applied | ReceiverDetermination.groovy: child `I2049_MaterialBOM_MSAP_SmarTeam_PDToHTTP` → `I2049_MaterialBOM_MSAP_SmarTeam_JMSToHTTP`. Deploy together with the child |
| 2026-11-23 | Same round as I2050 (L2, user: "change the remaining iFlows") | Applied | Step "Intial Properties" → "Initial Properties" |
| 2026-11-23 | Same round as I2050 (L2, user: "change the remaining iFlows") | Applied | Removed 18 unused parameters: `Address`, `Authorization`, `CSRF Protected`, `CSRF_Protected`, `Contition`, `Credential Name`, `Custom Query Options`, `HTTP_Address` (was `/I2049_P_…`), `Location ID`, `Reuse Connection`, `S4`, `S4_Address`, `S4_Authentication`, `S4_CSRF`, `S4_Credential`, `S4_LocationID`, `S4_Proxy`, `UserRole` |
| 2026-11-23 | Same round as I2050 (L2, user: "change the remaining iFlows") | Applied | Renamed spaced parameters: `S4 Address`→`S4_Address`, `S4 Authentication`→`S4_Authentication`, `S4 Credential Name`→`S4_CredentialName`, `S4 Location ID`→`S4_LocationID`, `S4 CSRF Protected`→`S4_CSRFProtected`, `S4 Reuse Connection`→`S4_ReuseConnection`, `proxy Type`→`S4_ProxyType`, `Body Size`→`HTTPS_BodySize`. **Set tenant values again** |
| 2026-11-23 | Same round as I2050 (L2, user: "change the remaining iFlows") | Applied | OData Lookup BOM: `S4_CSRFProtected=false` (GET); Delete Idle Connection → `{{S4_DeleteIdleConnection}}` (true), Idle Timeout → `{{S4_IdleTimeout}}` (300), as in I2050_P |
| 2026-11-23 | Same round as I2050 (L2, user: "change the remaining iFlows") | Applied | iflw file `I0040_P_EDI_DESADV_B30_AMQPToJMS.iflw` → `I2049_P_MaterialBOM_MSAP_AMQPToJMS.iflw` |
| 2026-11-23 | Step name of the logCustomHeaders.groovy step (L2, user, screenshot: "LogCustomHeaders" for all iFlows) | `LogCustomHeaders` | 1.0.5: renamed from 'Log Headers'. The build names every such step this way and fails on any other name |
| 2026-11-23 | Name of the JMS send step (L2, user: all parents) | "Send To JMS" | 1.0.6: was "Send 1". Build rule `name_jms_send_step` |

## Open points (not changed)
- `metainfo.prop` still has `source=B30`; Bhavesh set `source=MSAP` in I2050_P 1.0.5. Set it the same?
