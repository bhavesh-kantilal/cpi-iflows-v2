# CHANGELOG — I0539_P_CostCenter_FSAP_SOAPToJMS

## 2.1.0 — 2026-11-16 11:30 CET
Took over Bhavesh's CPI version 2.0.3 and aligned it with I0541_P/I0545_P 2.1.0 (user: "Align I0539_P to HTTP_*"):
- ReceiverDetermination.groovy is the CPI version unchanged. It adds a third receiver, MSAP: dedicated queue `I0540_MSAP` (dummy iFlow name).
- `SendingUserRole` renamed to `HTTP_UserRole` (`SSAB_MessagingSend_InternalOperations`). **Set it again on the tenant after import.**
- Externalized as in the other parents: `HTTP_CSRFProtected=0`, `HTTP_Authorization=RoleBased`, `HTTP_MaxBodySize=40`, `PD_Address`, `PD_MailAddress`, and `JMS_ExpirationPeriod`, `JMS_RetentionThresholdAlerting`, `JMS_EncryptMessage`, `JMS_UseMessageCompression`, `JMS_TransferExchangeProperties`.
- Default values corrected. The source package carried another interface's defaults (`SAP_Sender=DR1_350`, `SAP_MessageType=BusinessPartnerSUITEBulkReplicateRequest`). Now `SAP_MessageType=CostCentreReplicationBulkRequest` and `SAP_Sender=FD1_110`. The user confirmed FD1_110; CPI 2.0.3 still had FD1-110.
- Removed the unused `P_IO_QUEUES` parameter entry.
- No other logic changes. The process model equals CPI 2.0.3, apart from generated ids.

## 2.0.1 — 2026-11-16 11:10 CET
Bhavesh's first look at the 2.0.0 parents (I0539_P screenshot): Main Process had a gap with an arrow to nothing, and Send to Receivers had no arrows.
- Model fix: "Log Payload" still listed the removed flow `SequenceFlow_30` as incoming. Its incoming/outgoing now match the flows.
- Diagram: removed the leftover shapes and edges of the removed loop steps (Set Receiver Determination Identifiers, AddQueueIndex, SetQueueNameHeader, RestorePayload, loop gateway).
- Main Process: closed the gap after "Set Monitoring Identifiers". The steps after it move 160 px left and the pool shrinks to fit.
- Send to Receivers: drew "Get Current Index Receiver" (it had no shape) and the arrows Start → Get Current Index Receiver → Send → End. The JMS receiver sits under Send.
- No logic or parameter changes.

## 2.0.0 — 2026-11-15
Migrated to new Iterating Splitter + arr_receiversQueueList pattern. Removed QUEUE_INDEX/QUEUE_LIST_SIZE loop (AddQueueIndex, SetQueueNameHeader, RestorePayload). Medius receiver now uses I0702_Medius dispatcher queue. Oracle receiver keeps I0539_ORACLE dedicated queue (dummy iFlow name). SAP_MessageProcessingLogCustomStatus set per iteration.

