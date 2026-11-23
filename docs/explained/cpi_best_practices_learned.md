# CPI Best Practices — what Claude has learned so far (SSAB)

Plain-language summary of everything taught through references, feedback rounds and Q&A (Nov 2026).
Each point is a rule you gave, or a lesson proven in CPI. Details and evidence live in `CLAUDE.md`,
`_reference/FORMAT_NOTES.md` and `_reference/IFLOW_CONVENTIONS.md`.

---

## Part A — Message Mappings

### Way of working
- Ask, don't assume: unclear columns, conditions, contexts, cardinality or value-mapping agencies are asked, and every answer is written into the mapping's Decisions log.
- Only build what has been seen working in a real SSAB export. Anything new is a stop-and-ask.
- Mapping name: `Map_<Src>_<Tgt>_<Object>_<MsgType>`, given by you. Zip, `.mmap` and iFlow step all use the same name.
- After testing in CPI, your download is the truth. Your fixes are taken over, but anything that contradicts the spec or samples is flagged, not copied blindly.
- Every version gets a changelog line with date and time.

### Structure and nodes
- **Container nodes** (only hold children) are fed by an empty constant; if the node is optional, by `createIf`.
- **Value nodes** (even with attributes, like `Reference`, `PartyId`, `Date`) keep their source value.
- **Repeating nodes** follow their source occurrence (e.g. `Item` ← `E1EDP01`).
- Header value on every item: `CopyValue(value, 0)`, not `useOneAsMany`.

### Functions
- **Standard functions first**, UDFs only when nothing standard does the job (e.g. `count`, not a counting UDF).
- Reuse a known UDF unchanged before writing a new one. Every new UDF is explained: why, the standard alternative, and why not.
- Leading zeros: `formatNumber` (`#`) for always-numeric values; `removezeros` UDF only when the value can contain letters.
- `substring` when the length is guaranteed; the safe variant only when it isn't.
- Value tables: FixValues with "Use Key" so unknown values pass through (e.g. M → MTR), instead of if-then-else chains.

### Qualifiers, contexts and conditions (the hard part)
- Qualifier filters (e.g. `Quantity[@Type='21']`) follow your PO pattern, no UDF. Risky transforms (substring) come **after** the filter.
- Context change only when an attribute is compared with **its own** element's value (`Date/@Type` vs `Date`). Attribute vs child element: no context change.
- A segment and its fields must come from **the same aligned chain**, otherwise counts look right but values land on the wrong line.
- `createIf` on a repeating condition → follow with `removeContexts`; fields are then straight maps.
- Never `createIf` on a segment plus `ifWithoutElse` on its fields. Optional item segments (E1EDP03, E1EDP19) come from one filtered chain: `ifWithoutElse` → `removeContexts` → `SplitByValue`.
- `mapWithDefault` after a context change only if there is at most one value per context; otherwise default first, then change context.
- Lifting a field up a level: prefer a context setting on the source; `removeContexts` when all contexts must go.
- `SplitByValue` "value change" only groups **consecutive** values → always ask whether the input must be sorted (sorting is an iFlow XSLT step, not a mapping trick).
- Line numbers: use the source's own; only if missing, the standard `counter`.

### Schemas and namespaces
- Qualified XSD (`elementFormDefault="qualified"`) → every element carries the namespace prefix; attributes never do.
- The source/target link must carry the root's namespace, or CPI asks to "Add source message".
- WSDLs that point to XSDs by URL: CPI never downloads them. Copy the WSDL, point `schemaLocation` to `../xsd/<file>.xsd`, ship the XSDs in the zip. Your original stays untouched.
- Every type reference inside the schemas must resolve, or CPI silently shows an empty structure.

### Testing in the simulator
- Sample files without an encoding declaration must be UTF-8.
- Remove `xsi:schemaLocation` from the root for simulation (`prefix "ns…" not bound` error). Original samples are never changed.

### Mapping vs iFlow — decide per interface
Before building, ask whether part of the job belongs in the iFlow instead:
- sort step before value-change grouping
- splitter when the target wants one message per object (e.g. Medius per supplier)
- XSLT for grouping, filtering or moving whole segments
- removing `xsi:nil` clutter

Otherwise a UDF is preferred over XSLT.

### Quality gate before handing over
- All paths exist in the schemas, all XML well-formed, zip layout like SAP's own exports.
- No overlapping boxes on the mapping canvas; shared logic only when it stays readable.
- No tool/AI traces in any file; owner fields empty.

---

## Part B — iFlows

### Architecture (JMS dispatcher pattern)
- **Parent → JMS queue → Dispatcher → ProcessDirect → Child → target.**
- One queue + one DLQ **per receiver system**, not per interface (tenant queue limit). A new interface to an existing receiver costs zero queues.
- Parent sets header `SSAB_Dispatcher_ReceiverIFlow` = child iFlow name; dispatcher routes on it.
- Child's ProcessDirect address = `/` + its own iFlow name, and must match exactly.
- Dispatcher: max-retries check, then DLQ (`<queue>_D`). DLQ receiver named `<Sender>_DLQ`.
- Migration is gradual: old and new style can live side by side in one parent.

### Naming
- Parent `I<nnnn>_P_<Object>_<Action>_<Src>_<Sender>To<Receiver>`; child same number without `_P_`.
- Sender part = the real inbound adapter (HTTP, JMS, PD); `PDToIDoc` still says IDoc so the target is clear.
- Queues: `I<nnnn>_<Receiver>`, DLQ `_D`. Custom headers/roles prefixed `SSAB_`, copied values `CH_`.
- **Participants**: plain system name (`MSAP`, `SmarTeam`, `CI`). Suffix (`MSAP_BOM`) only when that name is already taken in the same iFlow. Never `Receiver1`, `Sender`. Names must be unique; ask before renaming.
- Fixed step names: `LogCustomHeaders`, `Send To JMS`, `Set Monitoring Identifiers`, local process `Manual Retrigger`.

### Monitoring
- First Content Modifier sets headers `SAP_Sender`, `SAP_Receiver`, `SAP_MessageType` from same-named parameters.
- IDoc senders can derive the message type from MESTYP / IDOCTYP / CIMTYP.
- `SAP_ApplicationID` = the business key (e.g. `//DOCNUM`) for payload search.
- **Parents with several receivers never set `SAP_Receiver`**; only point-to-point flows and children do.
- Custom headers only via the shared `LogCustomHeaders` script (`CH_` properties).
- Allowed values for sender/receiver/message type: asked, never invented. SmarTeam sender = `AD1_110`.

### Externalization ("the more the better")
- Every adapter setting someone may tune becomes a parameter: timeout, proxy type, location ID, authentication, retries, allowed headers, host, body size, PD address.
- Naming `HTTP_<Setting>` or `<System>_<Setting>`; channels to the same system share one set.
- Location ID always next to proxy type, even when empty.
- Check **every** adapter in every round, not just the ones being changed; no "open points" left.
- Renaming a parameter (even a typo fix) loses the tenant value → you're told to set it again.

### Security
- Child iFlows: HTTPS role always `SSAB_MessagingSend_InternalOperations`, Allowed Headers `{{AllowedHeaders}}` = `SSAB.*|SAP.*`.
- Parents with HTTPS as main entry: role never changed. Parents where HTTPS is only the retrigger: internal-operations role.
- CSRF: always ask (SSAB default off).

### XPath
- No `local-name()` unless really needed. Plain paths checked against a real sample or schema; `/*/child/…` when only the root is namespaced.

### Diagram hygiene
- A change in the process flow also updates the drawing: no leftover shapes, every arrow connected, no gaps.
- No overlapping pools or steps; when a pool grows, everything to its right moves with it.

### Quality gate before handing over
- Well-formed, every step drawn and connected, step in/out links match the flow.
- Every `{{parameter}}` defined, nothing defined but unused.
- Manifest name = iFlow name, no tool/AI traces.

---

## How the learning works
- Evidence levels: your original export > your CPI download / statement > Claude build you tested > Claude's own analysis (marked unverified).
- New lesson → noted in the spec → proposed to you → becomes a rule only after your OK.
- Everything lives in the repo, not in Claude's memory.
