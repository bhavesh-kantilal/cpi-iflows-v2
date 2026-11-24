# IXXXX_DespatchAdvice_FinMessageHub_HameenlinnaTilkku_TibnorS4_JMSToIDoc

Child (package Tibnor_SSAB_EDIMigration) for not METOCS, InterchangeSender 00372389445751. The parent `IXXXX_P_DespatchAdvice_FinMessageHub_MQToJMS` puts the message on `IXXXX_TibnorS4`; the dispatcher calls this flow over ProcessDirect `/<iFlow name>`. The flow maps it with `Map_HammelinnaTilkkuHub_TibnorS4_DeliveryNotice_DESADV` (v1.0.2) to DESADV.DELVRY01 and sends it over ProcessDirect to the shared IDoc flow `T0143_P_IDocReceiver_TibnorS4_PDToIDoc`.

- Same shape as the ORDRSP children (templates: our ORDERS child, ProcessDirect receiver of I2052).
- Build: `py -I tools/iflow_build_tibnor_inbound.py --flow DESADV --only HameenlinnaTilkku`

## Flow (Main Process)
Set Monitoring Identifiers → Log Payload → LogCustomHeaders → mapping → Set AttachmentName → Log Payload → **Send To TibnorS4** (ProcessDirect) → End.
- Headers `SAP_Sender` = `FinMessageHub`, `SAP_Receiver` = `TibnorS4`, `SAP_MessageType` = `DESADV`, `SAP_ApplicationID` = DeliveryBatchId.
- Properties `CH_FinMessageHubSourceSystem`, `CH_PurchaseOrder`, and `SNDPOR` / `RCVPOR` / `RCVPRN` for EDI_DC40 (read by the mapping with getProperty where it uses them).

## Parameters
| Parameter | Default | Note |
|---|---|---|
| `PD_Address` | `/<iFlow name>` | must equal the name the parent sends |
| `TibnorS4_IDocEndpoint` | `/T0143_P_IDocReceiver_TibnorS4_PDToIDoc` | shared IDoc flow |
| `TibnorS4_SNDPOR`, `TibnorS4_RCVPOR`, `TibnorS4_RCVPRN` | *empty* | **set on the tenant** |

## Decisions
| Date | Question | Answer | Impact |
|---|---|---|---|
| 2026-11-24 | Names (L2, user) | Parent `IXXXX_P_DespatchAdvice_FinMessageHub_MQToJMS`, children `IXXXX_DespatchAdvice_FinMessageHub_<Mill>_TibnorS4_JMSToIDoc` ("DespatchAdvice / Invoice"). Number to be decided | `NUMBER` in `tools/iflow_build_tibnor.py` |
| 2026-11-24 | Shape (L2, user: "similar iflows") | Same as the ORDRSP flows: IBM MQ sender from I2017, queue `IXXXX_TibnorS4`, one child per mill, ProcessDirect to `T0143_P_IDocReceiver_TibnorS4_PDToIDoc` | Same build script, `--flow DESADV` |
| 2026-11-24 | Routing (L2, user's PO conditions) | No `ApplicationId` in this message. PO: `/p1:DeliveryBatch[starts-with(p1:SourceSystem,'METOCS')]` → 96A (Metocs), `not(...)` → 93A (Tilkku); receiver `Header/InterchangeRecipient` = one of the 4 GLNs | Receiver determination below |
| 2026-11-24 | Split of Tilkku (L2, user) | PO had one Tilkku mapping, we have two: split by `InterchangeSender` (Raahe 00372389445741, Hämeenlinna 00372389445751), the GLN the Tilkku mappings check | A Tilkku message with another GLN → no receiver → Error End |
| 2026-11-24 | Recipient check (L2, user) | Yes: only recipient GLNs 7340195700006, 7080003309006, 5790002585623, 003723894430 | Externalized `FinMessageHub_AllowedRecipients` (comma list) |
| 2026-11-24 | Namespaces | iFlow Namespace Mapping `xmlns:p1=http://www.ruukki.com/schemas/eai/rucomef/otc` (**verified** (L2, user 2026-11-24: the Namespace Mapping works in CPI)) | |
| 2026-11-24 | IDoc to Tibnor S4 (L2, user, ORDRSP round) | ProcessDirect to `T0143_P_IDocReceiver_TibnorS4_PDToIDoc`, control values externalized and empty | As the ORDRSP children |

## Open points
- No exception subprocess (as the template); the dispatcher's JMS retry / DLQ handles errors.
