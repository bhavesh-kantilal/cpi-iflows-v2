# I0545_P_WBSElement_FSAP_SOAPToJMS

Receives the FSAP WBSElementMasterDataReplicationBulkRequest (SOAP), determines receivers (Medius via the dispatcher queue `I0710_Medius` with the child `I0545_WBSElement_FSAP_Medius_PDToREST`; Mobile via its own queue `I0546_MOBILE`), and sends one JMS message per receiver.

- Source: `_reference/iflows/FSAP_Controlling_MasterData.zip` → `I0545_P_WBSElement_FSAP_SOAPToJMS` (v1, QUEUE_INDEX loop)
- Build: `py -I tools/iflow_build_fsap_dispatcher.py --only I0545_P_WBSElement_FSAP_SOAPToJMS` (`_build_parent`, `apply_new_loop_to_parent_iflw`, `fix_parent_diagram`)
- Pattern: Iterating Splitter + `arr_*` lists, taken from `_reference/iflows/I2018_P_Material_MSAP_SOAPToJMS.zip`. Decisions on the dispatcher architecture are in `docs/questions/iflow_architecture_questions.md`.

## Decisions
| Date | Question | Answer | Impact |
|---|---|---|---|
| 2026-11-16 | 2.0.0 in CPI: Main Process gap and arrow to nothing, no arrows in Send to Receivers (L2, user screenshot of I0539_P) | Apply the I0539 child lesson: the build updates the diagram too, and the model's incoming/outgoing must match the flows | 2.0.1: `fix_parent_diagram`. The build check now also compares incoming/outgoing with the flows |
