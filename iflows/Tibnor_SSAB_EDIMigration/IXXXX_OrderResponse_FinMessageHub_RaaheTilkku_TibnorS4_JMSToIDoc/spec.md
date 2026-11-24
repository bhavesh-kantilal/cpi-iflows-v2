# IXXXX_OrderResponse_FinMessageHub_RaaheTilkku_TibnorS4_JMSToIDoc

Child (package Tibnor_SSAB_EDIMigration) for ApplicationId `TILKKURA`. The parent `IXXXX_P_OrderResponse_FinMessageHub_MQToJMS` puts the order response on `IXXXX_TibnorS4`; the dispatcher calls this flow over ProcessDirect `/<iFlow name>`. The flow maps the hub ORDRSP with `Map_RaaheTilkkuHub_TibnorS4_OrderConfirmation_ORDRSP` (v1.0.2) to ORDERS01 and sends it over ProcessDirect to the shared IDoc flow `T0143_P_IDocReceiver_TibnorS4_PDToIDoc`.

- Templates:
  - flow shape: our ORDERS child `IXXXX_PurchaseOrder_…_JMSToMQ` (L3)
  - ProcessDirect receiver ("IDoc to SAP"): reference `I2052_…_PDToIDoc` (L1, `source/`)
- Build: `py -I tools/iflow_build_tibnor_ordrsp.py --only RaaheTilkku`

## Flow (Main Process)
Set Monitoring Identifiers → Log Payload → LogCustomHeaders → mapping → Set AttachmentName → Log Payload → **Send To TibnorS4** (ProcessDirect) → End.
- Headers `SAP_Sender` = `FinMessageHub`, `SAP_Receiver` = `TibnorS4`, `SAP_MessageType` = `ORDRSP`, `SAP_ApplicationID` = DocumentNo.
- Properties `CH_FinMessageHubApplicationId`, `CH_PurchaseOrder`, and **`SNDPOR` / `RCVPOR` / `RCVPRN`**, which the mapping reads with getProperty for EDI_DC40.

## Parameters
| Parameter | Default | Note |
|---|---|---|
| `PD_Address` | `/<iFlow name>` | must equal the name the parent sends |
| `TibnorS4_IDocEndpoint` | `/T0143_P_IDocReceiver_TibnorS4_PDToIDoc` | shared IDoc flow |
| `TibnorS4_SNDPOR`, `TibnorS4_RCVPOR`, `TibnorS4_RCVPRN` | *empty* | **set on the tenant** |

## Decisions
| Date | Question | Answer | Impact |
|---|---|---|---|
| 2026-11-24 | Names (L2, user) | Parent `IXXXX_P_OrderResponse_FinMessageHub_MQToJMS`; children `IXXXX_OrderResponse_FinMessageHub_<Mill>_TibnorS4_JMSToIDoc` (the mill is only known after the receiver determination). Number to be decided | `NUMBER` in `tools/iflow_build_tibnor.py` |
| 2026-11-24 | Dispatcher queue (L2, user) | `IXXXX_TibnorS4`, a new Tibnor S4 dispatcher (not built here) | Number from the Central Integration team (I07xx/I08xx) |
| 2026-11-24 | Mills (L2, user) | Three children: METOCS* → Hämeenlinna Metocs, TILKKUHA → Hämeenlinna Tilkku, TILKKURA → Raahe Tilkku. The two Tilkku mappings differ only in the mill GLN check and SNDPRN | One child per mill; merging them later is a small change |
| 2026-11-24 | ApplicationId with namespaces (L2, user) | iFlow Namespace Mapping `xmlns:p1=http://www.ruukki.com/schemas/eai/internal/production/eruukki`, XPath `/p1:OrdrspInterchange/p1:OrderResponseMessage/p1:Header/p1:ApplicationId` | **UNVERIFIED**: no reference iFlow has the Namespace Mapping filled. Check it first in CPI |
| 2026-11-24 | Custom header name (L2, user) | `CH_FinMessageHubApplicationId`, not `CH_ApplicationId` (confusable with SAP_ApplicationID) | Logged by LogCustomHeaders |
| 2026-11-24 | IDoc to Tibnor S4 (L2, user) | ProcessDirect to `T0143_P_IDocReceiver_TibnorS4_PDToIDoc` | Channel as I2052 "Send IDoc to MSAP" |
| 2026-11-24 | IDoc control values (L2, user) | Externalized, empty defaults | Set on the tenant |

## Open points
- Guide §4.4.1 (`SapMessageId` = `SAP_MessageProcessingLogID` for IDoc receivers): expected in the shared T0143 flow. Check there.
- No exception subprocess (as the template); the dispatcher's JMS retry / DLQ handles errors.
