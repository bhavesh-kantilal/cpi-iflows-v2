# CHANGELOG — I0539_P_CostCenter_FSAP_SOAPToJMS

## 2.0.0 — 2026-11-15
Migrated to new Iterating Splitter + arr_receiversQueueList pattern. Removed QUEUE_INDEX/QUEUE_LIST_SIZE loop (AddQueueIndex, SetQueueNameHeader, RestorePayload). Medius receiver now uses I0702_Medius dispatcher queue. Oracle receiver keeps I0539_ORACLE dedicated queue (dummy iFlow name). SAP_MessageProcessingLogCustomStatus set per iteration.

