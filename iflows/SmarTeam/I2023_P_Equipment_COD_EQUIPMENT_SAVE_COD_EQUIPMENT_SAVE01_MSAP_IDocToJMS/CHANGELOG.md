# CHANGELOG — I2023_P_Equipment_COD_EQUIPMENT_SAVE_COD_EQUIPMENT_SAVE01_MSAP_IDocToJMS

## 1.0.12 — 2026-11-23 11:41 CET
- `SAP_Sender` default `MSAP` → `AD1_110` (same in all SmarTeam flows).
- Header `SAP_MessageType` was a fixed constant → `{{SAP_MessageType}}` (default `COD_EQUIPMENT_SAVE.COD_EQUIPMENT_SAVE01`).

## 1.0.11 — 2026-11-23 11:23 CET
- Retrigger role `HTTPS_Userrole`: `ESBMessaging.send` → `SSAB_MessagingSend_InternalOperations` (the flow's main entry is IDoc; the HTTPS sender is only the retrigger). Set the tenant value again if it was configured.

## 1.0.10 — 2026-11-23 11:07 CET
- Externalized `HTTPS_BodySize` (retrigger max body size, 40 MB).
- New build check: no fixed adapter value left (except the shared mail utility's ProcessDirect address).

## 1.0.9 — 2026-11-23 10:44 CET
- JMS send step "Send to JMS" → "Send To JMS".

## 1.0.8 — 2026-11-23 10:39 CET
- Every logCustomHeaders.groovy step is now named `LogCustomHeaders` (was 'Log Custom Headers').

## 1.0.7 — 2026-11-23 10:25 CET
Built from MSAPControllingMasterData_artifacts (4).zip → I2023_P_… (1.0.6).
- Removed 8 unused parameters: `AttachmentName`, `CompressStoredMessage`, `Encryptstoredmessage`, `Expirationperiod`, `HTTP_Adress`, `JMS_TransferexchangeProperties`, `RetentionThreshold`, `TransferexchangeProperties`. The iflw file name was already right
