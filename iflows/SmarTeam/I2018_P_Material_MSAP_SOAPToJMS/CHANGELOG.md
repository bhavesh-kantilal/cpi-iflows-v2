# CHANGELOG — I2018_P_Material_MSAP_SOAPToJMS

## 1.0.23 — 2026-11-23 11:41 CET
- `SAP_Sender` default `MSAP` → `AD1_110` (same in all SmarTeam flows).

## 1.0.22 — 2026-11-23 11:36 CET
- Parameter renamed: `SAP_MESSAGETYPE` → `SAP_MessageType` (header SAP_MessageType = `{{SAP_MessageType}}`). Set the tenant value again if configured.

## 1.0.21 — 2026-11-23 11:23 CET
- Retrigger role `HTTP_UserRole`: `ESBMessaging.send` → `SSAB_MessagingSend_InternalOperations` (the flow's main entry is SOAP; the HTTPS sender is only the retrigger). Set the tenant value again if it was configured.

## 1.0.20 — 2026-11-23 11:07 CET
- Externalized `PD_Address` (ProcessDirect sender address, default `/<iFlow name>`; keep it equal to what its callers use).
- Externalized `HTTPS_Address` (retrigger path, default `/<iFlow name>`).
- New build check: no fixed adapter value left (except the shared mail utility's ProcessDirect address).

## 1.0.19 — 2026-11-23 10:44 CET
- JMS send step "Send" → "Send To JMS".

## 1.0.18 — 2026-11-23 10:39 CET
- Every logCustomHeaders.groovy step is now named `LogCustomHeaders` (was 'Log Custom Header').

## 1.0.17 — 2026-11-23 10:25 CET
Built from MSAPControllingMasterData_artifacts (4).zip → I2018_P_Material_MSAP_SOAPToJMS (1.0.16).
- Set Monitoring Identifiers XPaths without local-name(): CH_Material = `/*/ProductMDMReplicateRequestMessage/Product/ProductInternalID`, CH_MessageID = `/*/MessageHeader/ID` (only the root element has a namespace)
- iflw file `I2017_P_Material_ASAP_FSAP_SOAPToJMS.iflw` → `I2018_P_Material_MSAP_SOAPToJMS.iflw`. No unused parameters
