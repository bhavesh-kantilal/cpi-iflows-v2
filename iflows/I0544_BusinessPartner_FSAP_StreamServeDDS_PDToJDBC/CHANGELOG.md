# CHANGELOG — I0544_BusinessPartner_FSAP_StreamServeDDS_PDToJDBC

## 1.0.0 — 2026-11-16 11:55 CET
New StreamServe child for BP. ProcessDirect entry replaces the JMS consumer of the `I0544_StreamServeDDS` queue. DLQ handling is now in the new I0711.
- I0539 lessons applied: consistent diagram, Retrigger role and CSRF off, address, `HTTP_MaxBodySize`, `PD_Address`.
- JDBC parameters renamed to the `JDBC_*` convention: `JDBC_Alias`, `JDBC_ConnectionTimeout` (typo `ConnectionTImeout` fixed), `JDBC_QueryTimeout`. Newly externalized: `JDBC_PageSize`, `JDBC_BatchMode`, `JDBC_BatchOperation`. Set the values again on the tenant.
- Removed the unused `Medius_Credentials`, `ssabQA`, `QUEUE_NAME` and `MaxRetries`. `SAP_Sender=FD1_110`. No UDFs added.
