# CHANGELOG — I0545_P_WBSElement_FSAP_SOAPToJMS

## 2.0.1 — 2026-11-16 11:10 CET
Bhavesh's first look at the 2.0.0 parents (I0539_P screenshot): Main Process had a gap with an arrow to nothing, and Send to Receivers had no arrows.
- Model fix: "Log Payload" still listed the removed flow `SequenceFlow_30` as incoming. Its incoming/outgoing now match the flows.
- Diagram: removed the leftover shapes and edges of the removed loop steps (Set Receiver Determination Identifiers, AddQueueIndex, SetQueueNameHeader, RestorePayload, loop gateway).
- Main Process: closed the gap after "Set Monitoring Identifiers". The steps after it move 160 px left and the pool shrinks to fit.
- Send to Receivers: drew "Get Current Index Receiver" (it had no shape) and the arrows Start → Get Current Index Receiver → Send → End. The JMS receiver sits under Send.
- No logic or parameter changes.

## 2.0.0 — 2026-11-15
Migrated to new Iterating Splitter + arr_* pattern. Medius receiver uses I0702_Medius dispatcher queue. Mobile receiver keeps I0546_MOBILE dedicated queue (dummy iFlow name). Removed malformed IO_QUEUES parameter artifact.

