# JMS Queue Consolidation — Dispatcher Architecture

> **Customer-specific: SSAB / Tibnor** (one CPI tenant). Used through the skill `.claude/skills/ssab-tibnor/SKILL.md`. For another customer, ask before reusing anything here (CLAUDE.md "Which customer?").
Source: CPI_JMS_Queue_Consolidation.pptx (SSAB Integration, November 2026)

---

## The problem it solves

375 interfaces × (1 queue + 1 DLQ) = 750 queues against an 850-queue tenant limit.
Adding one interface costs two queues. The old pattern cannot scale.

---

## Core idea

**One JMS queue + one DLQ per receiver system**, not per interface.
A new interface to an existing receiver costs **zero** queues.

| Receiver | Queue | DLQ |
|---|---|---|
| SmarTeam | `I0700_SmarTeam` | `I0700_SmarTeam_D` |
| Medius | `I0xxx_Medius` | `I0xxx_Medius_D` |

---

## Three-layer flow

```
Parent iFlow (_P_)          Dispatcher iFlow           Child iFlow (_PDToHTTP)
─────────────────────       ────────────────────       ──────────────────────────
Write to receiver queue  →  Read queue, route via  →   Map + deliver to receiver
Set header:                 ProcessDirect using         (mapping, HTTP call, log)
  SSAB_Dispatcher_          header value
  ReceiverIFlow = child
  iFlow name
```

### 1 — Parent iFlow (sender side)
Naming: `I<id>_P_<Object>_<SrcSystem>_<Transport>ToJMS`
Example: `I2018_P_Material_MSAP_SOAPToJMS`

- `ReceiverDetermination.groovy` builds two parallel arrays:
  - `arr_receiversQueueList` — JMS queue name per receiver
  - `arr_receiversIFlowList` — child iFlow name per receiver
- **Send to Receivers** loop iterates over the arrays and for each receiver sets:
  - Property `QueueName` → JMS write target
  - Header `SSAB_Dispatcher_ReceiverIFlow` → child iFlow name (e.g. `I2018_Material_MSAP_SmarTeam_PDToHTTP`)
  - Header `SAP_MessageProcessingLogCustomStatus` → interface ID prefix (e.g. `I2018`)
- Old and new styles can coexist in the same parent (one receiver on old dedicated queue, another on the shared dispatcher queue).

### 2 — Dispatcher iFlow
Naming: `I0700_P_JMSDispatcher_<ReceiverSystem>`
Example: `I0700_P_JMSDispatcher_SmarTeam`

- Reads from the shared receiver queue (`I0700_SmarTeam`).
- Sets `SAP_MessageProcessingLogCustomStatus` from the header:
  `${header.SSAB_Dispatcher_ReceiverIFlow.split('_')[0]}` → e.g. `I2018`
- Routes via **ProcessDirect** using:
  `/${header.SSAB_Dispatcher_ReceiverIFlow}`
- Errors propagate back → JMS retry → DLQ after max retries.

### 3 — Child iFlow (receiver side)
Naming: `I<id>_<Object>_<SrcSystem>_<ReceiverSystem>_PDToHTTP`
Example: `I2018_Material_MSAP_SmarTeam_PDToHTTP`

- ProcessDirect address **= iFlow name** (must match the value the parent writes exactly).
- Holds all receiver logic: mapping, lookups, HTTP delivery, response logging.
- Manual retrigger via HTTPS kept for support.

---

## Key header

| Header | Set by | Value | Used by |
|---|---|---|---|
| `SSAB_Dispatcher_ReceiverIFlow` | Parent | Child iFlow name | Dispatcher (ProcessDirect routing) |
| `SAP_MessageProcessingLogCustomStatus` | Parent + Dispatcher | Interface ID prefix (`I<id>`) | MPL / queue monitor |

The custom status makes it possible to identify which interface wrote a message in the shared queue or DLQ.

---

## Naming convention (from PPTX + examples)

| Layer | Pattern | Example |
|---|---|---|
| Parent | `I<id>_P_<Object>_<Src>_<Transport>ToJMS` | `I2018_P_Material_MSAP_SOAPToJMS` |
| Dispatcher | `I<queueId>_P_JMSDispatcher_<Receiver>` | `I0700_P_JMSDispatcher_SmarTeam` |
| Child | `I<id>_<Object>_<Src>_<Receiver>_PDToHTTP` | `I2018_Material_MSAP_SmarTeam_PDToHTTP` |
| Queue | `I<queueId>_<Receiver>` | `I0700_SmarTeam` |
| DLQ | `I<queueId>_<Receiver>_D` | `I0700_SmarTeam_D` |

The child iFlow name must start with its interface ID (`I<id>`) — the dispatcher uses `split('_')[0]` to extract it for the custom status.

---

## Migration strategy

1. **Build child** — create `_PDToHTTP` child; move receiver logic from old consumer.
2. **Repoint parent** — update receiver determination to use shared queue + child iFlow name.
3. **Deploy** — child first, then parent (dispatcher already runs).
4. **Drain** — wait for old dedicated queue + DLQ to empty.
5. **Retire** — undeploy old consumer; delete old queue + DLQ to free capacity.

Old and new styles coexist in the same parent during migration. No big bang required.

---

## Capacity outlook

- ~200 receiver systems → ~400 queues (saves ~350 vs today's 750).
- Options under consideration: shared DLQ per domain; common dispatcher for small/single-interface receivers; JMS only for receivers needing guaranteed async delivery.
