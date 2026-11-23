# I2023_Equipment_COD_EQUIPMENT_SAVE_COD_EQUIPMENT_SAVE01_MSAP_SmarTeam_JMSToHTTP

Child: looks up the superior functional location in MSAP (OData), maps the equipment and POSTs it to SmarTeam. Parent: `I2023_P_…_IDocToJMS`.

- Source: `iflows/SmarTeam/source/I2023_…_JMSToHTTP.jar (1.1)` (Bhavesh's export, 2026-11-23)
- Build: `py -I tools/iflow_build_smarteam.py --only I2023_Equipment_COD_EQUIPMENT_SAVE_COD_EQUIPMENT_SAVE01_MSAP_SmarTeam_JMSToHTTP` (config in `CHILDREN` / `PARENTS`)

## Decisions
| Date | Question | Answer | Impact |
|---|---|---|---|
| 2026-11-23 | Same round as I2050 (L2, user: "change the remaining iFlows") | Applied | After Send to SmarTeam: property `CH_SmarTeamWorkId` (xpath `/InboundResponse/WorkId`) in the response Content Modifier `CallActivity_734129`, then a new Script step "Set Custom Header" (`UTIL_LogCustomHeaders`). Earlier CH_ headers stay (CPI adds only new values) |
| 2026-11-23 | Same round as I2050 (L2, user: "change the remaining iFlows") | Applied | OData lookup `OData`: Delete Idle Connection → `{{{{MSAP_DeleteIdleConnection}}}}` (true, was a fixed false) and Idle Timeout → `{{{{MSAP_IdleTimeout}}}}` (300), as Bhavesh did in I2050_P 1.0.5. CSRF was already off (GET) |
| 2026-11-23 | Same round as I2050 (L2, user: "change the remaining iFlows") | Applied | Removed unused parameters: all `JMSReceiver_*` / `JMSSender_*` (the sender is ProcessDirect), `MaxRetries`, `SAP_Message_name` |
| 2026-11-23 | Same round as I2050 (L2, user: "change the remaining iFlows") | Applied | iflw file `I0579_CostCentre…JMSToSOAP.iflw` → `<iFlow name>.iflw` |
