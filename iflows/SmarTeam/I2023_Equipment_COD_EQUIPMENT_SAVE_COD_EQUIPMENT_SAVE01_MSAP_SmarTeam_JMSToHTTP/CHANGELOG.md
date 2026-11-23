# CHANGELOG — I2023_Equipment_COD_EQUIPMENT_SAVE_COD_EQUIPMENT_SAVE01_MSAP_SmarTeam_JMSToHTTP

## 1.1.6 — 2026-11-23 11:30 CET
- OData lookup parameters renamed to the `MSAP_<Setting>` pattern: `CC_Location` → `MSAP_LocationID`, `MSAPHost` → `MSAP_Host`, `MSAPCredentials` → `MSAP_Credentials`, `sap-client` → `MSAP_Client`. Defaults unchanged; **set tenant values again** under the new names.

## 1.1.5 — 2026-11-23 11:29 CET
- SmarTeam HTTP receiver: Location ID → `{{SmarTeam_LocationID}}` (default empty), always together with Proxy Type.

## 1.1.4 — 2026-11-23 11:07 CET
- Externalized `PD_Address` (ProcessDirect sender address, default `/<iFlow name>`; **must stay equal to the iFlow name**: the dispatcher calls it).
- Externalized `HTTPS_Address` (retrigger path, default `/<iFlow name>`).
- Externalized OData lookup to MSAP: `MSAP_Timeout` (1 min), `MSAP_Authentication` (Basic), `MSAP_ProxyType` (sapcc), `MSAP_CSRFProtected` (false), `MSAP_ReuseConnection` (true), `MSAP_RetryOnException` (false), `MSAP_RetryOnErrorResponse` (false), `MSAP_RetryIterations` (1), `MSAP_RetryInterval` (5), `MSAP_AllowedRequestHeaders` / `MSAP_AllowedResponseHeaders` (traceparent).
- New build check: no fixed adapter value left (except the shared mail utility's ProcessDirect address).

## 1.1.3 — 2026-11-23 11:03 CET
- SmarTeam HTTP receiver externalized (12 settings, shared `SmarTeam_*` set): `SmarTeam_Address`, `SmarTeam_ProxyType`, `SmarTeam_Authentication`, `SmarTeam_Timeout`, `SmarTeam_ThrowExceptionOnFailure`, `SmarTeam_RetryOnConnectionFailure`, `SmarTeam_RetryIterations`, `SmarTeam_RetryInterval`, `SmarTeam_RetryOnException`, `SmarTeam_AllowedRequestHeaders`, `SmarTeam_AllowedResponseHeaders`, `SmarTeam_IdleTimeout`. Defaults = the previous fixed values.

## 1.1.2 — 2026-11-23 10:39 CET
- Every logCustomHeaders.groovy step is now named `LogCustomHeaders` (was 'Set Custom Header' (2 steps)).

## 1.1.1 — 2026-11-23 10:25 CET
Built from I2023_…_JMSToHTTP.jar (1.1).
- After Send to SmarTeam: property `CH_SmarTeamWorkId` (xpath `/InboundResponse/WorkId`) in the response Content Modifier `CallActivity_734129`, then a new Script step "Set Custom Header" (`UTIL_LogCustomHeaders`). Earlier CH_ headers stay (CPI adds only new values)
- OData lookup `OData`: Delete Idle Connection → `{{{{MSAP_DeleteIdleConnection}}}}` (true, was a fixed false) and Idle Timeout → `{{{{MSAP_IdleTimeout}}}}` (300), as Bhavesh did in I2050_P 1.0.5. CSRF was already off (GET)
- Removed unused parameters: all `JMSReceiver_*` / `JMSSender_*` (the sender is ProcessDirect), `MaxRetries`, `SAP_Message_name`
- iflw file `I0579_CostCentre…JMSToSOAP.iflw` → `<iFlow name>.iflw`
