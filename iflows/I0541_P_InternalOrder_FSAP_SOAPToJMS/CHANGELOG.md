# CHANGELOG — I0541_P_InternalOrder_FSAP_SOAPToJMS

## 2.0.1 — 2026-11-16 11:10 CET
Bhavesh's first look at the 2.0.0 parents (I0539_P screenshot): Main Process had a gap with an arrow to nothing, and Send to Receivers had no arrows.
- Model fix: "Log Payload" still listed the removed flow `SequenceFlow_30` as incoming. Its incoming/outgoing now match the flows.
- Diagram: removed the leftover shapes and edges of the removed loop steps (Set Receiver Determination Identifiers, AddQueueIndex, SetQueueNameHeader, RestorePayload, loop gateway).
- Wiring fix: v2.0.0 had two flows from "Set Monitoring Identifiers" to "Internal Order Splitter" (`SequenceFlow_29` and a duplicate `SequenceFlow_IOSplit_in`). The duplicate is removed.
- Main Process: drew "Internal Order Splitter" (it had no shape) between Set Monitoring Identifiers and Log Payload, with its arrows.
- Send to Receivers: drew "Get Current Index Receiver" and the arrows Start → Get Current Index Receiver → Send → End. The JMS receiver sits under Send.
- No logic or parameter changes.

## 2.0.0 — 2026-11-15
Migrated to new Iterating Splitter + arr_* pattern. ASAP gateway removed (ASAP decommissioned). Internal Order Splitter moved to parent (before ReceiverDetermination). Only Medius receiver via I0702_Medius dispatcher. IO_QUEUES (was empty) removed.

