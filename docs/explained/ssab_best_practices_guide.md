# SSAB Integration Suite Best Practises — summary (guide v1.9, 18.11.2026)

> **Customer-specific: SSAB / Tibnor** (one CPI tenant). Used through the skill `.claude/skills/ssab-tibnor/SKILL.md`. For another customer, ask before reusing anything here (CLAUDE.md "Which customer?").

Source: `SSAB_IntegrationSuite_Best Practises.pdf` on SharePoint (SSE IT - SAP Integration Suite › 20. Development). Author: Bhavesh Kantilal. Reviewer: Andreas Holmberg. Updates by Hans Nehrman. Evidence level L2.
Read on 2026-11-23. The build rules taken from it are in `CLAUDE.md` ("SSAB Best Practises"), and the naming facts are in `_reference/IFLOW_CONVENTIONS.md` (§1.5, §2.3). This page also holds the parts that are **not** build rules (security, operations, transport), so they are known when a question comes up.

## Where we deliberately differ (user, 2026-11-23; the guide will be updated)
| Guide | What we do |
|---|---|
| §3.5: don't externalize the HTTP sender or ProcessDirect sender address | Externalized as `HTTPS_Address` / `PD_Address` |
| §3.10.5.5: a dispatcher child's sender part is `JMS` | SmarTeam children `…_JMSToHTTP`; FSAP Medius children stay `…_PDToREST` |
| §3.10.1.1: JMS Retention Threshold 1 | FSAP parents keep 2 |
| §3.3.2: retrigger role `SSAB_Internal_Operations` | `SSAB_MessagingSend_InternalOperations` |
| §3.6: `SAP_Receiver` mandatory | Not set when receivers are determined dynamically |

## 1 Monitoring and payload logging
- Standard headers (`SAP_Sender`, `SAP_Receiver`, `SAP_MessageType`, `SAP_ApplicationID`) come from the allowed lists in the Naming Convention Guide. They are set in the first step, a Content Modifier "Set Monitoring Identifiers".
- **Custom headers:** `CH_` properties of type String, logged by `UTIL_LogCustomHeaders`. In the monitor, search them with "Use More Fields".
- **Payload as attachment:** `UTIL_LogPayloadAsAttachment`. It logs only when the tenant flag `SSAB_LogPayloadAsAttachment` (Partner Directory, default true) **and** the iFlow property `LogPayload` are true. The size limit is `LogPayloadSize`, else the tenant's `SSAB_LogPayloadAsAttachment_Size` (1024 KB).
- **Longer retention:** MPL archiving beyond 30 days goes to BTP DMS (proven in a PoC, not licensed yet). External logging to Splunk was evaluated and is not used.

## 2 Security
- Each sending system gets a custom role `SSAB_MessagingSend_<System>` and its own service instance + key (OAuth client credentials) in the space `Integration_External`.
- Internal keys sit in `Integration_Internal`, transport keys in `CloudTransportManagement`. Only subaccount admins are space developers. SAP IAS as the identity provider is possible (PoC done).

## 3 Development (build rules → CLAUDE.md)
- Main Process, max 15 steps per local process, two entry points (source + Manual Retrigger), left-to-right layout.
- Externalize all channel parameters and every Content Modifier value.
- No `*` headers; clean up payload properties.
- Transaction handling, session handling, JMS settings, max retries and DLQ, Error End for retries.
- **SSAB Simplified Pipeline:** one queue per receiver plus a dispatcher. Background: 850 queues provisioned, at the physical limit. Details: `jms_dispatcher_architecture.md`.
  - In Manage Message Queues, add the columns Sender, Receiver, Application Message Type, Application Message ID and Custom Status. Then filter the queue or DLQ per interface (custom status = `IXXXX`) and move messages back.
- **Datastore retry** (§3.11) is the exception. Use it only when single messages must be reprocessed from a dead-letter store (`SAP_DataStoreRetries`, a utility flow with `SourceDS`/`TargetDS`/`MessageCount` or `EntryId`). Datastores count against the tenant's 30 GB; JMS does not. SSAB default: JMS.
- **Messages in a JMS DLQ:** move them with the UI for small numbers, or a utility flow for hundreds, which must be undeployed afterwards. A single message cannot be taken out.
- **Mapping:** graphical first.

## 4 Flow structuring
- **Goals:** guaranteed delivery, exactly once, and one receiver's outage never blocks the others. That is why JMS sits between parent and child, not ProcessDirect.
- **ERP IDoc and ABAP-proxy senders:** use one SM59 destination to a generic dispatcher: `I0002_P_IDocDispatcher_SAPHR_IDocToPD` and `I0009_P_XIDispatcher_Asynch_StripSAP_XIToPD`, with value mappings `VM_…_To_IFlow`. The dispatcher forwards over ProcessDirect to the parent. Templates are in the package `Templates`.
- **ODEX EDI via SFTP:** use the template `ODEX_Sender_Asynch_EDI_ParentFlow`. It converts EDI to XML, sets the PO root tag, and routes on the sender ID via value mapping `ODEX_Sender_Asynch_EDI_VM`.
- **Shared SAP receiver flows and MDM lookup:** see IFLOW_CONVENTIONS §1.5.
- **Plain SFTP file transfers:** no JMS. A failed run leaves the file on the sender and alerts.

## 5 Versioning
- **Version numbers:** major per project, minor per CR / SR / production fix, micro per change during development.
- **Version comment:** always set, with the project or SR ID (convention in the Naming Convention Guide).

## 6 Transport
- Cloud TMS: export only from DEV. Everything imported to TEST is also imported to PROD, in the same order.
- Developers configure and deploy in each tenant.
- Transport iFlows individually. A whole package only for its first transport.
- Value mappings: only the first version is transported.
- Rollback via TMS within 30 days, otherwise an admin reverts the version manually.

## 7 Operations
- **Queue alerts:** `I0006_P_UTIL_MonitorJMSQueues` runs every 15 min. Thresholds: queue 5, DLQ 0 (a value mapping overrides them). Mail receivers come from the Partner Directory `SSAB_AlertMailReceivers`.
- **Failed, escalated and retry alerts:** `I0027_P_UTIL_MonitorFailedIFlows`. A value mapping ignores known errors or iFlows.
- **Receiver outage:** mass undeploy/deploy with `I0024_P_UTIL_MassUndeploy` and `I0025_P_UTIL_MassDeploy` (`?SytemName=<System>`, value mapping `VM_CloudIntegration_MassDeployUndeploy`).
- **Cloud ALM:** only certificate-expiry alerts are active (warning < 30 days, critical < 7). Queue and exception monitoring there is not used, because the custom flows above do it better.

## Errors in the guide (for the next update)
- **§1.1.1.2:** `SAP_Receiver` is described as the sender system.
- **§3.10.5.6:**
  - The text says Base64 JSON, but `CopyPropertiesToHeader` writes Java `Properties` text.
  - The snippet labelled "(Parent IFlow)" is the child script.
  - The JSON variant can't read what the parent writes.
  - Script names are mixed (`HeaderToProperties` / `CopyHeaderToProperties`).
- **§3.12** says 500 queues, but §3.10.5 says 850.
- **§3.10.5.8:** TODO link to the queue list.
- **§4.2.2.2** "receives the IDoc" (proxy section). Child entry points in §4.1.2.2 and §4.2.2.2 still show their own JMS queue (pre-pipeline).
- Plus the differences in the table at the top.
