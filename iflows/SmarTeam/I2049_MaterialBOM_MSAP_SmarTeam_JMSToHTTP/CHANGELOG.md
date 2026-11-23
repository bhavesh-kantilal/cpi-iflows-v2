# CHANGELOG — I2049_MaterialBOM_MSAP_SmarTeam_JMSToHTTP

## 1.0.4 — 2026-11-23 10:25 CET
Built from I2049_MaterialBOM_MSAP_SmarTeam_PDToHTTP.jar (1.0.3).
- Renamed from `I2049_MaterialBOM_MSAP_SmarTeam_PDToHTTP` (new `_JMSToHTTP` naming). PD address and HTTPS retrigger path are now `/I2049_MaterialBOM_MSAP_SmarTeam_JMSToHTTP`. CPI imports it as a new artifact
- "Error End 1" in Integration Process from Source → Message End (success)
- After Send to SmarTeam: property `CH_SmarTeamWorkId` (xpath `/InboundResponse/WorkId`) in the response Content Modifier `I2049_CA_SetAtt`, then a new Script step "Set Custom Header" (`UTIL_LogCustomHeaders`). Earlier CH_ headers stay (CPI adds only new values)
- Set Monitoring Identifiers XPaths fixed and without local-name(): they skipped the `MaterialBOMType` level (`MaterialBOM_Input.xsd`). Now `/MaterialBOM/MaterialBOMType/BillOfMaterial`, `…/BillOfMaterialCategory`, `…/BillOfMaterialVariant` (CH_BillOfMaterialVariant read `BillOfMaterialVariantUsage`), `…/Plant`, `…/Material` (CH_Material + SAP_ApplicationID)
- Removed unused parameters: all `JMSReceiver_*` / `JMSSender_*` (the sender is ProcessDirect), `MaxRetries`, `SAP_Message_name`
- iflw file `I0579_CostCentre…JMSToSOAP.iflw` → `I2049_MaterialBOM_MSAP_SmarTeam_JMSToHTTP.iflw`
