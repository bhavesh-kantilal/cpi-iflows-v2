# I0541_InternalOrder_FSAP_Medius_PDToREST

Child iFlow of the FSAP → Medius dispatcher pattern. `I0541_P_InternalOrder_FSAP_SOAPToJMS` splits per internal order and puts each one on queue `I0710_Medius`. `I0710_P_JMSDispatcher_Medius` calls this flow over ProcessDirect `/I0541_InternalOrder_FSAP_Medius_PDToREST`. The flow maps the order to Medius JSON (DIMENSION3) and POSTs it to Medius. It also updates User Responsible.

- Source: `_reference/iflows/FSAP_Controlling_MasterData.zip` → `I0541_InternalOrder_FSAP_Medius_JMSToREST`. The Internal Order Splitter was removed and moved to the parent.
- Build: `py -I tools/iflow_build_fsap_dispatcher.py --only I0541_InternalOrder_FSAP_Medius_PDToREST` (`build_i0541_child`, `pd_child_feedback_v110`)
- Shared helpers: `tools/iflow_lib.py`

## Externalized parameters (v1.1.0)
Same set as I0539 (see `iflows/I0539_CostCenter_FSAP_Medius_PDToREST/spec.md`), with these differences:
- No `HTTP_AllowedRequestHeaders`. "Allowed Request Headers" is empty in both Medius channels of the source flow, so it is left empty.
- Content Modifiers: `ErpSourceId` is set in "Set Monitoring Identifiers", and the Medius body step is "Set Payload".
- `SAP_MessageType=InternalOrderBulkReplicateRequest`.

## Decisions
| Date | Question | Answer | Impact |
|---|---|---|---|
| 2026-11-16 | Apply the I0539 v1.1.0 feedback to this flow? | Yes (user: "do the same for the remaining 2 Medius child flows") | Diagram fix, role/CSRF, SE78, shared `HTTP_*` params, Medius_Host, HTTP_MaxBodySize, PD_Address, Medius_ErpSourceId |
| 2026-11-16 | Retrigger HTTPS address was `/I0541_InternalOrder_FSAP_Medius_SOAPToREST`. The v1.0.0 build only replaced names ending in `JMSToREST` (L4, build bug) | Set to `/I0541_InternalOrder_FSAP_Medius_PDToREST`, the same as I0539/I0545 | The Retrigger URL changes |
| 2026-11-16 | Allowed Request Headers is empty here, but `Content-Type` in I0539/I0545 | Left as it is. Only non-empty values are externalized | No `HTTP_AllowedRequestHeaders` parameter. User 2026-11-16: "does not matter, ignore" |
| 2026-11-16 | The diagram had a gap where the splitter was | The `SequenceFlow_30` arrow is redrawn across the gap. The step positions are unchanged | Cosmetic only |
