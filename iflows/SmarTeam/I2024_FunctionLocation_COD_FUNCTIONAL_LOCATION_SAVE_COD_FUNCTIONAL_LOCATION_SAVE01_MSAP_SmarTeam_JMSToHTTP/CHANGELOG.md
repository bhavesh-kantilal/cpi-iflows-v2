# CHANGELOG — I2024_FunctionLocation_COD_FUNCTIONAL_LOCATION_SAVE_COD_FUNCTIONAL_LOCATION_SAVE01_MSAP_SmarTeam_JMSToHTTP

## 1.0.14 — 2026-11-23 11:59 CET
- OData lookup receiver `Receiver1` → `MSAP` (participant, channel system, propdef categories). The ProcessDirect sender is also named `MSAP` (sender and receiver are on separate Configure tabs; UNVERIFIED until the CPI import).

## 1.0.13 — 2026-11-23 11:36 CET
- Parameter renamed: `SAP_Message_name` → `SAP_MessageType` (header SAP_MessageType = `{{SAP_MessageType}}`, value `COD_FUNCTIONAL_LOCATION_SAVE.COD_FUNCTIONAL_LOCATION_SAVE01`). Set the tenant value again if configured.

## 1.0.12 — 2026-11-23 11:30 CET
- OData lookup parameters renamed to the `MSAP_<Setting>` pattern: `MSAPHost` → `MSAP_Host`, `MSAPCredentials` → `MSAP_Credentials`, `sap-client` → `MSAP_Client`. Defaults unchanged; **set tenant values again** under the new names.

## 1.0.11 — 2026-11-23 11:29 CET
- SmarTeam HTTP receiver: Location ID → `{{SmarTeam_LocationID}}` (default empty), always together with Proxy Type.
- OData lookup: Location ID → `{{MSAP_LocationID}}` (default empty; proxy is sapcc, I2023 has `CC_Location`).

## 1.0.10 — 2026-11-23 11:07 CET
- Externalized `PD_Address` (ProcessDirect sender address, default `/<iFlow name>`; **must stay equal to the iFlow name**: the dispatcher calls it).
- Externalized `HTTPS_Address` (retrigger path, default `/<iFlow name>`).
- Externalized OData lookup to MSAP: `MSAP_Timeout` (1 min), `MSAP_Authentication` (Basic), `MSAP_ProxyType` (sapcc), `MSAP_CSRFProtected` (false), `MSAP_ReuseConnection` (true), `MSAP_RetryOnException` (false), `MSAP_RetryOnErrorResponse` (false), `MSAP_RetryIterations` (1), `MSAP_RetryInterval` (5), `MSAP_AllowedRequestHeaders` / `MSAP_AllowedResponseHeaders` (traceparent).
- New build check: no fixed adapter value left (except the shared mail utility's ProcessDirect address).

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
