# iFlow Architecture — Open Questions
Created: 2026-11-15
Based on: FSAP_Controlling_MasterData, UTIL_JMSDispatcher, MSAP_PlantMaintenance_MasterData, GlobalMediusInvoice
**Answered: 2026-11-15**

Questions follow the mapping Q&A format: each question names `iFlow › step › property (expression)`.

---

## A — FSAP Parent Flow Receiver Determination (I0539_P / I0541_P / I0545_P)

The existing FSAP controlling parents use a **custom loop** that is different from the new parent pattern seen in MSAP PlantMaintenance.

| Old pattern (I0539_P, I0541_P, I0545_P) | New pattern (MSAP PlantMaintenance) |
|---|---|
| `ReceiverDetermination.groovy` reads `IO_QUEUES` string, builds `QUEUE_LIST` + `QUEUE_INDEX` | `ReceiverDetermination.groovy` builds `arr_receiversQueueList` + `arr_receiversIFlowList` + `arr_receiversLastIndex` |
| `SetQueueNameHeader.groovy` / `RestorePayload.groovy` drive the loop | CPI Iterating Splitter with `${property.CamelLoopIndex}` |
| `RestorePayload.groovy` restores `ORIGINAL_BODY` for each receiver | Iterating Splitter handles per-iteration payload automatically |
| Sets header `QueueName` only | Sets header `QueueName` + header `SSAB_Dispatcher_ReceiverIFlow` + header `SAP_MessageProcessingLogCustomStatus` |
| **No** `SSAB_Dispatcher_ReceiverIFlow` | **Has** `SSAB_Dispatcher_ReceiverIFlow` = child iFlow name |

**Q-A1 › I0539_P / I0541_P / I0545_P › ReceiverDetermination.groovy (loop mechanism):**
When we enhance these parents, should we replace the QUEUE_LIST/QUEUE_INDEX custom loop with the new Iterating Splitter + `arr_receivers*` pattern, or keep the existing loop and just add the `SSAB_Dispatcher_ReceiverIFlow` header on top?

*Answer: Use the new pattern (arr_receiversQueueList + arr_receiversIFlowList + Iterating Splitter). The receiver determination + looping process is the standard pattern; the FSAP flows were messed up by other developers. Queue names are hardcoded in ReceiverDetermination.groovy. Only the Medius queue changes to the common dispatcher (I0702_Medius); all JMS REST receivers keep their existing dedicated queues.*

---

**Q-A2 › I0539_P / I0541_P / I0545_P › RestorePayload.groovy:**
If we migrate to the Iterating Splitter pattern, `RestorePayload.groovy` and `AddQueueIndex.groovy` become redundant and can be removed. Confirmed?

*Answer: Yes, remove both scripts when migrating to the new pattern.*

---

**Q-A3 › I0539_P › parameters.prop (P_IO_QUEUES vs IO_QUEUES):**
Should we standardise to `IO_QUEUES` (no prefix) in I0539_P when we update it?

*Answer: No need to externalise queue names at all. Queue names go directly in ReceiverDetermination.groovy (not in parameters.prop). Making them dynamic would require making other parameters dynamic too, which is not desirable. Only the Medius queue changes to I0702_Medius; others stay as-is in the script.*

---

**Q-A4 › I0541_P › ASAP gateway:**
Is the ASAP path still active, or was it decommissioned? What is the correct IO_QUEUES value for I0541_P today?

*Answer: ASAP was the old name for MSAP. ASAP is decommissioned — remove that gateway path entirely.*

---

**Q-A5 › I0545_P › parameters.prop (`I0545_MEDIUS,I0546_MOBILE=...`):**
What should the IO_QUEUES value be for I0545_P?

*Answer: No need to externalise. Each queue name goes in the Groovy script. Only the Medius queue changes to the common dispatcher; other queues stay as they are, hardcoded in the script.*

---

## B — "Cost Center 2 Numbers" Consolidation

**Q-B1 › All CostCenter flows (naming):**
Which interface number should own the Medius child after migration?

*Answer: Everything becomes I0539. The new Medius child will be `I0539_CostCenter_FSAP_Medius_PDToREST`. The existing `I0540_CostCenter_FSAP_Medius_JMSToREST` stays alive until its queue drains, then is retired. The queue name `I0540_MEDIUS` stays the same (old consumer still reads it during transition); the new child is ProcessDirect, not JMS.*

---

**Q-B2 › I0539_P › P_IO_QUEUES (Oracle queue — in scope?):**
Is the Oracle/SFTP child `I0539_CostCenter_FSAP_Oracle_JMSToSFTP` in scope for the dispatcher migration?

*Answer: Keep Oracle as-is. First migration is Medius only. Oracle queue I0539_ORACLE stays on its dedicated queue.*

---

## C — Medius Dispatcher Design

**Q-C1 › New Medius dispatcher (interface number and naming):**
What interface number and queue name should the Medius dispatcher use?

*Answer: I0702. Dispatcher iFlow: `I0702_P_JMSDispatcher_Medius`. Queue: `I0702_Medius`. DLQ: `I0702_Medius_D`.*

---

**Q-C2 › Medius dispatcher — scope: one per SAP stream, or one for all Medius?**

*Answer: One common Medius dispatcher (I0702_P_JMSDispatcher_Medius) for all FSAP→Medius interfaces. Note: in this context FSAP is the sender and Medius is the receiver — the queue/dispatcher is named after the receiver system (Medius), not the sender (FSAP).*

---

**Q-C3 › Medius dispatcher — `MaxRetries` and retry parameters:**
Should the Medius dispatcher use the same values as SmarTeam?

*Answer: Yes, same parameters as the SmarTeam dispatcher (MaxRetries=2, JMS_ConcurentProcesses=1, JMS_RetryInterval=1, JMS_ExponentialBackoff=1, JMS_ExpirationDays=30).*

---

## D — New PDToREST Child iFlow Design

**Q-D1 › Company filter (`AllowedCompanies` / `Allowed?` gateway):**
Should the company filter stay in the child iFlow or move to the parent?

*Answer: Company filter stays in the child iFlow. This allows adding new companies to a child without changing the parent. Add a custom header when a message is filtered out.*

---

**Q-D2 › I0541 (`I0541_InternalOrder_FSAP_Medius_JMSToREST`) › "Internal Order Splitter" step:**
Should the splitter stay in the new PDToREST child?

*Answer: Move the splitter to the parent flow. One IDOC message for Internal Order can contain multiple internal orders — split in the parent and process each individually in the child. The child processes one at a time.*

---

**Q-D3 › I0545 (`I0545_WBSElement_FSAP_Medius_JMSToREST`) › "Query WBS Element" OData call:**
Should the OData lookup stay inside the new PDToREST child or become a separate subprocess?

*Answer: OData lookup stays inside the PDToREST child. Keep all logic exactly the same — the only change is switching from JMS consumer to ProcessDirect entry.*

---

**Q-D4 › `ReplaceWithVirtualCompany.groovy`:**
Should this script be kept unchanged in the new children?

*Answer: Yes, absolutely. No logic changes. Copy unchanged from existing children.*

---

## E — Existing Children During Migration

**Q-E1 › Migration order:**
Should we build child + dispatcher first and deploy separately, or all in one go?

*Answer: Start with Medius only. Build the new PDToREST children and I0702 dispatcher first, then update the parents.*

---

**Q-E2 › Old dedicated queues (`I0540_MEDIUS`, `I0541_MEDIUS`, `I0545_MEDIUS`):**
Is there a standard drain-and-verify procedure?

*Answer: User handles queue deletion. No procedure needed from development side.*

---

## F — GlobalMediusInvoice (I0115 flows) — Scope

**Q-F1 › I0115 flows — dispatcher migration in scope?**

*Answer: No migration needed on these flows. Learn only. This is for future reference when building more complex flows — learn and remember for later after the FSAP controlling work is done.*

**Q-F2 › GlobalMediusInvoice — changes needed?**

*Answer: Confirmed — learn only, no development work.*

---

## G — Miscellaneous

**Q-G1 › I0539_P / I0541_P / I0545_P › sender adapter:**
Should the FSAP controlling parents keep the SOAP sender adapter?

*Answer: Yes, no logic changes to the sender side. One group is event-based (AMQP), the other is DRF-based (SOAP) — both are valid, keep them as-is.*

---

**Q-G2 › `SAP_MessageProcessingLogCustomStatus` in parent vs dispatcher:**
Should the FSAP controlling parents also set this header in the loop?

*Answer: Yes, set it in both parent and dispatcher so it is always visible in the MPL regardless of which process log you look at.*

---

**Q-G3 › New parent iFlow names:**
Does `I0539_P_CostCenter_FSAP_SOAPToJMS` need renaming?

*Answer: No rename needed. The name already follows the convention (`I<id>_P_<Object>_<Src>_<Transport>ToJMS`). Both old and new are SOAPToJMS — no change.*

---

## Decision Summary

| Decision | Value |
|---|---|
| New parent loop pattern | Iterating Splitter + `arr_receiversQueueList` + `arr_receiversIFlowList` |
| Queue names location | Hardcoded in `ReceiverDetermination.groovy` (not parameters.prop) |
| Medius dispatcher | `I0702_P_JMSDispatcher_Medius` / queue `I0702_Medius` / DLQ `I0702_Medius_D` |
| Dispatcher parameters | Same as I0701 (MaxRetries=2, ConcurrentProcesses=1, RetryInterval=1, ExponentialBackoff=1) |
| CostCenter interface number | Everything under **I0539** (retire I0540 for Medius after drain) |
| Oracle queue (I0539_ORACLE) | Keep as-is — Medius migration only for now |
| ASAP gateway (I0541_P) | Remove entirely — decommissioned |
| Company filter | Stays in child; custom header when filtered |
| Internal Order splitter | Move to **parent** (one IDoc may contain multiple orders) |
| WBS OData lookup | Stays in PDToREST child unchanged |
| ReplaceWithVirtualCompany | Copy unchanged into new children |
| SAP_MessageProcessingLogCustomStatus | Set in **both** parent (per iteration) and dispatcher |
| GlobalMediusInvoice | Learn only — no changes |

*End of Q&A — 2026-11-15*
