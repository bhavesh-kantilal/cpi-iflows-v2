# IXXXX_P_PurchaseOrder_ORDERS_ORDERS02_TibnorS4_IDocToJMS

Parent (package Tibnor_SSAB_EDIMigration). It receives the ORDERS02 IDoc from Tibnor S4 over **ProcessDirect**: "IDoc" in the name is the message, not the adapter. It finds the receiver from `EDI_DC40/RCVPRN` and writes to the JMS queue of the I0707 dispatcher.

- `IXXXX`: the interface number is not decided yet. It is one constant, `NUMBER` in `tools/iflow_build_tibnor.py`. Changing it renames both iFlows, the PD addresses and the receiver iFlow name in `ReceiverDetermination.groovy`.
- Template: our build of `I2023_P_Equipment_…_MSAP_IDocToJMS` 1.0.14 (L3). It has the same IDoc-parent shape: PD sender, Manual Retrigger, Main Process, receiver loop, Send To JMS.
- Build: `py -I tools/iflow_build_tibnor.py --only parent`

## Flow
1. Entry: ProcessDirect `/<iFlow name>` (sender `TibnorS4`), or the HTTPS retrigger (`Retrigger`, role `SSAB_MessagingSend_InternalOperations`). Both call Main Process.
2. Set Monitoring Identifiers:
   - headers `SAP_Sender`, `SAP_MessageType`, `SAP_ApplicationID` (= DOCNUM)
   - properties `CH_IdocNumber`, `CH_PurchaseOrder` (`/ORDERS02/IDOC/E1EDK01/BELNR`), `Environment`, `IFlowName`, and the LogPayload settings
3. Log Payload, then LogCustomHeaders.
4. Receiver Determination (`ReceiverDetermination.groovy`): if RCVPRN without leading zeros is `25200`, the receiver is queue `I0707_FinMessageHub` with receiver iFlow `IXXXX_PurchaseOrder_ORDERS_ORDERS02_TibnorS4_FinMessageHub_HameenlinnaMetocs_JMSToMQ`.
5. Receivers Exist?
   - No → **Error End**.
   - Yes → Send To Receivers loop: header `SSAB_Dispatcher_ReceiverIFlow`, then Send To JMS (`${property.QueueName}`).

## Parameters
| Parameter | Default | Note |
|---|---|---|
| `ProcessDirect_Address` | `/IXXXX_P_…_IDocToJMS` | the Tibnor S4 entry flow must call this address |
| `HTTPS_Address` | `/IXXXX_P_…_IDocToJMS` | retrigger |
| `SAP_Sender` | `TibnorS4` | |
| `SAP_MessageType` | `ORDERS.ORDERS02` | |
| `Environment` | `DEV` | was `Enviroinment` in the template |
| `JMS_*` | as I2023_P | the queue comes from the receiver determination |

## Decisions
| Date | Question | Answer | Impact |
|---|---|---|---|
| 2026-11-23 | Names (L2, user) | Parent `IXXXX_P_PurchaseOrder_ORDERS_ORDERS02_TibnorS4_IDocToJMS`, child `IXXXX_…_FinMessageHub_HameenlinnaMetocs_JMSToMQ`. Number to be decided | `NUMBER` constant in the build script |
| 2026-11-23 | Sender adapter (L2, user) | ProcessDirect, even though the name says IDoc | The I2023_P template already has a PD sender |
| 2026-11-23 | Receiver rule (L2, user) | RCVPRN = 25200 → child; leading zeros ignored | `ReceiverDetermination.groovy` (see call-out) |
| 2026-11-23 | Queue (L2, user) | `I0707_FinMessageHub` (DLQ `_D`). The dispatcher already exists on the tenant | Not built here |
| 2026-11-23 | No receiver found (L2, user) | Error | The existing "Receivers Exist?" router goes to the Error End. No extra code |
| 2026-11-23 | Package (L2, user) | `Tibnor_SSAB_EDIMigration` (typed "TIbnor_…", read as a typo) | Repo folder `iflows/Tibnor_SSAB_EDIMigration/` |
| 2026-11-23 | SAP_Sender (L2, user) | `TibnorS4` (typed "TIbnorS4", read as a typo). No SAP_Receiver in the parent | Header defaults; PD sender participant `TibnorS4` |
| 2026-11-23 | Misspelt template names (CLAUDE.md rule) | Fixed | `Enviroinment` → `Environment` (parameter and property) |

## Call-outs
- **Bhavesh, I built `ReceiverDetermination.groovy` because** the receiver depends on RCVPRN with leading zeros ignored, and the SSAB parent pattern feeds the receiver loop from the `arr_receivers*` properties.
  - Standard alternative: a Router on `number(//RCVPRN) = 25200`.
  - Why not: the loop pattern with the script is the agreed SSAB standard (`docs/questions/iflow_architecture_questions.md`), and it keeps every receiver in one place.

## Open points
- **Template leftover, not changed:** in "Send to Receiver", the header `SAP_MessageProcessingLogCustomStatus` has type *constant* and value `${header.Dispatcher_ReceiverIFlow.split('_')[0]}`. A constant is not evaluated, and the header name lacks `SSAB_`. I2023_P has the same problem. Fix it in all parents?
- FLAG §3.8.2: the receiver loop writes to JMS, but transaction handling is not "Required for JMS". I2023_P and I2024_P are the same. Here only one receiver can match.
