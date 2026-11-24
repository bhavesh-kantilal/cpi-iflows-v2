# Tibnor_SSAB_EDIMigration: status and open points

Status on 2026-11-24, for the next session. Details per iFlow and mapping are in its `spec.md` (Decisions) and `CHANGELOG.md`.

## What is built
| Direction | Parent | Children | Build |
|---|---|---|---|
| ORDERS out (Tibnor S4 → hub) | `IXXXX_P_PurchaseOrder_ORDERS_ORDERS02_TibnorS4_IDocToJMS` 1.0.2 | `IXXXX_PurchaseOrder_…_HameenlinnaMetocs_JMSToMQ` 1.0.1 | `tools/iflow_build_tibnor.py` |
| ORDRSP in (hub → Tibnor S4) | `IXXXX_P_OrderResponse_FinMessageHub_MQToJMS` 1.0.0 | 3 × `IXXXX_OrderResponse_FinMessageHub_<Mill>_TibnorS4_JMSToIDoc` 1.0.1 | `tools/iflow_build_tibnor_inbound.py --flow ORDRSP` |
| DESADV in | `IXXXX_P_DespatchAdvice_FinMessageHub_MQToJMS` 1.0.0 | 3 × `IXXXX_DespatchAdvice_…_JMSToIDoc` 1.0.1 | `… --flow DESADV` |
| INVOIC in | `IXXXX_P_Invoice_FinMessageHub_MQToJMS` 1.0.0 | 3 × `IXXXX_Invoice_…_JMSToIDoc` 1.0.1 | `… --flow INVOIC` |

`<Mill>` = HameenlinnaMetocs / HameenlinnaTilkku / RaaheTilkku. The children contain the mappings of `mappings/2,3,4,7,8,9,11,12,13` byte-identical to their `build/` zips.

Routing:
- ORDRSP: `Header/ApplicationId` (METOCS* / TILKKUHA / TILKKURA)
- DESADV / INVOIC: recipient GLN in `FinMessageHub_AllowedRecipients`, then SourceSystem METOCS*, else the mill GLN (InterchangeSender)

## Tested by the user (L2)
- Metocs ORDRSP mapping: OK (2026-11-24). Feedback: EDI_DC40 without a condition (now a rule, applied).
- Metocs INVOIC mapping: mill check and MWSKZ split removed (rules, applied to all 9 inbound mappings, 2026-11-24).
- iFlow Namespace Mapping (`xmlns:p1=…`): works in CPI.

## Open points
1. **Not tested yet:** the Metocs DESADV mapping, all Tilkku mappings, and all inbound iFlows on the tenant.
2. **User reminder:** review E1EDK03 of the Metocs ORDRSP in detail (`mappings/2_…/spec.md`, Q3). The ORDRSP test was OK; confirm with the user that this is covered.
3. **Explain Q4 to the user:** the E1EDK01 BSART/FKART_RL/FKTYP field-level `DocumentType = 380` checks in INVOIC are kept for now (`mappings/4_…/spec.md`).
4. **Not built here:** dispatcher `IXXXX_TibnorS4`; `T0143_P_IDocReceiver_TibnorS4_PDToIDoc` is assumed to exist. Deploy order: children → dispatcher → T0143 → parents.
5. **Interface numbers:** every flow is `IXXXX`. Change `NUMBER` in `tools/iflow_build_tibnor.py` when decided (dispatcher numbers I07xx/I08xx come from the Central Integration team).
6. **Tenant values:**
   - `IBMMQ_QueueName` / `IBMMQ_DLQueueName` in the 3 inbound parents
   - `TibnorS4_SNDPOR/RCVPOR/RCVPRN` in the 9 children
7. **Ask the user:** the ORDRSP parent has no recipient-GLN check (DESADV / INVOIC have one). Add it?
8. **Template leftovers in all parents:**
   - `SAP_MessageProcessingLogCustomStatus` is a constant holding an expression
   - FLAG §3.8.2 "Required for JMS"
9. **Possible simplification:** the two Tilkku mappings per message type differ only in SNDPRN / vendor, and the mill GLN check is gone. They could be merged (one mapping, a value table).
10. **Open business points (OP-xx)** in the mapping specs.
11. **Toolkit:** `tools/mm.py selftest` has 2 failures from before this work (`MM_SupplierInvoice_API` brick `Var`, `MapToRFC_SAVE_TEXT` legacy envelope).

## Working notes (tooling)
- **Python on Windows changes line endings.** `Path.write_text` writes CRLF, which flipped every line of CLAUDE.md / REVIEW.md once. Use `write_bytes`, or keep the file's original line ending (see the `edit()` helper in the 2026-11-24 scripts). After a commit, check `git diff --stat` for whole-file changes.
- **Bash tool heredocs with nested quotes fail.** Write longer Python helpers to a file (scratchpad) and run them with `py -I <file>`.
- **`git add` with one wrong path adds nothing**, so the commit then holds only what was staged before. Check `git show --stat HEAD` after each commit.
