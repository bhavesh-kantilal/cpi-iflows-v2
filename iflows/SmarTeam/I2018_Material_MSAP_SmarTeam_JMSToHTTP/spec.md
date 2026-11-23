# I2018_Material_MSAP_SmarTeam_JMSToHTTP

Child: maps the material (ProductMDMBulkReplicateRequest) and POSTs it to SmarTeam. Parent: `I2018_P_Material_MSAP_SOAPToJMS`.

- Source: `iflows/SmarTeam/source/I2018_Material_MSAP_SmarTeam_JMSToHTTP.jar (1.1)` (Bhavesh's export, 2026-11-23)
- Build: `py -I tools/iflow_build_smarteam.py --only I2018_Material_MSAP_SmarTeam_JMSToHTTP` (config in `CHILDREN` / `PARENTS`)

## Decisions
| Date | Question | Answer | Impact |
|---|---|---|---|
| 2026-11-23 | Same round as I2050 (L2, user: "change the remaining iFlows") | Applied | After Send to SmarTeam: property `CH_SmarTeamWorkId` (xpath `/InboundResponse/WorkId`) in the response Content Modifier `CallActivity_734112`, then a new Script step "Set Custom Header" (`UTIL_LogCustomHeaders`). Earlier CH_ headers stay (CPI adds only new values) |
| 2026-11-23 | Same round as I2050 (L2, user: "change the remaining iFlows") | Applied | Set Monitoring Identifiers XPaths without local-name(): `/*/ProductMDMReplicateRequestMessage/Product/ProductInternalID` (CH_Material, SAP_ApplicationID) and `…/Product/ProductTypeCode` (CH_MaterialType). `/*` because only the root element has a namespace (WSDL: child elements unqualified) |
| 2026-11-23 | Same round as I2050 (L2, user: "change the remaining iFlows") | Applied | Removed unused parameters: all `JMSReceiver_*` / `JMSSender_*` (the sender is ProcessDirect), `MaxRetries`, `SAP_Message_name` |
| 2026-11-23 | Same round as I2050 (L2, user: "change the remaining iFlows") | Applied | iflw file `I0579_CostCentre…JMSToSOAP.iflw` → `I2018_Material_MSAP_SmarTeam_JMSToHTTP.iflw` |
| 2026-11-23 | Step name of the logCustomHeaders.groovy step (L2, user, screenshot: "LogCustomHeaders" for all iFlows) | `LogCustomHeaders` | 1.1.2: renamed from 'Set Custom Header' (2 steps). The build names every such step this way and fails on any other name |
| 2026-11-23 | SmarTeam adapter not externalized (L2, user: "we always externalize adapters"; rule already in CLAUDE.md, missed in the first round) | Externalize every setting of the SmarTeam HTTP receiver | 1.1.3: 12 `SmarTeam_*` parameters, defaults = old fixed values, propdef references like the I0539 Medius receiver (L3). `SmarTeam_RetryOnException` and `SmarTeam_IdleTimeout` (pooledConnectionIdleTimeout, ms) are not in the I0539 set: UNVERIFIED until the CPI test |
