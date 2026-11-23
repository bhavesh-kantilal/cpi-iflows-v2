# CHANGELOG — I2050_MaintenanceBOM_MSAP_SmarTeam_JMSToHTTP

## 1.0.4 — 2026-11-23 10:00 CET
Built from Bhavesh's export 1.0.3 (`I2050_MaintananceBOM_MSAP_SmarTeam_PDToHTTP.jar`).
- Renamed from `I2050_MaintananceBOM_MSAP_SmarTeam_PDToHTTP`: the typo is fixed and the name follows the new `_JMSToHTTP` naming. The ProcessDirect address and the HTTPS retrigger path are now `/I2050_MaintenanceBOM_MSAP_SmarTeam_JMSToHTTP`. SAP_MessageType is `MaintenanceBOM`.
- "Error End 1" in Integration Process from Source is now a normal Message End, so messages complete successfully.
- After Send to SmarTeam, the WorkId from the response is logged as custom header `SmarTeamWorkId` (property `CH_SmarTeamWorkId` + new Set Custom Header step).
- Removed 16 unused parameters (JMSReceiver_*, JMSSender_*, MaxRetries, SAP_Message_name).
- The iflw file is renamed to `I2050_MaintenanceBOM_MSAP_SmarTeam_JMSToHTTP.iflw`.
