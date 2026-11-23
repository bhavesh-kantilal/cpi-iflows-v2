# CHANGELOG — I2050_MaintenanceBOM_MSAP_SmarTeam_JMSToHTTP

## 1.0.8 — 2026-11-23 11:03 CET
- SmarTeam HTTP receiver externalized (12 settings, shared `SmarTeam_*` set): `SmarTeam_Address`, `SmarTeam_ProxyType`, `SmarTeam_Authentication`, `SmarTeam_Timeout`, `SmarTeam_ThrowExceptionOnFailure`, `SmarTeam_RetryOnConnectionFailure`, `SmarTeam_RetryIterations`, `SmarTeam_RetryInterval`, `SmarTeam_RetryOnException`, `SmarTeam_AllowedRequestHeaders`, `SmarTeam_AllowedResponseHeaders`, `SmarTeam_IdleTimeout`. Defaults = the previous fixed values.

## 1.0.7 — 2026-11-23 10:39 CET
- Every logCustomHeaders.groovy step is now named `LogCustomHeaders` (was 'Set Custom Header' (2 steps)).

## 1.0.6 — 2026-11-23 10:31 CET
- Allowed Headers (`{{AllowedHeaders}}`) now defaults to `SSAB.*|SAP.*` (was `SSAB.*`). Set the tenant value again if it was configured.

## 1.0.5 — 2026-11-23 10:25 CET
- Set Monitoring Identifiers XPaths fixed: they pointed to `A_MaintBillOfMaterial`, which is not in the message. Now `/BOMHeader/MaintBOMHeader_Type/BillOfMaterial`, `…/BillOfMaterialCategory`, `…/BillOfMaterialVariant`, `…/Plant`, `…/TechnicalObject` (also SAP_ApplicationID). CH_BillOfMaterialVariant read `BillOfMaterialCategory` before; it now reads `BillOfMaterialVariant`.
- No `local-name()` anymore. The WorkId XPath is `/InboundResponse/WorkId`.

## 1.0.4 — 2026-11-23 10:00 CET
Built from Bhavesh's export 1.0.3 (`I2050_MaintananceBOM_MSAP_SmarTeam_PDToHTTP.jar`).
- Renamed from `I2050_MaintananceBOM_MSAP_SmarTeam_PDToHTTP`: the typo is fixed and the name follows the new `_JMSToHTTP` naming. The ProcessDirect address and the HTTPS retrigger path are now `/I2050_MaintenanceBOM_MSAP_SmarTeam_JMSToHTTP`. SAP_MessageType is `MaintenanceBOM`.
- "Error End 1" in Integration Process from Source is now a normal Message End, so messages complete successfully.
- After Send to SmarTeam, the WorkId from the response is logged as custom header `SmarTeamWorkId` (property `CH_SmarTeamWorkId` + new Set Custom Header step).
- Removed 16 unused parameters (JMSReceiver_*, JMSSender_*, MaxRetries, SAP_Message_name).
- The iflw file is renamed to `I2050_MaintenanceBOM_MSAP_SmarTeam_JMSToHTTP.iflw`.
