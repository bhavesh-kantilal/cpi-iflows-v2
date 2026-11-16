# CHANGELOG — I0541_InternalOrder_FSAP_Medius_PDToREST

## 1.1.0 — 2026-11-16 10:20 CET
Same changes as I0539 1.1.0 (tested OK by Bhavesh 2026-11-16):
- Fixed the missing connection Start → Main Process → End in "Integration Process from Source". Removed the leftover shapes and edges of the DLQ steps and of the Internal Order Splitter (moved to the parent). The arrow that crosses the gap where the splitter was is redrawn.
- Retrigger HTTPS: role `SSAB_MessagingSend_InternalOperations`, CSRF off, and address fixed to `/I0541_InternalOrder_FSAP_Medius_PDToREST`. It was still `/I0541_InternalOrder_FSAP_Medius_SOAPToREST`.
- `AllowedCompanies` default `SE78` (no typo in this flow).
- Externalized both Medius receivers (shared parameters): HTTP_Timeout, HTTP_ProxyType, HTTP_ThrowExceptionOnFailure, HTTP_Authentication, HTTP_RetryOnConnectionFailure, HTTP_RetryIterations, HTTP_RetryInterval, HTTP_AllowedResponseHeaders, Medius_Host. "Allowed Request Headers" is empty in both channels here, so it was left as it is.
- Also externalized: HTTP_MaxBodySize, PD_Address, Medius_ErpSourceId (property ErpSourceId in "Set Monitoring Identifiers", read by the "Set Payload" body).
- Removed the unused parameters QUEUE_NAME and MaxRetries.
- No UDFs added.

## 1.0.0 — 2026-11-15
New Medius child. ProcessDirect entry replacing JMS consumer (I0541_MEDIUS queue). Internal Order Splitter moved to I0541_P parent; child processes one order at a time. All REST/mapping logic carried over unchanged from I0541 (JMSToREST). Bhavesh, no UDFs were added; ReplaceWithVirtualCompany.groovy copied unchanged.
