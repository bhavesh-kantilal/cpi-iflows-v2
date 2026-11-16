# CHANGELOG — I0544_BusinessPartner_FSAP_Medius_PDToREST

## 1.0.0 — 2026-11-16 11:55 CET
New Medius child for BP. ProcessDirect entry replaces the JMS consumer of the `I0544_MEDIUS` queue. DLQ handling is now in I0710.
- I0539 lessons applied:
  - consistent diagram
  - Retrigger role `SSAB_MessagingSend_InternalOperations`, CSRF off, address `/I0544_BusinessPartner_FSAP_Medius_PDToREST`
  - `HTTP_MaxBodySize`, `PD_Address`
  - shared `HTTP_*` Medius receiver parameters and `Medius_Host`
- `{{ssabQA}}` renamed to `{{tenantName}}` (user). Set the value again on the tenant.
- The account-information splitter stays in the child, because Medius wants one message per supplier/company code.
- Removed `QUEUE_NAME`, `MaxRetries`. `SAP_Sender=FD1_110`. No UDFs added.
