# CHANGELOG — I2049_P_MaterialBOM_MSAP_AMQPToJMS

## 1.0.4 — 2026-11-23 10:25 CET
Built from MSAPPlantMaintenanceMasterData_artifacts (1).zip → I2049_P_MaterialBOM_MSAP_AMQPToJMS (1.0.3).
- ReceiverDetermination.groovy: child `I2049_MaterialBOM_MSAP_SmarTeam_PDToHTTP` → `I2049_MaterialBOM_MSAP_SmarTeam_JMSToHTTP`. Deploy together with the child
- Step "Intial Properties" → "Initial Properties"
- Removed 18 unused parameters: `Address`, `Authorization`, `CSRF Protected`, `CSRF_Protected`, `Contition`, `Credential Name`, `Custom Query Options`, `HTTP_Address` (was `/I2049_P_…`), `Location ID`, `Reuse Connection`, `S4`, `S4_Address`, `S4_Authentication`, `S4_CSRF`, `S4_Credential`, `S4_LocationID`, `S4_Proxy`, `UserRole`
- Renamed spaced parameters: `S4 Address`→`S4_Address`, `S4 Authentication`→`S4_Authentication`, `S4 Credential Name`→`S4_CredentialName`, `S4 Location ID`→`S4_LocationID`, `S4 CSRF Protected`→`S4_CSRFProtected`, `S4 Reuse Connection`→`S4_ReuseConnection`, `proxy Type`→`S4_ProxyType`, `Body Size`→`HTTPS_BodySize`. **Set tenant values again**
- OData Lookup BOM: `S4_CSRFProtected=false` (GET); Delete Idle Connection → `{{S4_DeleteIdleConnection}}` (true), Idle Timeout → `{{S4_IdleTimeout}}` (300), as in I2050_P
- iflw file `I0040_P_EDI_DESADV_B30_AMQPToJMS.iflw` → `I2049_P_MaterialBOM_MSAP_AMQPToJMS.iflw`
