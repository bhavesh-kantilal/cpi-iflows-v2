# iFlow Architecture — Open Questions
Created: 2026-11-15
Based on: FSAP_Controlling_MasterData, UTIL_JMSDispatcher, MSAP_PlantMaintenance_MasterData, GlobalMediusInvoice

Questions follow the mapping Q&A format: each question names `iFlow › step › property (expression)`.
Please add your answer below each question. I will update the design plan and IFLOW_CONVENTIONS.md after you answer.

---

## A — FSAP Parent Flow Receiver Determination (I0539_P / I0541_P / I0545_P)

The existing FSAP controlling parents use a **custom loop** that is different from the new AMQP parent pattern seen in I2049_P / I2050_P.

| Old pattern (I0539_P, I0541_P, I0545_P) | New pattern (I2049_P, I2050_P) |
|---|---|
| `ReceiverDetermination.groovy` reads `IO_QUEUES` string, builds `QUEUE_LIST` + `QUEUE_INDEX` | `ReceiverDetermination.groovy` builds `arr_receiversQueueList` + `arr_receiversIFlowList` + `arr_receiversLastIndex` |
| `SetQueueNameHeader.groovy` / `RestorePayload.groovy` drive the loop | CPI Iterating Splitter with `${property.CamelLoopIndex}` |
| `RestorePayload.groovy` restores `ORIGINAL_BODY` for each receiver | Iterating Splitter handles per-iteration payload automatically |
| Sets header `QueueName` only | Sets header `QueueName` + header `SSAB_Dispatcher_ReceiverIFlow` + header `SAP_MessageProcessingLogCustomStatus` |
| **No** `SSAB_Dispatcher_ReceiverIFlow` | **Has** `SSAB_Dispatcher_ReceiverIFlow` = child iFlow name |

**Q-A1 › I0539_P / I0541_P / I0545_P › ReceiverDetermination.groovy (loop mechanism):**
When we enhance these parents, should we replace the QUEUE_LIST/QUEUE_INDEX custom loop with the new Iterating Splitter + `arr_receivers*` pattern (matching I2049_P), or keep the existing loop and just add the `SSAB_Dispatcher_ReceiverIFlow` header on top?

*Answer:*

---

**Q-A2 › I0539_P / I0541_P / I0545_P › RestorePayload.groovy:**
If we migrate to the Iterating Splitter pattern, `RestorePayload.groovy` and `AddQueueIndex.groovy` become redundant and can be removed. Confirmed?

*Answer:*

---

**Q-A3 › I0539_P › parameters.prop (P_IO_QUEUES vs IO_QUEUES):**
I0539_P uses `{{P_IO_QUEUES}}` (value: `I0540_MEDIUS,I0539_ORACLE`) as its parameter name, while I0541_P uses `{{IO_QUEUES}}` (currently empty). The ReceiverDetermination.groovy script reads property `IO_QUEUES`, so there must be a Content Modifier copying `P_IO_QUEUES` → `IO_QUEUES` before the script runs.
Should we standardise to `IO_QUEUES` (no prefix) in I0539_P when we update it?

*Answer:*

---

**Q-A4 › I0541_P › ASAP? gateway (condition: `${header.QueueName} = 'I0541_ASAP'`):**
I0541_P has a gateway that routes separately when the current queue is `I0541_ASAP`. The parameters.prop shows `IO_QUEUES=` (empty) and a suspicious entry `I0541_MEDIUS,I0542_MOBILE=I0541_MEDIUS,I0542_MOBILE` that looks like a copy-paste error (the whole queue-list string was used as the parameter key).
Is the ASAP path still active, or was it decommissioned? What is the correct IO_QUEUES value for I0541_P today?

*Answer:*

---

**Q-A5 › I0545_P › parameters.prop (`I0545_MEDIUS,I0546_MOBILE=I0545_MEDIUS,I0546_MOBILE`):**
Same pattern as I0541_P — the queue-list appears as the key with itself as the value, and `IO_QUEUES` is not present. What should the IO_QUEUES value be for I0545_P?

*Answer:*

---

## B — "Cost Center 2 Numbers" Consolidation

The CostCenter FSAP interface currently spans two ID numbers:
- **I0539** — parent (`I0539_P_CostCenter_FSAP_SOAPToJMS`) + Oracle child (`I0539_CostCenter_FSAP_Oracle_JMSToSFTP`)
- **I0540** — Medius child (`I0540_CostCenter_FSAP_Medius_JMSToREST`)

`I0539_P` sends to both `I0540_MEDIUS` and `I0539_ORACLE` queues.

**Q-B1 › All CostCenter flows (naming):**
When we migrate to the dispatcher pattern, which interface number should own the Medius child?
- Option A: Use **I0539** for everything CostCenter (new child: `I0539_CostCenter_FSAP_Medius_PDToREST`; retire I0540 for Medius). I0539 becomes: parent + Oracle child + Medius child.
- Option B: Keep **I0540** for the Medius child (new child: `I0540_CostCenter_FSAP_Medius_PDToREST`). The parent stays I0539.
- Option C: Renumber — assign a new number to unify parent and all children.

*Answer:*

---

**Q-B2 › I0539_P › P_IO_QUEUES (Oracle queue — in scope?):**
The Oracle/SFTP child `I0539_CostCenter_FSAP_Oracle_JMSToSFTP` reads from `I0539_ORACLE` queue. Is this interface in scope for the dispatcher migration, or does it stay on its own dedicated queue?

*Answer:*

---

## C — Medius Dispatcher Design

The SmarTeam dispatcher uses queue `I0700_SmarTeam`. We need an equivalent for Medius.

**Q-C1 › New Medius dispatcher (interface number and naming):**
What interface number and queue name should the Medius dispatcher use?
Suggested pattern (following I0700): `I0xxx_P_JMSDispatcher_Medius` / queue `I0xxx_Medius`.
Which number? Note: I0540–I0545 are already Cost Center / Internal Order / WBSE Medius children, so it needs its own number.

*Answer:*

---

**Q-C2 › Medius dispatcher — scope: one per SAP stream, or one for all Medius?**
You mentioned: "for SAP Systems MSAP, FSAP, GSAP we will have multiple per SAP Stream (procurement, logistics, finance, controlling, cash & banking)."
For the Medius receiver specifically:
- One shared `I0xxx_P_JMSDispatcher_Medius` for all FSAP→Medius interfaces (controlling, finance, etc.), or
- Separate dispatchers per stream, e.g. `I0xxx_P_JMSDispatcher_FSAP_Controlling_Medius`?

*Answer:*

---

**Q-C3 › Medius dispatcher — `MaxRetries` and retry parameters:**
The SmarTeam dispatcher uses `MaxRetries=2`, `JMS_ConcurentProcesses=1`, `JMS_RetryInterval=1`, `JMS_ExponentialBackoff=1`.
Should the Medius dispatcher use the same values, or different ones?

*Answer:*

---

## D — New PDToREST Child iFlow Design

The new Medius child iFlows (replacing I0540, I0541, I0545 JMSToREST) will follow the SmarTeam PDToHTTP pattern (Pattern B from the scan: ProcessDirect → Medius REST).

**Q-D1 › I0540 / I0541 / I0545 › company filter (`AllowedCompanies` / `Allowed?` gateway):**
The existing children filter by company:
- I0540: `AlowedCompanies=` (empty = all allowed)
- I0541: `AllowedCompanies=SE78` (only SE78)
- I0545: not visible yet

Should this company filter stay in the **child** iFlow, or move to the **parent** `ReceiverDetermination.groovy` (so the child only receives relevant messages)?
Moving it to the parent is cleaner (no dead messages on the queue), but changes the parent logic.

*Answer:*

---

**Q-D2 › I0541 (`I0541_InternalOrder_FSAP_Medius_JMSToREST`) › "Internal Order Splitter" step:**
The existing I0541 has an "Internal Order Splitter" step, which the other children don't have. Should this splitter step be kept in the new PDToREST child?

*Answer:*

---

**Q-D3 › I0545 (`I0545_WBSElement_FSAP_Medius_JMSToREST`) › "Query WBS Element" OData call:**
I0545 does an OData lookup to fetch the person responsible for a WBS element. The source system does not provide it directly. Should this OData lookup stay inside the new PDToREST child iFlow, or should it become a separate subprocess / UTIL iFlow called via ProcessDirect?

*Answer:*

---

**Q-D4 › I0540 / I0541 / I0545 › `ReplaceWithVirtualCompany.groovy`:**
All three current children use `ReplaceWithVirtualCompany.groovy`. This should be kept in the new children as-is. Confirmed?

*Answer:*

---

## E — Existing Children During Migration

**Q-E1 › Migration order:**
The PPTX says: deploy child first, then update parent, let old queue drain, then retire old consumer.
For the first interface (probably CostCenter), should we:
a) Build the new PDToREST child and dispatcher, then update I0539_P — all in one go?
b) Build and deploy the new child first, let the user verify it works (via HTTPS retrigger), then update the parent?

*Answer:*

---

**Q-E2 › Old dedicated queues (`I0540_MEDIUS`, `I0541_MEDIUS`, `I0545_MEDIUS`):**
Once migrated, these queues need to be drained and deleted to free capacity. Is there a standard drain-and-verify procedure you follow, or should I document one?

*Answer:*

---

## F — GlobalMediusInvoice (I0115 flows) — Scope

The I0115 invoice flows are highly complex (I0115_Invoice_Medius_GSAP_ProcessPostedInvoices_JMSToRFC at v1.229; multiple XSLT steps, 15+ custom Groovy scripts, multiple SAP RFC/SOAP/OData calls, 13+ subprocesses in the router). The timer parents (I0115_P_*) currently use old per-company-code JMS queues.

**Q-F1 › I0115 flows — dispatcher migration in scope?**
Are the I0115 invoice flows in scope for the dispatcher migration, or is that a separate project?

*Answer:*

---

**Q-F2 › GlobalMediusInvoice — changes needed?**
You said "Global_Medius_Invoice is for you to learn my most complex iFlows. No changes needed." Confirmed — learn only, no development work on these flows?

*Answer:*

---

## G — Miscellaneous

**Q-G1 › I0539_P / I0541_P / I0545_P › sender adapter (stays SOAP):**
The FSAP controlling parents receive via SOAP from FSAP (SAP S/4). The MSAP plant maintenance parents receive via AMQP (SAP Event Mesh). The FSAP parents should keep the SOAP sender adapter after the receiver-determination enhancement. Confirmed?

*Answer:*

---

**Q-G2 › `SAP_MessageProcessingLogCustomStatus` in parent vs dispatcher:**
In the new AMQP parent (I2049_P), the parent itself sets `SAP_MessageProcessingLogCustomStatus` to `${header.SSAB_Dispatcher_ReceiverIFlow.split('_')[0]}` as part of "Get Current Index Receiver". The dispatcher also sets it from the same expression. Should the FSAP controlling parents also set this header in the loop, or rely on the dispatcher only?

*Answer:*

---

**Q-G3 › New parent iFlow names:**
After enhancement, should the FSAP controlling parents be renamed to match the new naming convention?
Current: `I0539_P_CostCenter_FSAP_SOAPToJMS`
Convention from IFLOW_CONVENTIONS / PPTX: `I<id>_P_<Object>_<Src>_<Transport>ToJMS`
The name already follows the pattern. No rename needed? Or should `SOAPToJMS` become `SOAPToJMS` (unchanged)?

*Answer:*

---

*End of questions — 2026-11-15*
