# IXXXX_PurchaseOrder_ORDERS_ORDERS02_TibnorS4_FinMessageHub_HameenlinnaMetocs_JMSToMQ

Child (package Tibnor_SSAB_EDIMigration) in the SSAB Simplified Pipeline:
- The parent `IXXXX_P_PurchaseOrder_ORDERS_ORDERS02_TibnorS4_IDocToJMS` puts the ORDERS02 IDoc on `I0707_FinMessageHub`.
- The I0707 dispatcher calls this flow over ProcessDirect `/<iFlow name>`.
- This flow maps the IDoc with `Map_TibnorS4_HammelinnaMetocsHub_PurchaseOrder_ORDERS02` and puts the OrdersMessage on IBM MQ for the Hämeenlinna Metocs hub.

Sources:
- Flow shape: our build of `I2018_Material_MSAP_SmarTeam_JMSToHTTP` 1.1.5 (L3).
- IBM MQ receiver channel, parameters and propdef: copied unchanged from Bhavesh's export `I2034_Pickinglist_SCWM_WMTORD_SCWM_WMTOID01_MSAP_StreamServe_JMSToIBMMQ` 1.0.10 (L1, in `source/`).
- Mapping: `mappings/1_ORDERS_Tibnor-to-HameenlinnaMetocs/build/Map_…_ORDERS02.zip` (v1.1.1), packed into `src/main/resources/`.
- Build: `py -I tools/iflow_build_tibnor.py --only child`

## Flow (Main Process)
Set Monitoring Identifiers → Log Payload → LogCustomHeaders → mapping → Set AttachmentName (`OutputPayload`) → Log Payload → **Send To MQ** → End.
- Set Monitoring Identifiers:
  - headers `SAP_Sender`, `SAP_Receiver`, `SAP_MessageType`, `SAP_ApplicationID` (= DOCNUM)
  - properties `CH_IdocNumber`, `CH_PurchaseOrder`, and **`HubEnvironment`**, which the mapping reads for `MessageRoutingInbound/Outbound`
- The template's SmarTeam response steps are removed: MQ returns no business response.

## Parameters
| Parameter | Default | Note |
|---|---|---|
| `PD_Address` | `/<iFlow name>` | must equal the name the parent sends in `SSAB_Dispatcher_ReceiverIFlow` |
| `HubEnvironment` | `TST` | `PRD` on production |
| `SAP_Sender` | `TibnorS4` | |
| `SAP_Receiver` | `FinMessageHub_HameenlinnaMetocs` | |
| `SAP_MessageType` | `ORDERS.ORDERS02` | |
| 16 other `IBMMQ_*` parameters | I2034 values, e.g. host `srt00990.ssab.com`, port 1414, channel `SAPISCLIENT.CH`, QM `QM1001T`, SSL `*TLS12`, proxy onPremise, Location ID empty, authentication none, transactional session true | as in I2034 |
| `IBMMQ_QueueName` | *empty* | **set on the tenant** |
| `IBMMQ_MessageType`, `IBMMQ_MessagePersistence`, `IBMMQ_TargetClient` | `textMessage`, `persistent`, `1` | fixed in I2034, externalized here |
| `AllowedHeaders` | `SSAB.*\|SAP.*` | child rule |

## Decisions
| Date | Question | Answer | Impact |
|---|---|---|---|
| 2026-11-23 | IBM MQ reference (L2, user) | I2034 instead of I2030 (I2030 is not in the repo) | Channel copied unchanged; source zip in `source/` |
| 2026-11-23 | MQ target (L2, user) | Same host, QM, channel and SSL as I2034. Queue to be decided | `IBMMQ_QueueName` empty |
| 2026-11-23 | HubEnvironment (L2, user; mapping Q3) | Externalized, default `TST` | Property in Set Monitoring Identifiers |
| 2026-11-23 | SAP_Sender / SAP_Receiver (L2, user) | `TibnorS4` / `FinMessageHub_HameenlinnaMetocs` | Header defaults |
| 2026-11-23 | Participant names (CLAUDE.md: plain system name) | PD sender `TibnorS4`, MQ receiver `FinMessageHub` | **FLAG**: neither is in the known list yet. Confirm |
| 2026-11-23 | Fixed MQ settings (CLAUDE.md: externalize all) | `messageType`, `messagePersistence`, `targetClient` externalized. `entity` (queue) and `connectionProtocol` (tcpip) stay fixed because they define the channel | Confirm |

## Open points
- The IBM MQ adapter is the third-party Rojo adapter (`rojoconsultancy.com`, 1.4.1). It must be deployed on the tenant; it is, because I2034 uses it.
- There is no exception subprocess, as in the template. An error fails the ProcessDirect call, and the dispatcher's JMS retry and DLQ handle it. Add an exception subprocess with an Error End?
- Deploy order: the child before the parent.
