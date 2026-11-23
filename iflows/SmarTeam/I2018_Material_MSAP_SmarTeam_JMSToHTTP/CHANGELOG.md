# CHANGELOG — I2018_Material_MSAP_SmarTeam_JMSToHTTP

## 1.1.1 — 2026-11-23 10:25 CET
Built from I2018_Material_MSAP_SmarTeam_JMSToHTTP.jar (1.1).
- After Send to SmarTeam: property `CH_SmarTeamWorkId` (xpath `/InboundResponse/WorkId`) in the response Content Modifier `CallActivity_734112`, then a new Script step "Set Custom Header" (`UTIL_LogCustomHeaders`). Earlier CH_ headers stay (CPI adds only new values)
- Set Monitoring Identifiers XPaths without local-name(): `/*/ProductMDMReplicateRequestMessage/Product/ProductInternalID` (CH_Material, SAP_ApplicationID) and `…/Product/ProductTypeCode` (CH_MaterialType). `/*` because only the root element has a namespace (WSDL: child elements unqualified)
- Removed unused parameters: all `JMSReceiver_*` / `JMSSender_*` (the sender is ProcessDirect), `MaxRetries`, `SAP_Message_name`
- iflw file `I0579_CostCentre…JMSToSOAP.iflw` → `I2018_Material_MSAP_SmarTeam_JMSToHTTP.iflw`
