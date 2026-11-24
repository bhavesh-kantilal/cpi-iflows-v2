# IXXXX_P_Invoice_FinMessageHub_MQToJMS

Parent (package Tibnor_SSAB_EDIMigration): invoices (INVOIC, hub `Invoice` XML) from the Finnish message hub on **IBM MQ** → receiver determination as the PO conditions → JMS queue `IXXXX_TibnorS4` → one child per mill, which posts a INVOIC.INVOIC01 IDoc to Tibnor S4.

- Same shape as `IXXXX_P_OrderResponse_FinMessageHub_MQToJMS` (templates: our ORDERS parent, IBM MQ sender of I2017).
- Build: `py -I tools/iflow_build_tibnor_inbound.py --flow INVOIC --only parent`

## Flow
1. IBM MQ sender (`FinMessageHub`) or HTTPS retrigger → Main Process.
2. Set Monitoring Identifiers:
   - headers `SAP_Sender` = `FinMessageHub`, `SAP_MessageType` = `INVOIC`, `SAP_ApplicationID` = DocumentId/DocumentNo
   - properties logged by LogCustomHeaders: `CH_FinMessageHubSourceSystem` (`/Invoice/Header/SourceSystem`), `CH_PurchaseOrder` (`Reference[@Type='ON'][1]/ReferenceIdentification`)
   - properties for routing only: `FinMessageHubSender` (`/Invoice/Header/InterchangeSender`), `FinMessageHubRecipient` (`/Invoice/Header/RecipientIdentification`), `AllowedRecipients` = `{{FinMessageHub_AllowedRecipients}}`
3. `ReceiverDetermination.groovy` reads the properties; it does not parse the payload. Recipient in `AllowedRecipients`, then:
   - SourceSystem `METOCS*` → `IXXXX_Invoice_FinMessageHub_HameenlinnaMetocs_TibnorS4_JMSToIDoc`
   - else InterchangeSender `00372389445751` → `…_HameenlinnaTilkku_…`, `00372389445741` → `…_RaaheTilkku_…`
   - all on queue `IXXXX_TibnorS4`; anything else → Error End.

## Parameters
As the ORDRSP parent (IBM MQ sender; `IBMMQ_QueueName` / `IBMMQ_DLQueueName` empty: **set on the tenant**), plus:
| Parameter | Default | Note |
|---|---|---|
| `FinMessageHub_AllowedRecipients` | `7340195700006,7080003309006,5790002585623,003723894430` | the PO receiver condition |

## Decisions
| Date | Question | Answer | Impact |
|---|---|---|---|
| 2026-11-24 | Names (L2, user) | Parent `IXXXX_P_Invoice_FinMessageHub_MQToJMS`, children `IXXXX_Invoice_FinMessageHub_<Mill>_TibnorS4_JMSToIDoc` ("DespatchAdvice / Invoice"). Number to be decided | `NUMBER` in `tools/iflow_build_tibnor.py` |
| 2026-11-24 | Shape (L2, user: "similar iflows") | Same as the ORDRSP flows: IBM MQ sender from I2017, queue `IXXXX_TibnorS4`, one child per mill, ProcessDirect to `T0143_P_IDocReceiver_TibnorS4_PDToIDoc` | Same build script, `--flow INVOIC` |
| 2026-11-24 | Routing (L2, user's PO conditions) | No `ApplicationId` in this message. PO: `/Invoice/Header[starts-with(SourceSystem,'METOCS')]` → `…_TIBNOR_Tube` (Metocs), `not(...)` → `…_TIBNOR` (Tilkku); receiver `Header/RecipientIdentification` = one of the 4 GLNs | Receiver determination below |
| 2026-11-24 | Split of Tilkku (L2, user) | PO had one Tilkku mapping, we have two: split by `InterchangeSender` (Raahe 00372389445741, Hämeenlinna 00372389445751), the GLN the Tilkku mappings check | A Tilkku message with another GLN → no receiver → Error End |
| 2026-11-24 | Recipient check (L2, user) | Yes: only recipient GLNs 7340195700006, 7080003309006, 5790002585623, 003723894430 | Externalized `FinMessageHub_AllowedRecipients` (comma list) |
| 2026-11-24 | Namespaces | no Namespace Mapping: `<Invoice>` has no namespace | |

## Call-outs
- **Bhavesh, I extended `ReceiverDetermination.groovy` because** the receiver depends on three values (recipient list, SourceSystem prefix, mill GLN).
  - Standard alternative: a Router with the PO XPath conditions.
  - Why not: the SSAB parent pattern feeds the receiver loop from the `arr_receivers*` properties, as in the ORDERS and ORDRSP parents.

## Open points
- Same as the ORDRSP parent: template leftover `SAP_MessageProcessingLogCustomStatus`; FLAG §3.8.2 "Required for JMS".
- Deploy order: the 3 children, dispatcher `IXXXX_TibnorS4`, `T0143_P_IDocReceiver_TibnorS4_PDToIDoc`, then this parent.
