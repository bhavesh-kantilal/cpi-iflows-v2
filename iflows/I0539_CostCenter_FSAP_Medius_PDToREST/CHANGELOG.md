# CHANGELOG — I0539_CostCenter_FSAP_Medius_PDToREST

## 1.1.0 — 2026-11-16 10:05 CET
Feedback on 1.0.0 (feedback/I0539_Feedback.docx, CPI download 1.0.1):
- Fixed the missing connection Start → Main Process → End in "Integration Process from Source". The diagram now has edges for the new flows, and the leftover shapes and edges of the removed DLQ steps are gone. The layout is taken from Bhavesh's download.
- Retrigger HTTPS: role `SSAB_MessagingSend_InternalOperations`, CSRF off.
- `AlowedCompanies` renamed to `AllowedCompanies` (typo), default `SE78`. A value already configured on the tenant must be set again.
- Externalized both Medius receivers (shared parameters): HTTP_Timeout, HTTP_ProxyType, HTTP_ThrowExceptionOnFailure, HTTP_Authentication, HTTP_RetryOnConnectionFailure, HTTP_RetryIterations, HTTP_RetryInterval, HTTP_AllowedRequestHeaders, HTTP_AllowedResponseHeaders, Medius_Host.
- Also externalized: HTTP_MaxBodySize (Retrigger), PD_Address (ProcessDirect sender), Medius_ErpSourceId (property ErpSourceId in "Set Monitor Identifiers", read by the Form Payload body).
- Removed the unused parameters ssabQA, QUEUE_NAME and MaxRetries.
- No UDFs added.

## 1.0.0 — 2026-11-15
New Medius child. ProcessDirect entry replacing JMS consumer (I0540_MEDIUS queue). All mapping, company filter, and UserResponsible logic carried over from I0540 unchanged. Bhavesh, no UDFs were added; ReplaceWithVirtualCompany.groovy copied unchanged from I0540.
