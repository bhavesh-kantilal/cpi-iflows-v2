# CHANGELOG — I0544_P_BusinessPartner_FSAP_SOAPToJMS

## 2.0.0 — 2026-11-16 11:55 CET
Migrated to the dispatcher pattern (user, 2026-11-16), the same as I0539_P/I0541_P/I0545_P 2.1.0:
- Iterating Splitter + `arr_*` lists replace the QUEUE_INDEX loop (AddQueueIndex, SetQueueNameHeader and RestorePayload removed).
- ReceiverDetermination routes Medius → `I0710_Medius` (child `I0544_BusinessPartner_FSAP_Medius_PDToREST`), StreamServe → `I0711_StreamServe` (child `I0544_BusinessPartner_FSAP_StreamServeDDS_PDToJDBC`), and MSAP → dedicated queue `I0544_MSAP` (dummy iFlow name).
- The diagram and the incoming/outgoing are consistent (Send to Receivers drawn, no gap in Main Process).
- Externalized: `HTTP_UserRole=SSAB_MessagingSend_InternalOperations`, `HTTP_CSRFProtected=0`, `HTTP_Authorization`, `HTTP_MaxBodySize`, `PD_Address`, `PD_MailAddress`, and the `JMS_*` settings.
- Removed `P_IO_QUEUES` and the IO_QUEUES row. `SAP_Sender=FD1_110`.
