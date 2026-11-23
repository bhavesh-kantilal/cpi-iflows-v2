# CHANGELOG — I2024_P_FunctionLocation_COD_FUNCTIONAL_LOCATION_SAVE_COD_FUNCTIONAL_LOCATION_SAVE01_MSAP_IDocToJMS

## 1.0.11 — 2026-11-23 11:07 CET
- Externalized `PD_Address` (ProcessDirect sender address, default `/<iFlow name>`; keep it equal to what its callers use).
- Externalized `HTTPS_Address` (retrigger path, default `/<iFlow name>`).
- Externalized `HTTPS_BodySize` (40), `HTTPS_CSRF_Protected` (0).
- Externalized JMS receiver: `JMS_CompressStoredMessage` (1), `JMS_Encryptstoredmessage` (1), `JMS_TransferExchangeProperties` (0), names as in I2023_P.
- New build check: no fixed adapter value left (except the shared mail utility's ProcessDirect address).

## 1.0.10 — 2026-11-23 10:44 CET
- JMS send step "Send TO CI" → "Send To JMS".

## 1.0.9 — 2026-11-23 10:39 CET
- Every logCustomHeaders.groovy step is now named `LogCustomHeaders` (was 'Log Custom Headers').

## 1.0.8 — 2026-11-23 10:25 CET
Built from MSAPControllingMasterData_artifacts (4).zip → I2024_P_… (1.0.7).
- `SAP_MessageType` held the value twice (`COD_FUNCTIONAL_LOCATION_SAVE.COD_FUNCTIONAL_LOCATION_SAVE01COD_FUNCTIONAL_…`) → `COD_FUNCTIONAL_LOCATION_SAVE.COD_FUNCTIONAL_LOCATION_SAVE01`
- Removed unused parameter `AttachmentName`
- iflw file `I2023_P_Equipment_…_IDocToJMS.iflw` → `I2024_P_FunctionLocation_…_IDocToJMS.iflw`
