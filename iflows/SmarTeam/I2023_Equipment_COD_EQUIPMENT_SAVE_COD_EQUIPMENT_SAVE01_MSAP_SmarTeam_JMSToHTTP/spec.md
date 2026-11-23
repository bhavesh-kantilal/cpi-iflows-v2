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
| 2026-11-23 | Step name of the logCustomHeaders.groovy step (L2, user, screenshot: "LogCustomHeaders" for all iFlows) | `LogCustomHeaders` | 1.1.2: renamed from 'Set Custom Header' (2 steps). The build names every such step this way and fails on any other name |
| 2026-11-23 | SmarTeam adapter not externalized (L2, user: "we always externalize adapters"; rule already in CLAUDE.md, missed in the first round) | Externalize every setting of the SmarTeam HTTP receiver | 1.1.3: 12 `SmarTeam_*` parameters, defaults = old fixed values, propdef references like the I0539 Medius receiver (L3). `SmarTeam_RetryOnException` and `SmarTeam_IdleTimeout` (pooledConnectionIdleTimeout, ms) are not in the I0539 set: UNVERIFIED until the CPI test |
| 2026-11-23 | Remaining fixed adapter settings (L2, user: "all of them") | Externalize; defaults = old values | 1.1.4: `PD_Address` (ProcessDirect sender address, default `/<iFlow name>`; **must stay equal to the iFlow name**: the dispatcher calls it); `HTTPS_Address` (retrigger path, default `/<iFlow name>`); OData lookup to MSAP: `MSAP_Timeout` (1 min), `MSAP_Authentication` (Basic), `MSAP_ProxyType` (sapcc), `MSAP_CSRFProtected` (false), `MSAP_ReuseConnection` (true), `MSAP_RetryOnException` (false), `MSAP_RetryOnErrorResponse` (false), `MSAP_RetryIterations` (1), `MSAP_RetryInterval` (5), `MSAP_AllowedRequestHeaders` / `MSAP_AllowedResponseHeaders` (traceparent). Build check `fixed_adapter_values` |
