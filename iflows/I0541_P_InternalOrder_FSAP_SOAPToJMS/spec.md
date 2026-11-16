# I0541_P_InternalOrder_FSAP_SOAPToJMS

Receives the FSAP InternalOrderBulkReplicateRequest (SOAP), splits it per internal order (Internal Order Splitter, moved here from the child), determines receivers (Medius via the dispatcher queue `I0710_Medius` with the child `I0541_InternalOrder_FSAP_Medius_PDToREST`), and sends one JMS message per receiver.

- Source: `_reference/iflows/FSAP_Controlling_MasterData.zip` → `I0541_P_InternalOrder_FSAP_SOAPToJMS` (v1, QUEUE_INDEX loop)
- Build: `py -I tools/iflow_build_fsap_dispatcher.py --only I0541_P_InternalOrder_FSAP_SOAPToJMS` (`_build_parent`, `apply_new_loop_to_parent_iflw`, `fix_parent_diagram`)
- Pattern: Iterating Splitter + `arr_*` lists, taken from `_reference/iflows/I2018_P_Material_MSAP_SOAPToJMS.zip`. Decisions on the dispatcher architecture are in `docs/questions/iflow_architecture_questions.md`.

## Decisions
| Date | Question | Answer | Impact |
|---|---|---|---|
| 2026-11-16 | 2.0.0 in CPI: Main Process gap and arrow to nothing, no arrows in Send to Receivers (L2, user screenshot of I0539_P) | Apply the I0539 child lesson: the build updates the diagram too, and the model's incoming/outgoing must match the flows | 2.0.1: `fix_parent_diagram`. The build check now also compares incoming/outgoing with the flows |
| 2026-11-16 | Role, CSRF and externalization for the parent (L2: "apply the role, CSRF and externalization to the parents too") | Same names and values as the children (`HTTP_*`, `PD_*`), plus `JMS_*` for the JMS receiver | 2.1.0 |
| 2026-11-16 | Leftover `IO_QUEUES` row (`{{IO_QUEUES}}`) found by the parameter check | Removed. The new ReceiverDetermination does not read it | Configure no longer shows `IO_QUEUES, I0541_MEDIUS,I0542_MOBILE` |
