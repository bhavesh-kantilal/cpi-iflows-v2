# CHANGELOG — I2018_P_Material_MSAP_SOAPToJMS

## 1.0.18 — 2026-11-23 10:39 CET
- Every logCustomHeaders.groovy step is now named `LogCustomHeaders` (was 'Log Custom Header').

## 1.0.17 — 2026-11-23 10:25 CET
Built from MSAPControllingMasterData_artifacts (4).zip → I2018_P_Material_MSAP_SOAPToJMS (1.0.16).
- Set Monitoring Identifiers XPaths without local-name(): CH_Material = `/*/ProductMDMReplicateRequestMessage/Product/ProductInternalID`, CH_MessageID = `/*/MessageHeader/ID` (only the root element has a namespace)
- iflw file `I2017_P_Material_ASAP_FSAP_SOAPToJMS.iflw` → `I2018_P_Material_MSAP_SOAPToJMS.iflw`. No unused parameters
