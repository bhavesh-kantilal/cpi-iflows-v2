---
name: ssab-tibnor
description: SSAB and Tibnor iFlow conventions (one CPI tenant). Use whenever an iFlow is built, changed or reviewed for SSAB or Tibnor (packages FSAP Controlling, SmarTeam, Tibnor_SSAB_EDIMigration, Medius, StreamServe, MSAP, FSAP, GSAP), or when the user wants to reuse the SSAB conventions for another customer.
---

# SSAB / Tibnor: customer conventions for iFlows

SSAB and Tibnor run on **one CPI tenant**, so everything here applies to both (user, 2026-11-27).
How iFlows are *built* (diagram rules, checks, Groovy, XPath, externalizing, workflow) is generic and lives in `CLAUDE.md`. This skill holds the **customer answers** to the checklist in `CLAUDE.md` ("Customer checklist").

Each point is marked:
- **[Generic pattern, SSAB value]**: you use the same pattern at most customers; only the value is SSAB's. For a new customer, ask for that customer's value.
- **[SSAB only]**: specific to SSAB. Don't reuse it unasked.

Evidence levels as in `CLAUDE.md` (L1 export, L2 user statement or CPI download, L3 tested build, L4 unverified).

## 1. Monitoring identifiers
- **[Generic pattern, SSAB value]** Standard headers are set as **headers** in the first Content Modifier, `Set Monitoring Identifiers`:
  - `SAP_Sender` = `{{SAP_Sender}}`
  - `SAP_Receiver` = `{{SAP_Receiver}}`
  - `SAP_MessageType` = `{{SAP_MessageType}}`
  - `SAP_ApplicationID` = XPath to the business key

  The generic rule is in `CLAUDE.md`.
- **[SSAB only]** Allowed values come from the SSAB Naming Convention Guide. Ask, don't invent.
  - SmarTeam flows: `SAP_Sender` = `AD1_110` everywhere (user, 2026-11-23).
  - Tibnor ORDERS: `SAP_Sender` = `TibnorS4`.
- **[SSAB only]** The guide §3.6 makes `SAP_Receiver` mandatory. We don't set it with dynamic receiver determination (user, 2026-11-23).

## 2. How JMS is organized
- **[Generic pattern, SSAB value]** **SSAB Simplified Pipeline**: one queue per receiver plus a dispatcher. The reason: 850 queues provisioned, which is the tenant's physical limit.
  - Detail: `docs/explained/jms_dispatcher_architecture.md`.
- **[SSAB only]** Queue name = `<DispatcherNo>_<TgtSys>_<Area>`, e.g. `I0701_MSAP_PlantMaintenance`. The DLQ is `<Queue>_D`.
  - The core ERP queues (I0701–I0706 MSAP, I0716–I0720 FSAP) are listed in `_reference/IFLOW_CONVENTIONS.md` §2.3.
- **[Generic pattern, SSAB value]** The JMS sender is externalized: concurrency 1, retry interval 1 min, exponential backoff only for unstable targets, Dead-Letter Queue on. The JMS receiver's Retention Threshold and Expiration are externalized (guide §3.10.1).
- **[SSAB only]** `JMS_RetentionThresholdAlerting = 2` stays on the FSAP parents (the guide says 1).
- **[Generic pattern, SSAB value]** Max retries: the dispatcher's `MaxRetries` = 2. When `SAPJMSRetries > MaxRetries`, the message goes to the DLQ `<Queue>_D` and an Escalation End (§3.10.5.1, §3.10.5.4).
- **[Generic pattern, SSAB value]** A JMS-fed flow, including every dispatcher child, ends its exception subprocess with an **Error End**, so JMS retries (§3.13).
- **[Generic pattern, SSAB value]** Transaction handling:
  - "Not Required" by default.
  - More than one JMS write: "Required for JMS", timeout 1 min.
  - Several JDBC receivers: "Required for JDBC".
  - Never JMS and JDBC in one iFlow (§3.8).
- **[SSAB only]** Plain SFTP file transfers use no JMS queue (§4.6).

## 3. How iFlows are named
- **[SSAB only]** The name patterns are in `_reference/IFLOW_CONVENTIONS.md` §2.1:
  - parent: `I<nnnn>_P_<Object>_<Action>_<SrcSys>_<Sender>To<Receiver>`
  - dispatcher: `I<nnnn>_P_JMSDispatcher_<TgtSys>_<Area>`
  - child: `I<nnnn>_<Object>_…_<SrcSys>_<TgtSys>_<Sender>To<Receiver>`
- **[SSAB only]** A child of a dispatcher has the sender part `JMS`: SmarTeam `…_JMSToHTTP`. The FSAP Medius children stay `…_PDToREST` (user, 2026-11-23).
- **[Generic pattern, SSAB value]** Step names:
  - `Set Monitoring Identifiers` (first Content Modifier)
  - `LogCustomHeaders` (every Script step that runs `logCustomHeaders.groovy`)
  - `Send To JMS` (the JMS send step in parents)
  - `Set JMS Header Parameters` (a parent with one receiver)
  - local process `Main Process`; retrigger process `Manual Retrigger`
- **[Generic pattern, SSAB value]** Participant names (the generic rule "plain system name" is in `CLAUDE.md`):
  - SSAB names: `MSAP`, `MSAP_BOM`, `MSAP_FLOC`, `SmarTeam`, `CI`, `CI_MAIL`, `FinMessageHub`
  - the ProcessDirect sender from the system: `MSAP`
  - the HTTPS retrigger sender: `Retrigger`
  - the DLQ receiver in a dispatcher: `<SenderParticipant>_DLQ`
- **[Generic pattern, SSAB value]** Parameter names: `HTTP_<Setting>`, `<System>_<Setting>` (`MSAP_Host`, `Medius_Host`), `JMS_*`, `PD_Address`, `HTTPS_Address` (IFLOW_CONVENTIONS §2.4).
- **[SSAB only]** Message mapping names: `Map_<Src>_<Tgt>_<Object>_<MsgType>` (IFLOW_CONVENTIONS §2.2).
- **[SSAB only]** Versions (§5): major per project, minor per CR / SR / production fix, micro per change during development. The version comment carries the project or SR ID.

## 4. How the JMS dispatcher is set up
- **[SSAB only]** Shared dispatchers, one per target system and process stream, not one per pair: parent → JMS queue → `I07nn_P_JMSDispatcher_…` → ProcessDirect → child.
  - The parent sets header `SSAB_Dispatcher_ReceiverIFlow` = child iFlow name.
  - The dispatcher routes to `/${header.SSAB_Dispatcher_ReceiverIFlow}`.
  - Detail: `_reference/IFLOW_CONVENTIONS.md` §1.1–1.3.
- **[SSAB only]** Dispatcher numbers I07XX/I08XX are created only by the Central Integration team (§3.10.5.7–8).
- **[SSAB only]** Deploy the child before the parent (§3.10.5.4).
- **[Generic pattern, SSAB value]** Properties to the child: pass headers. `CopyPropertiesToHeader` / `CopyHeaderToProperties` only as a last resort (§3.10.5.6).
- **[Generic pattern, SSAB value]** Routing: a Router (multicast) for 2–5 receivers. The Groovy Receiver Determination for 5 or more, or when "No receivers found" must be an error (§4.1.2.1).

## 5. How payloads are logged
- **[Generic pattern, SSAB value]** Only with the script collection `UTIL_LogPayloadAsAttachment`, never an own script (§1.5).
  - The properties `LogPayload` (default false) and `LogPayloadSize` (KB) are set in `Set Monitoring Identifiers` and externalized.
  - `AttachmentName` is never externalized (§1.2.1).
- **[SSAB only]** It logs only when the tenant flag `SSAB_LogPayloadAsAttachment` (Partner Directory, default true) **and** `LogPayload` are true. The tenant size default is `SSAB_LogPayloadAsAttachment_Size` = 1024 KB.

## 6. How custom headers are logged
- **[Generic pattern, SSAB value]** Only with the reusable script `UTIL_LogCustomHeaders` (`logCustomHeaders.groovy`). Properties named `CH_<Name>` (String).
  - In the monitor, search them with "Use More Fields", `Name=Value`.
  - Log `${exception.message}` to a custom header when needed.
- **[SSAB only]** The customer prefix `SSAB_` for custom headers, e.g. `SSAB_Dispatcher_ReceiverIFlow`.

## 7. Sender role, Allowed Headers, shared helper flows
- **[Generic pattern, SSAB value]** Never CPI's default role `ESBMessaging.send` (rule in `CLAUDE.md`). SSAB roles:
  - each sending system gets `SSAB_MessagingSend_<System>`, e.g. `SSAB_MessagingSend_SmarTeam`
  - **child iFlows always `SSAB_MessagingSend_InternalOperations`**
  - **parents:**
    - never change the role of a parent whose main entry is HTTPS
    - when the HTTPS sender is only the retrigger (SOAP/IDoc/AMQP parents), it gets `SSAB_MessagingSend_InternalOperations` (I2018_P, I2023_P, I2024_P)
  - the guide §3.3.2 says `SSAB_Internal_Operations`; what we built is correct (user, 2026-11-23)
- **[Generic pattern, SSAB value]** CSRF protection: always ask. SSAB default: off (`HTTP_CSRFProtected=0`).
- **[Generic pattern, SSAB value]** Allowed Headers:
  - never `*` in a sender's Allowed Headers or a receiver's request headers (§3.7.1)
  - child iFlows: `{{AllowedHeaders}}` = `SSAB.*|SAP.*`
  - dispatcher: `AllowedHeaders=SSAB.*`
- **[SSAB only]** Shared helper flows over ProcessDirect instead of own channels. The list is in `_reference/IFLOW_CONVENTIONS.md` §1.5:
  - IDoc/XI receivers per SAP system: `I0076`–`I0082`, `I2004`, `I0525`
  - MDM lookup `I0096_P_MasterData_MDMLookup_PDToHTTP`
  - mail `/I0031_P_UTIL_SendEmail_JMSToMail`
- **[SSAB only]** ERP IDoc and ABAP-proxy senders go through the generic dispatchers `I0002_P_IDocDispatcher_SAPHR_IDocToPD` / `I0009_P_XIDispatcher_Asynch_StripSAP_XIToPD`. ODEX EDI uses the template `ODEX_Sender_Asynch_EDI_ParentFlow` (guide §4).

## 8. Other SSAB conventions
- **[Generic pattern, SSAB value]** Structure (§3.1–3.4):
  - all logic in a local process `Main Process`, called from each entry point
  - at most 15 steps per local process; lookups, backend checks and exception handling get their own local process
  - layout left to right
- **[Generic pattern, SSAB value]** Two entry points (§3.3): the source process and a `Manual Retrigger` HTTPS process. The retrigger needs a payload attachment named `IncomingPayload`.
- **[Generic pattern, SSAB value]** Mandatory externalized (§3.6): `SAP_Sender`, `SAP_MessageType`, `MaxRetries` (JMS), `LogPayload`, `LogPayloadSize`, and every Content Modifier value.
- **[Generic pattern, SSAB value]** HTTP session handling (§3.9):
  - "On Integration Flow" (one user per host), externalized
  - "None" only with different users for the same host
- **[Generic pattern, SSAB value]** Delete properties that hold a payload as soon as they are no longer needed. Never put a payload in a header (§3.7.1.3–4).
- **[Generic pattern, SSAB value]** Mapping: graphical message mapping first; XSLT or Groovy only when the graphical one gets too hard (§3.14).
- **[SSAB only]** Where we deliberately differ from the guide (user, 2026-11-23; the guide gets updated later):
  - the ProcessDirect and HTTPS sender addresses **are** externalized (`PD_Address`, `HTTPS_Address`)
  - child names stay as built
  - `JMS_RetentionThresholdAlerting = 2` on the FSAP parents
  - the retrigger role `SSAB_MessagingSend_InternalOperations`
- **[SSAB only]** Security, transport (Cloud TMS) and operations (queue and failure alert flows I0006, I0027; mass deploy I0024/I0025): `docs/explained/ssab_best_practices_guide.md` §2, §6, §7.

## Where the code enforces SSAB values
The iFlow code is not split by customer yet (planned cleanup). These places hold SSAB values:
- **`tools/iflow_build_smarteam.py`**:
  - `SENDER_DEFAULT` (`AD1_110`), `CHILD_ROLE`, `CHILD_ALLOWED_HEADERS`
  - `KNOWN_PARTICIPANTS`, `LOGCH_NAME`, `JMS_STEP_NAME`, `MSAP_RENAMES`, `SMARTEAM_HTTP`
  - the checks `participant_name_errors`, `monitor_header_errors`, `logch_name_errors`
- **`tools/iflow_lib.py`**: `best_practice_flags` reports by SSAB guide section (§3.x).
- **`tools/iflow_build_fsap_dispatcher.py`, `iflow_build_tibnor.py`, `iflow_build_tibnor_inbound.py`**: SSAB queue names, dispatcher numbers, roles and participant names.

For another customer, don't run these builders unchanged. Ask first.

## Detail files (evidence)
- `_reference/IFLOW_CONVENTIONS.md`: patterns and naming observed in the SSAB exports, plus Q&A
- `docs/explained/ssab_best_practices_guide.md`: summary of the SSAB Integration Suite Best Practises v1.9 (SharePoint, SSE IT - SAP Integration Suite › 20. Development)
- `docs/explained/jms_dispatcher_architecture.md`: the Simplified Pipeline
- `docs/explained/iflow_scan_findings.md`: the scan of all SSAB reference iFlows
- `_reference/iflows/`: the SSAB iFlow exports (L1)
