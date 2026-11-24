# IXXXX_P_OrderResponse_FinMessageHub_MQToJMS

Parent (package Tibnor_SSAB_EDIMigration): order responses (ORDRSP, hub XML) from the Finnish message hub on **IBM MQ** → receiver determination on `Header/ApplicationId` → JMS queue `IXXXX_TibnorS4` → one child per mill, which posts an ORDERS01 IDoc to Tibnor S4.

- Templates:
  - our ORDERS parent `IXXXX_P_PurchaseOrder_…_IDocToJMS` (L3): Manual Retrigger, Main Process, Receivers Exist? → Error End, receiver loop, Send To JMS
  - IBM MQ sender channel: Bhavesh's `I2017_PurchaseOrder_SalesOrderBulkRequest_TILKKU_MSAP_IBMMQtoSOAP.jar` (L1, `source/`)
- Build: `py -I tools/iflow_build_tibnor_ordrsp.py --only parent`

## Flow
1. IBM MQ sender (`FinMessageHub`, Rojo IBMMQ adapter 1.4.1) or HTTPS retrigger → Main Process.
2. Set Monitoring Identifiers:
   - headers `SAP_Sender` = `FinMessageHub`, `SAP_MessageType` = `ORDRSP`, `SAP_ApplicationID` = DocumentId/DocumentNo
   - properties `CH_FinMessageHubApplicationId` (Header/ApplicationId) and `CH_PurchaseOrder` (Reference[@Type='CO']/RefNo), logged by LogCustomHeaders
3. `ReceiverDetermination.groovy` reads the property; it does not parse the payload (CLAUDE.md rule). METOCS* / TILKKUHA / TILKKURA → queue `IXXXX_TibnorS4` + child name. Anything else → Error End.

## Parameters (IBM MQ sender)
| Parameter | Default | Note |
|---|---|---|
| `IBMMQ_QueueName`, `IBMMQ_DLQueueName` | *empty* | **set on the tenant** |
| `IBMMQ_Hostname`, `_Port`, `_ChannelName`, `_Queue_ManagerName`, `_SSL_Cipher_Suite`, `_ProxyType`, `_Authentication` | I2017 values (`srt04684.ssab.com`, 1414, `SAPISCLIENT.CH`, `QM1010T`, `*TLS12`, onPremise, none) | |
| `IBMMQ_CCSID`, `IBMMQ_PollingInterval`, `IBMMQ_LocationID` | 1208, 300000, empty | renamed from I2017's `IBMMQ_CharacterSetID(CCSID)forNonASCIINames`, `IBMMQ_ConnectionCheckInterval(in ms)` ("Polling Interval" in the propdef), `LocationID` |
| `IBMMQ_MaxDeliveryCount`, `IBMMQ_Transactional_JMS_Session` | 4, true | |
| `IBMMQ_InitialDelay`, `IBMMQ_TransactionFailedHandling`, `IBMMQ_TargetClient` | 5000, moveMessageToAnotherQueue, 1 | fixed in I2017, externalized here |

## Decisions
| Date | Question | Answer | Impact |
|---|---|---|---|
| 2026-11-24 | Names (L2, user) | Parent `IXXXX_P_OrderResponse_FinMessageHub_MQToJMS`; children `IXXXX_OrderResponse_FinMessageHub_<Mill>_TibnorS4_JMSToIDoc` (the mill is only known after the receiver determination). Number to be decided | `NUMBER` in `tools/iflow_build_tibnor.py` |
| 2026-11-24 | Dispatcher queue (L2, user) | `IXXXX_TibnorS4`, a new Tibnor S4 dispatcher (not built here) | Number from the Central Integration team (I07xx/I08xx) |
| 2026-11-24 | Mills (L2, user) | Three children: METOCS* → Hämeenlinna Metocs, TILKKUHA → Hämeenlinna Tilkku, TILKKURA → Raahe Tilkku. The two Tilkku mappings differ only in the mill GLN check and SNDPRN | One child per mill; merging them later is a small change |
| 2026-11-24 | ApplicationId with namespaces (L2, user) | iFlow Namespace Mapping `xmlns:p1=http://www.ruukki.com/schemas/eai/internal/production/eruukki`, XPath `/p1:OrdrspInterchange/p1:OrderResponseMessage/p1:Header/p1:ApplicationId` | **UNVERIFIED**: no reference iFlow has the Namespace Mapping filled. Check it first in CPI |
| 2026-11-24 | Custom header name (L2, user) | `CH_FinMessageHubApplicationId`, not `CH_ApplicationId` (confusable with SAP_ApplicationID) | Logged by LogCustomHeaders |
| 2026-11-24 | MQ sender reference (L2, user) | I2017, only for the IBMMQ sender properties | Channel copied; parameter names cleaned up (table above) |
| 2026-11-24 | Parse the payload in the script? (L2, user) | No: XPath in Set Monitoring Identifiers, the script reads the property | CLAUDE.md rule |

## Open points
- Same template leftover as the ORDERS parent: `SAP_MessageProcessingLogCustomStatus` in "Send to Receiver" is a constant holding an expression.
- FLAG §3.8.2: JMS writes in the receiver loop without "Required for JMS" (as the other parents).
- Deploy order: the 3 children, dispatcher `IXXXX_TibnorS4`, `T0143_P_IDocReceiver_TibnorS4_PDToIDoc`, then this parent.
