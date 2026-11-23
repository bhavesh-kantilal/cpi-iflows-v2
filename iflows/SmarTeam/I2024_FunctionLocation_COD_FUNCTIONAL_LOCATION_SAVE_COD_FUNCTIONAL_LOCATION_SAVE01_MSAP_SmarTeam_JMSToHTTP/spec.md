# I2024_FunctionLocation_COD_FUNCTIONAL_LOCATION_SAVE_COD_FUNCTIONAL_LOCATION_SAVE01_MSAP_SmarTeam_JMSToHTTP

Child: looks up the superior functional location in MSAP (OData), maps the functional location and POSTs it to SmarTeam. Parent: `I2024_P_…_IDocToJMS`.

- Source: `iflows/SmarTeam/source/I2024_…_JMSToHTTP.jar (1.0.6)` (Bhavesh's export, 2026-11-23)
- Build: `py -I tools/iflow_build_smarteam.py --only I2024_FunctionLocation_COD_FUNCTIONAL_LOCATION_SAVE_COD_FUNCTIONAL_LOCATION_SAVE01_MSAP_SmarTeam_JMSToHTTP` (config in `CHILDREN` / `PARENTS`)

## Decisions
| Date | Question | Answer | Impact |
|---|---|---|---|
| 2026-11-23 | Same round as I2050 (L2, user: "change the remaining iFlows") | Applied | Step "Request Reply 1" renamed to "Send to SmarTeam" (as in the other children) |
| 2026-11-23 | Same round as I2050 (L2, user: "change the remaining iFlows") | Applied | After Send to SmarTeam: property `CH_SmarTeamWorkId` (xpath `/InboundResponse/WorkId`) in the response Content Modifier `CallActivity_734141`, then a new Script step "Set Custom Header" (`UTIL_LogCustomHeaders`). Earlier CH_ headers stay (CPI adds only new values) |
| 2026-11-23 | Same round as I2050 (L2, user: "change the remaining iFlows") | Applied | OData lookup `OData`: Delete Idle Connection → `{{{{MSAP_DeleteIdleConnection}}}}` (true, was a fixed false) and Idle Timeout → `{{{{MSAP_IdleTimeout}}}}` (300), as Bhavesh did in I2050_P 1.0.5. CSRF was already off (GET) |
| 2026-11-23 | Same round as I2050 (L2, user: "change the remaining iFlows") | Applied | Removed unused parameters: all `JMSReceiver_*` / `JMSSender_*` (the sender is ProcessDirect), `MaxRetries`, `SAP_MessageType` (unused here, and it held the Equipment value; the flow uses `SAP_Message_name`) |
| 2026-11-23 | Same round as I2050 (L2, user: "change the remaining iFlows") | Applied | iflw file `I0579_CostCentre…JMSToSOAP.iflw` → `<iFlow name>.iflw` |
| 2026-11-23 | Step name of the logCustomHeaders.groovy step (L2, user, screenshot: "LogCustomHeaders" for all iFlows) | `LogCustomHeaders` | 1.0.8: renamed from 'Set Custom Header' (2 steps). The build names every such step this way and fails on any other name |
