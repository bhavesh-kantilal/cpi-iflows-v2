# CHANGELOG — I2049_P_MaterialBOM_MSAP_AMQPToJMS

## 1.0.9 — 2026-11-23 12:04 CET
- HTTPS retrigger sender `Trigger` → `Retrigger` (as in every other flow).

## 1.0.8 — 2026-11-23 11:41 CET
- Initial Properties (first Content Modifier): header `SAP_Sender` was a fixed `MSAP` → `{SAP_Sender}` (default `AD1_110`); new header `SAP_MessageType` = `{SAP_MessageType}` (default `MaterialBOM`).
- Receiver participant `MSAP_PO` → `MSAP_BOM` (participant, OData channel `system`, propdef references). Not plain `MSAP`: that is the AMQP sender participant.

## 1.0.7 — 2026-11-23 11:07 CET
- Externalized OData lookup: `S4_RetryIterations` (1) and `S4_RetryInterval` (5).
- New build check: no fixed adapter value left (except the shared mail utility's ProcessDirect address).

## 1.0.6 — 2026-11-23 10:44 CET
- JMS send step "Send 1" → "Send To JMS".

## 1.0.5 — 2026-11-23 10:39 CET
- Every logCustomHeaders.groovy step is now named `LogCustomHeaders` (was 'Log Headers').
- `LogPayloadSize` was an empty constant in Set Monitoring Identifiers (same gap as I2050_P): now `{{LogPayloadSize}}`, new parameter `LogPayloadSize=512`.

## 1.0.4 — 2026-11-23 10:25 CET
Built from MSAPPlantMaintenanceMasterData_artifacts (1).zip → I2049_P_MaterialBOM_MSAP_AMQPToJMS (1.0.3).
- ReceiverDetermination.groovy: child `I2049_MaterialBOM_MSAP_SmarTeam_PDToHTTP` → `I2049_MaterialBOM_MSAP_SmarTeam_JMSToHTTP`. Deploy together with the child
- Step "Intial Properties" → "Initial Properties"
- Removed 18 unused parameters: `Address`, `Authorization`, `CSRF Protected`, `CSRF_Protected`, `Contition`, `Credential Name`, `Custom Query Options`, `HTTP_Address` (was `/I2049_P_…`), `Location ID`, `Reuse Connection`, `S4`, `S4_Address`, `S4_Authentication`, `S4_CSRF`, `S4_Credential`, `S4_LocationID`, `S4_Proxy`, `UserRole`
- Renamed spaced parameters: `S4 Address`→`S4_Address`, `S4 Authentication`→`S4_Authentication`, `S4 Credential Name`→`S4_CredentialName`, `S4 Location ID`→`S4_LocationID`, `S4 CSRF Protected`→`S4_CSRFProtected`, `S4 Reuse Connection`→`S4_ReuseConnection`, `proxy Type`→`S4_ProxyType`, `Body Size`→`HTTPS_BodySize`. **Set tenant values again**
- OData Lookup BOM: `S4_CSRFProtected=false` (GET); Delete Idle Connection → `{{S4_DeleteIdleConnection}}` (true), Idle Timeout → `{{S4_IdleTimeout}}` (300), as in I2050_P
- iflw file `I0040_P_EDI_DESADV_B30_AMQPToJMS.iflw` → `I2049_P_MaterialBOM_MSAP_AMQPToJMS.iflw`
