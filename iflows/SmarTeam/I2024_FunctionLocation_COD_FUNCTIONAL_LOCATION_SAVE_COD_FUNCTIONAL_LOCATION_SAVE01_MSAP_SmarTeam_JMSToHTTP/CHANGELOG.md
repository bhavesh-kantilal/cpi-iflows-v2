# CHANGELOG — I2024_FunctionLocation_COD_FUNCTIONAL_LOCATION_SAVE_COD_FUNCTIONAL_LOCATION_SAVE01_MSAP_SmarTeam_JMSToHTTP

## 1.0.9 — 2026-11-23 11:03 CET
- SmarTeam HTTP receiver externalized (12 settings, shared `SmarTeam_*` set): `SmarTeam_Address`, `SmarTeam_ProxyType`, `SmarTeam_Authentication`, `SmarTeam_Timeout`, `SmarTeam_ThrowExceptionOnFailure`, `SmarTeam_RetryOnConnectionFailure`, `SmarTeam_RetryIterations`, `SmarTeam_RetryInterval`, `SmarTeam_RetryOnException`, `SmarTeam_AllowedRequestHeaders`, `SmarTeam_AllowedResponseHeaders`, `SmarTeam_IdleTimeout`. Defaults = the previous fixed values.

## 1.0.8 — 2026-11-23 10:39 CET
- Every logCustomHeaders.groovy step is now named `LogCustomHeaders` (was 'Set Custom Header' (2 steps)).

## 1.0.7 — 2026-11-23 10:25 CET
Built from I2024_…_JMSToHTTP.jar (1.0.6).
- Step "Request Reply 1" renamed to "Send to SmarTeam" (as in the other children)
- After Send to SmarTeam: property `CH_SmarTeamWorkId` (xpath `/InboundResponse/WorkId`) in the response Content Modifier `CallActivity_734141`, then a new Script step "Set Custom Header" (`UTIL_LogCustomHeaders`). Earlier CH_ headers stay (CPI adds only new values)
- OData lookup `OData`: Delete Idle Connection → `{{{{MSAP_DeleteIdleConnection}}}}` (true, was a fixed false) and Idle Timeout → `{{{{MSAP_IdleTimeout}}}}` (300), as Bhavesh did in I2050_P 1.0.5. CSRF was already off (GET)
- Removed unused parameters: all `JMSReceiver_*` / `JMSSender_*` (the sender is ProcessDirect), `MaxRetries`, `SAP_MessageType` (unused here, and it held the Equipment value; the flow uses `SAP_Message_name`)
- iflw file `I0579_CostCentre…JMSToSOAP.iflw` → `<iFlow name>.iflw`
