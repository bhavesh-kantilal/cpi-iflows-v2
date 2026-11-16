# I0539_P_CostCenter_FSAP_SOAPToJMS

Receives the FSAP CostCentreReplicationBulkRequest (SOAP), determines receivers (`ReceiverDetermination.groovy`: Medius via the dispatcher queue `I0710_Medius` with the child `I0539_CostCenter_FSAP_Medius_PDToREST`; Oracle via its own queue `I0539_ORACLE`), and sends one JMS message per receiver (Iterating Splitter over `arr_receiversQueueList`).

- Source: `_reference/iflows/FSAP_Controlling_MasterData.zip` → `I0539_P_CostCenter_FSAP_SOAPToJMS` (v1, QUEUE_INDEX loop)
- Build: `py -I tools/iflow_build_fsap_dispatcher.py --only I0539_P_CostCenter_FSAP_SOAPToJMS` (`_build_parent`, `apply_new_loop_to_parent_iflw`, `fix_parent_diagram`)
- Pattern: Iterating Splitter + `arr_*` lists, taken from `_reference/iflows/I2018_P_Material_MSAP_SOAPToJMS.zip`. Decisions on the dispatcher architecture are in `docs/questions/iflow_architecture_questions.md`.

## Decisions
| Date | Question | Answer | Impact |
|---|---|---|---|
| 2026-11-16 | 2.0.0 in CPI: Main Process gap and arrow to nothing, no arrows in Send to Receivers (L2, user screenshot of I0539_P) | Apply the I0539 child lesson: the build updates the diagram too, and the model's incoming/outgoing must match the flows | 2.0.1: `fix_parent_diagram`. The build check now also compares incoming/outgoing with the flows |
| 2026-11-16 | User's CPI version 2.0.3 (feedback/I0539_P_CostCenter_FSAP_SOAPToJMS.zip, L2) | **Not taken over into the build yet** (the user is testing Cost Center end to end with the CPI version) | Differences from build 2.0.1: (1) ReceiverDetermination adds a third receiver `I0540_MSAP` (dedicated queue, dummy iFlow name). (2) The role is externalized as `SendingUserRole` (I0541_P/I0545_P 2.1.0 use `HTTP_UserRole`, like the children). CSRF, body size, PD and JMS settings are still hard-coded. (3) `P_IO_QUEUES=I0540_MEDIUS,I0540_MSAP,I0539_ORACLE` is still in parameters.prop, but nothing uses it |
