# I2049_MaterialBOM_MSAP_SmarTeam_JMSToHTTP

Child: maps the material BOM and POSTs it to SmarTeam. It is called by the SmarTeam dispatcher over ProcessDirect. Parent: `I2049_P_MaterialBOM_MSAP_AMQPToJMS`.

- Source: `iflows/SmarTeam/source/I2049_MaterialBOM_MSAP_SmarTeam_PDToHTTP.jar (1.0.3)` (Bhavesh's export, 2026-11-23)
- Build: `py -I tools/iflow_build_smarteam.py --only I2049_MaterialBOM_MSAP_SmarTeam_JMSToHTTP` (config in `CHILDREN` / `PARENTS`)

## Decisions
| Date | Question | Answer | Impact |
|---|---|---|---|
| 2026-11-23 | Same round as I2050 (L2, user: "change the remaining iFlows") | Applied | Renamed from `I2049_MaterialBOM_MSAP_SmarTeam_PDToHTTP` (new `_JMSToHTTP` naming). PD address and HTTPS retrigger path are now `/I2049_MaterialBOM_MSAP_SmarTeam_JMSToHTTP`. CPI imports it as a new artifact |
| 2026-11-23 | Same round as I2050 (L2, user: "change the remaining iFlows") | Applied | "Error End 1" in Integration Process from Source → Message End (success) |
| 2026-11-23 | Same round as I2050 (L2, user: "change the remaining iFlows") | Applied | After Send to SmarTeam: property `CH_SmarTeamWorkId` (xpath `/InboundResponse/WorkId`) in the response Content Modifier `I2049_CA_SetAtt`, then a new Script step "Set Custom Header" (`UTIL_LogCustomHeaders`). Earlier CH_ headers stay (CPI adds only new values) |
| 2026-11-23 | Same round as I2050 (L2, user: "change the remaining iFlows") | Applied | Set Monitoring Identifiers XPaths fixed and without local-name(): they skipped the `MaterialBOMType` level (`MaterialBOM_Input.xsd`). Now `/MaterialBOM/MaterialBOMType/BillOfMaterial`, `…/BillOfMaterialCategory`, `…/BillOfMaterialVariant` (CH_BillOfMaterialVariant read `BillOfMaterialVariantUsage`), `…/Plant`, `…/Material` (CH_Material + SAP_ApplicationID) |
| 2026-11-23 | Same round as I2050 (L2, user: "change the remaining iFlows") | Applied | Removed unused parameters: all `JMSReceiver_*` / `JMSSender_*` (the sender is ProcessDirect), `MaxRetries`, `SAP_Message_name` |
| 2026-11-23 | Same round as I2050 (L2, user: "change the remaining iFlows") | Applied | iflw file `I0579_CostCentre…JMSToSOAP.iflw` → `I2049_MaterialBOM_MSAP_SmarTeam_JMSToHTTP.iflw` |
| 2026-11-23 | Step name of the logCustomHeaders.groovy step (L2, user, screenshot: "LogCustomHeaders" for all iFlows) | `LogCustomHeaders` | 1.0.5: renamed from 'Set Custom Header' (2 steps). The build names every such step this way and fails on any other name |
| 2026-11-23 | SmarTeam adapter not externalized (L2, user: "we always externalize adapters"; rule already in CLAUDE.md, missed in the first round) | Externalize every setting of the SmarTeam HTTP receiver | 1.0.6: 12 `SmarTeam_*` parameters, defaults = old fixed values, propdef references like the I0539 Medius receiver (L3). `SmarTeam_RetryOnException` and `SmarTeam_IdleTimeout` (pooledConnectionIdleTimeout, ms) are not in the I0539 set: UNVERIFIED until the CPI test |
| 2026-11-23 | Remaining fixed adapter settings (L2, user: "all of them") | Externalize; defaults = old values | 1.0.7: `PD_Address` (ProcessDirect sender address, default `/<iFlow name>`; **must stay equal to the iFlow name**: the dispatcher calls it); `HTTPS_Address` (retrigger path, default `/<iFlow name>`). Build check `fixed_adapter_values` |
