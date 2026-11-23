# CHANGELOG — I2018_Material_MSAP_SmarTeam_JMSToHTTP

## 1.1.3 — 2026-11-23 11:03 CET
- SmarTeam HTTP receiver externalized (12 settings, shared `SmarTeam_*` set): `SmarTeam_Address`, `SmarTeam_ProxyType`, `SmarTeam_Authentication`, `SmarTeam_Timeout`, `SmarTeam_ThrowExceptionOnFailure`, `SmarTeam_RetryOnConnectionFailure`, `SmarTeam_RetryIterations`, `SmarTeam_RetryInterval`, `SmarTeam_RetryOnException`, `SmarTeam_AllowedRequestHeaders`, `SmarTeam_AllowedResponseHeaders`, `SmarTeam_IdleTimeout`. Defaults = the previous fixed values.

## 1.1.2 — 2026-11-23 10:39 CET
- Every logCustomHeaders.groovy step is now named `LogCustomHeaders` (was 'Set Custom Header' (2 steps)).
- `AllowedHeaders` = `SSAB.*|SAP.*` (was `SSAB.*`; rule for all children).

## 1.1.1 — 2026-11-23 10:25 CET
Built from I2018_Material_MSAP_SmarTeam_JMSToHTTP.jar (1.1).
- After Send to SmarTeam: property `CH_SmarTeamWorkId` (xpath `/InboundResponse/WorkId`) in the response Content Modifier `CallActivity_734112`, then a new Script step "Set Custom Header" (`UTIL_LogCustomHeaders`). Earlier CH_ headers stay (CPI adds only new values)
- Set Monitoring Identifiers XPaths without local-name(): `/*/ProductMDMReplicateRequestMessage/Product/ProductInternalID` (CH_Material, SAP_ApplicationID) and `…/Product/ProductTypeCode` (CH_MaterialType). `/*` because only the root element has a namespace (WSDL: child elements unqualified)
- Removed unused parameters: all `JMSReceiver_*` / `JMSSender_*` (the sender is ProcessDirect), `MaxRetries`, `SAP_Message_name`
- iflw file `I0579_CostCentre…JMSToSOAP.iflw` → `I2018_Material_MSAP_SmarTeam_JMSToHTTP.iflw`
