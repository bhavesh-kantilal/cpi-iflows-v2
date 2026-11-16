# CHANGELOG — I0545_WBSElement_FSAP_Medius_PDToREST

## 1.1.0 — 2026-11-16 10:20 CET
Same changes as I0539 1.1.0 (tested OK by Bhavesh 2026-11-16):
- Fixed the missing connection Start → Main Process → End in "Integration Process from Source". Removed the leftover shapes and edges of the DLQ steps.
- Retrigger HTTPS: role `SSAB_MessagingSend_InternalOperations`, CSRF off.
- `AlowedCompanies` renamed to `AllowedCompanies` (typo), default `SE78`. A value already configured on the tenant must be set again.
- Externalized both Medius receivers (shared parameters): HTTP_Timeout, HTTP_ProxyType, HTTP_ThrowExceptionOnFailure, HTTP_Authentication, HTTP_RetryOnConnectionFailure, HTTP_RetryIterations, HTTP_RetryInterval, HTTP_AllowedRequestHeaders, HTTP_AllowedResponseHeaders, Medius_Host.
- Also externalized: HTTP_MaxBodySize, PD_Address, Medius_ErpSourceId (property ErpSourceId in "Set Monitoring Identifiers", read by the "Form Payload" body). The proxy type of the FSAP OData receiver is now `FSAP_ProxyType` (sapcc), matching the other FSAP_* settings.
- Removed the unused parameters QUEUE_NAME and MaxRetries.
- No UDFs added.

## 1.0.0 — 2026-11-15
New Medius child. ProcessDirect entry replacing JMS consumer (I0545_MEDIUS queue). OData lookup stays inside child unchanged. All REST/mapping logic carried over from I0545 (JMSToREST). Bhavesh, no UDFs were added; ReplaceWithVirtualCompany.groovy copied unchanged.
