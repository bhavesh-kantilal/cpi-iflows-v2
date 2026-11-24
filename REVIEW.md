# Actions to review

**Review 2026-11-15:** all proposals A1–A13 and toolkit changes B1–B6 were accepted by the user and applied (CLAUDE.md, FORMAT_NOTES; ORDERS 1.1.1, DESADV 1.0.1, INVOIC 1.0.1, NShift 1.0.2). The explanation of A3/A4 and of the ORDRSP namespace issue is in `docs/explained/wsdl-imports-and-namespaces.md`. Sections C (business assumptions) and D are still open.

The user asked (2026-11-13) to review all actions of this session later. This list collects what was done or proposed without a full review. Nothing in **Proposed** is applied until the user approves it.

Status: `Open` = not reviewed yet · `OK` = reviewed and accepted · `Changed` = reviewed and changed · `Rejected`

## A. Proposed rule changes (waiting for approval, NOT applied)
| # | Proposal | Where | Why | Status |
|---|---|---|---|---|
| A1 | Add to "Checks before finishing a build": **6. All type / element references in the zip's XSD and WSDL files resolve** (`check.py: schema_ref_errors`; runs inside every build already). | CLAUDE.md | NShift v1.0.0: a WSDL whose types did not resolve passed every check, and CPI showed an empty Consignment | OK (applied 2026-11-15) |
| A2 | In the sample-files rule, refer to `tools/sim_copy.py` for the `*_sim.xml` copies | CLAUDE.md | Same step, done by a tool since DESADV/INVOIC | OK (applied 2026-11-15) |
| A3 | Rule for target WSDLs that import XSDs by URL: download (with approval), keep them in `schemas/downloaded/`, build a self-contained copy with `tools/wsdl_inline.py` | CLAUDE.md or FORMAT_NOTES §1.1 | CPI does not fetch external imports (NShift) | OK (applied 2026-11-15) |
| A4 | Note in FORMAT_NOTES §2.2: WSDL link elem 3 = message **element** name, once CPI confirms it on NShift (`book` vs message `ConsignmentEndpoint_book`) | FORMAT_NOTES | Still UNVERIFIED (NShift OP-12) | OK (applied 2026-11-15) |
| A5 | FixValues **"Use Key" = `vmstrategy 2`**, empty default (user feedback ORDRSP 2026-11-15; closes part of §5 Q1) | FORMAT_NOTES §3.11, §5 | ORDRSP MENEE | OK (applied 2026-11-15) |
| A6 | Optional **item** segments (E1EDP03, E1EDP19…) come from the filtered value chain (`ifWithoutElse` → `removeContexts` → `SplitByValue`), **not** from `createIf` on a per-child condition: its SUPPRESS values hide the segments of other items | FORMAT_NOTES §3.5/§3.6 + CLAUDE.md conventions | ORDRSP feedback 2026-11-15 | OK (applied 2026-11-15) |
| A7 | Header value on every item: **`CopyValue` index 0** instead of `useOneAsMany` (once the ORDRSP test confirms BELNR) | CLAUDE.md conventions | ORDRSP feedback 2026-11-15 | OK (applied 2026-11-15) |
| A8 | **Layout rule:** share logic between targets only when the canvas stays clean (no overlap, shared brick in one column); otherwise split. Build check `layout_overlaps` | CLAUDE.md conventions + checks list | ORDRSP feedback 2026-11-15 | OK (applied 2026-11-15) |
| A9 | **`udf_library/`** in the folder layout: reusable UDFs, copied unchanged into a mapping's `scripts/`. Rule: standard `substring` first, `substringSafe` only when the length is not certain | CLAUDE.md | ORDRSP feedback 2026-11-15 | OK (applied 2026-11-15) |
| A10 | Apply A6/A7 to DESADV and INVOIC too (they use `useOneAsMany` / `createIf` the same way), and rebuild ORDERS, DESADV, INVOIC, NShift with the new layout at their next version | mappings | Consistency | OK (applied 2026-11-15) |
| A11 | **Attribute context rule:** an attribute's default context is its own element. When it is compared with that element's own value (`Date/@Type` vs `Date`, `AddArticleNo/@Type` vs `AddArticleNo`), set the attribute's context to the parent (e.g. Item). Not needed when it is compared with a child element (`Quantity/@Type` + `QuantityValue`). This changes the CLAUDE.md rule "no context settings on lower-level source fields". Use the same aligned chain for a segment and its fields: a misaligned chain can still give the right segment count (a segment only counts values) while the field values are wrong (ORDRSP E1EDP03 v1.0.4 → v1.0.5) | CLAUDE.md conventions + FORMAT_NOTES §3.6 | ORDRSP v1.0.4/v1.0.5 (user's CPI fix) | OK (applied 2026-11-15) |
| A12 | **createIf rule:** a segment with `createIf` gets `removeContexts` after it and straight child maps; never `createIf` on the segment together with `ifWithoutElse` on its fields. Otherwise build the segment and its fields from one filtered chain | CLAUDE.md conventions + FORMAT_NOTES §3.5 | ORDRSP v1.0.4 (feedback_v2) | OK (applied 2026-11-15) |
| A13 | Check DESADV, INVOIC and NShift for the same patterns (attribute vs its own element, header `createIf` without `removeContexts`) | mappings | Consistency | OK (applied 2026-11-15) |

## B. Toolkit changes made without separate approval (already committed)
| # | Change | Commit | Status |
|---|---|---|---|
| B1 | `Builder.out(x, 0)` writes a plain `<arg>` instead of `from="0"` (FORMAT_NOTES §3.10). ORDERS/ORDRSP builds are logically unchanged. | c051eb8 | OK |
| B2 | New `tools/sim_copy.py` (simulator copies without `xsi:` attributes) | c051eb8 | OK |
| B3 | New `tools/wsdl_inline.py` (self-contained WSDL). v1 lost namespace declarations; fixed and self-checking since 75a7f4d | 7fcc03c, 75a7f4d | OK |
| B4 | New build check `schema_ref_errors` in `tools/cpimm/check.py`, run by `check_build` for every zip | 75a7f4d | OK |
| B5 | Group-aware layout + clean-or-split sharing in `Builder.finish` / `_layout`; build check `layout_overlaps`. In-memory test: all 5 mappings 0 overlaps, logic unchanged (diff) | ORDRSP v1.0.3 commit | OK |
| B6 | New `udf_library/` (README + `substringSafe.groovy`) | ORDRSP v1.0.3 commit | OK |

## C. Mapping decisions and assumptions to confirm
| # | Mapping | Item | Status |
|---|---|---|---|
| C1 | ORDRSP | DATUM / EDATU carried the full range (user's temporary fix). **Fixed in v1.0.3** with `substringSafe(…, 9, 17)` after the filter, per the user's feedback document | OK (to test in CPI) |
| C2 | ORDRSP | "Some fields missing" in the user's v1.0.1 test (not specified yet) | Open |
| C3 | ORDRSP, DESADV, INVOIC | Does the iFlow runtime accept `xsi:schemaLocation` / `xsi:noNamespaceSchemaLocation` in real hub payloads (simulator does not)? | Open |
| C4 | ORDRSP, DESADV, INVOIC | PO pattern assumes exactly one value per item per qualifier; values shift if one is missing | Open |
| C5 | INVOIC | A1 ZEILE for METOCSTO (`000001` → Implema sent `10`), A2 only DocumentType 380 | Open |
| C6 | DESADV | Grouping UDF `groupByHeat`: key line + Heat, number format "as sent / sum without decimals" (A1, A2); all dates = DespatchDate (A3) | Open |
| C7 | DESADV | Folder `Samples` should be renamed `samples` (rename was refused, folder in use) | Open |
| C8 | NShift | All best-guess rules A1–A14 and open points OP-01–OP-12 in `spec.md` / the spec workbook, mainly: one consignment per freight order vs per house waybill (OP-01), template per carrier (OP-02), package codes (OP-04), re-booking / transactionId (OP-05) | Open |
| C9 | NShift | Mapping name `Map_TibnorS4_NShift_TransportOrder_Book` was chosen by Claude, not given by the user | Open |
| C10 | NShift | The spec workbook `S4TM-NShift_TransportOrder_Book_MappingSpec_v0.1.xlsx` was written by Claude (layout copied from the INVOIC workbook) | Open |
| C11 | All | Control record handled as ORDRSP: SNDPOR / RCVPOR / RCVPRN from exchange properties, STD constants, REFMES empty | Open |
| C12 | MAT (`Map_Material_SmartTeam` › `Descriptions/Description/@lang`) | Context on `Description/@languageCode` (to `Product/Description`): works for 0/1/2 languages, reason not recalled, not deeply tested (user, re-learn Q6) | Open (later) |
| C13 | DESADV | `groupByHeat` UDF vs the user's standard: XSLT sort in the iFlow + SplitByValue value change + formatByExample + sum. Decide in the iFlow phase (re-learn Q1) | Open |
| C14 | I0544 BP Medius | `CleanNamespace.groovy`: read from the iFlow as "namespace-free copy for the splitter XPath, original restored before the mapping" (L4). Please confirm when convenient | Open |
| C15 | I0544 JDBC vs I0544 BP Medius | Why `removeXSINil` exists only before `MapBPToDDSJDBC` and not before `SupplierMastertoMedius` (user doesn't know) | Open (later) |

## A2. Proposals from the re-learn (waiting for approval)
| # | Proposal | Where | Evidence | Status |
|---|---|---|---|---|
| R1 | SplitByValue "value change" groups consecutive equal values only: **always ask the user** whether to sort first (XSLT in the iFlow) or not (changed by the user 2026-11-15) | FORMAT_NOTES §3.6 + CLAUDE.md conventions | L2 (user, Q1) + L1 (I0115 `SortByTaxLines` before ACC and INV) | OK (applied 2026-11-15) |
| R2 | UDF call-out, question format, re-learn includes the iFlow (text in the chat of 2026-11-15) | CLAUDE.md | User request | OK (applied 2026-11-15) |
| R3 | To lift a field to a higher level, set `context=` on the source (JournalEntry style, shows in italics in the editor). Use `removeContexts` only when all contexts must be removed | CLAUDE.md conventions + FORMAT_NOTES §3.6 | L2 (user, Q3) + L1 (JE ProductTaxItem, INV GLACCOUNTDATA) | OK (applied 2026-11-15) |
| R4 | `mapWithDefault` after a context change only when the business context guarantees at most one occurrence per new context (e.g. an invoice header field). Otherwise `mapWithDefault` in the field's own context first, then `removeContexts` / `formatByExample` | FORMAT_NOTES §3.6 (narrows the ORDRSP v1.0.0 statement) | L2 (user, Q4) + L1 (ACC item[6], SUP identifiers) | OK (applied 2026-11-15) |
| R5 | Case by case: only when the source provides no line numbers, consider the standard `counter` (`ini`/`inc` as needed, e.g. `ini=2` when line 1 is reserved for the vendor line). A UDF only if `counter` can't do it | CLAUDE.md conventions | L2 (user, Q5) + L1 (ACC, JE, INV: 24 uses) | OK (applied 2026-11-15) |
| R6 | **Check, not rule:** before building, ask whether a step belongs in the iFlow: sort before value-change grouping (R1), split when the target expects one message per object (Q10), XSLT for grouping/filtering/moving whole segments (Q9), remove `xsi:nil` fields that clutter the mapping (Q11); otherwise prefer a UDF over XSLT. Decide per interface with the user, name it in `spec.md`, call it out | CLAUDE.md conventions | L1 (14 iFlows) + L2 (Q9–Q11) | OK (applied 2026-11-15) |
| R7 | `exists` (1 input) = true when the source node is present; use where it reads more clearly than `mapWithDefault` (no hard rule) | FORMAT_NOTES §3.4 | L1 (I0541 `isActive`) + L2 (Q7) | OK (applied 2026-11-15) |

## A3. Proposals from the I0539 iFlow feedback (2026-11-16, waiting for approval)
| # | Proposal | Where | Evidence | Status |
|---|---|---|---|---|
| F1 | **HTTPS sender role and CSRF: always ask.** SSAB default is `SSAB_MessagingSend_InternalOperations` with CSRF off | CLAUDE.md (iFlow section) + IFLOW_CONVENTIONS | L2 (I0539 feedback doc) | OK (applied 2026-11-16) |
| F2 | **Externalize every adapter setting someone may tune** (timeout, proxy, throw exception, retry, authentication, allowed headers, host, body size, PD address). Use the names `HTTP_<Setting>`. When several channels go to the same system, they share one set | IFLOW_CONVENTIONS §1.4, §2.4 + CLAUDE.md | L2 (I0539 feedback doc), L3 (v1.1.0 tested) | OK (applied 2026-11-16) |
| F3 | **Diagram rule:** a build that changes process flows must also update BPMNDiagram. Drop orphan shapes and edges, give each flow an edge, and give each step a shape. Enforced by `iflow_lib.check_iflow` in the build and `tools/check_all_iflows.py` | CLAUDE.md (iFlow section) | L2 (I0539 v1.0.0: "Main Process connection missing") | OK (applied 2026-11-16) |
| F4 | Apply I0539 v1.1.0 to the other FSAP iFlows. `check_all_iflows.py` reports the same orphan/missing-edge problem in I0539_P, I0541_P and I0545_P | iflows | `py -I tools/check_all_iflows.py` | Children done (I0541/I0545 v1.1.0). Parents: diagram and model refs fixed in 2.0.1 (2026-11-16); externalization/role/CSRF for parents not done yet (user is testing) |
| F5 | Fix the typo `AlowedCompanies` → `AllowedCompanies` in every FSAP iFlow that has it | iflows | L2 (user, 2026-11-16) | Children done (I0539, I0545; I0541 had no typo); parents to check |
| F6 | Open questions from I0541/I0545: (a) I0541 "Allowed Request Headers" is empty, but `Content-Type` in the others. Set it the same? (b) I0545 `SAP_Sender=FD1-110` vs `FD1_110` elsewhere. Which is right? | iflows | L4 → L2 | OK: (a) ignore; (b) `FD1_110` is right, fixed manually by the user in CPI (2026-11-16) |

### Toolkit changes (I0539 v1.1.0)
- New `tools/iflow_lib.py`: `fix_diagram`, `externalize`, `add_table_row`, `Params` (prop + propdef together), `check_iflow`.
- `tools/iflow_build_fsap_dispatcher.py`: `--only <iFlow>` switch, and a `post=` hook in `_build_child_pdtorest` that runs the checks.
- `tools/check_all_iflows.py`: now also runs the diagram and wiring checks.
- I0541/I0545 v1.1.0: `pd_child_feedback_v110(name, body_step, monitor_step, extra_layout, extra)` is the generic version of the I0539 change. The Process_1 layout is placed relative to the pool. `fix_diagram` also redraws edges whose ends no longer match (I0541 splitter removal).
- Retrigger urlPath bug: v1.0.0 only replaced names ending in `JMSToREST`, so I0541 kept `…_SOAPToREST`. Now it is always set to `/<iFlow name>`.
- Parents 2.0.1:
  - `iflow_lib.sync_flow_refs` and `remove_sequence_flow`
  - `fix_diagram(shift=…)` and edge routing by direction (side, down, up)
  - new check: incoming/outgoing match the flows
  - `fix_parent_diagram` in the build script
  - new `tools/iflow_render.py` (SVG preview)
  - The I0541_P duplicate flow `SequenceFlow_IOSplit_in` is removed.

## A4. Proposals from the SmarTeam round (2026-11-23, waiting for approval)
| # | Proposal | Where | Evidence | Status |
|---|---|---|---|---|
| S1 | **Custom header logging:** calling `logCustomHeaders.groovy` again later in the flow is safe. CPI does not duplicate a CH_ value that is already logged; a changed value is added as a new line, and the old one stays. So log a new CH_ property right where its value becomes known (e.g. the response WorkId), without deleting the earlier CH_ properties | `_reference/IFLOW_CONVENTIONS.md` (logging) | L2 (user, 2026-11-23) | Open |
| S2 | **Child naming in the Simplified Pipeline:** children are named `I<id>_<Object>_<Src>_<Receiver>_JMSToHTTP` even though they start with ProcessDirect. The PD address and the HTTPS retrigger path = `/<child name>`. Update `docs/explained/jms_dispatcher_architecture.md`, which still says `_PDToHTTP` | IFLOW_CONVENTIONS §2 + docs | L2 (user, 2026-11-23) + L1 (I2018/I2023/I2024 exports) | Open |
| S3 | **iflw file name = iFlow name.** Copy leftovers such as `I0579_CostCentre…JMSToSOAP.iflw` are renamed in every build | IFLOW_CONVENTIONS | L2 (user, 2026-11-23) | Open |
| S5 | **OData GET receivers:** CSRF off (a GET needs no token), and externalize Delete Idle Connection (`<System>_DeleteIdleConnection`, default true) and Idle Timeout (`<System>_IdleTimeout`, default 300) | IFLOW_CONVENTIONS §1.4 | L2 (Bhavesh's I2050_P 1.0.5, 2026-11-23) | Open (applied to I2049_P, I2023, I2024) |
| S6 | **XPath: no `local-name()`** unless Bhavesh asks or there is a logical reason. Use plain paths that match the real message (check against a sample or the mapping source XSD). When only the root element has a namespace (SAP ESR messages, children unqualified), use `/*/child/…` | CLAUDE.md (applied: user's explicit instruction) + IFLOW_CONVENTIONS | L2 (user, 2026-11-23) | OK (CLAUDE.md) |
| S7 | **Logging parameters in every flow:** `LogPayload` and `LogPayloadSize` (default 512 = 512 kB) are always externalized and set in "Set Monitoring Identifiers". Build check `empty_logpayload_rows` rejects an empty row | IFLOW_CONVENTIONS §1.4 | L2 (user, 2026-11-23; I2049_P/I2050_P had an empty row) | Open |
| S8 | **Child iFlows: `AllowedHeaders` = `SSAB.*\|SAP.*`, externalized.** Update IFLOW_CONVENTIONS §1.4, which only mentions `SSAB.*` in the dispatcher | CLAUDE.md (applied: user's explicit instruction) + IFLOW_CONVENTIONS | L2 (user, 2026-11-23) | OK (CLAUDE.md); IFLOW_CONVENTIONS open |
| S9 | **Step name `LogCustomHeaders`** for every logCustomHeaders.groovy step. Also add to IFLOW_CONVENTIONS §1.4 (shared pieces) | CLAUDE.md (applied: user's explicit instruction) + IFLOW_CONVENTIONS | L2 (user, 2026-11-23, screenshot) | OK (CLAUDE.md); IFLOW_CONVENTIONS open |
| S10 | **Step name "Send To JMS"** for the JMS send step in parents (applied to all 5 SmarTeam parents) | CLAUDE.md (applied) + IFLOW_CONVENTIONS | L2 (user, 2026-11-23, screenshot) | OK (CLAUDE.md, all 5 parents); IFLOW_CONVENTIONS open |
| S11 | **No fixed adapter values.** Every non-empty adapter setting is `{{…}}` (build check `fixed_adapter_values`; only technical fields and the shared mail utility PD address are exempt). New names: `SmarTeam_*`, `MSAP_*` (OData in children), `PD_Address`, `HTTPS_Address`, `S4_RetryIterations` / `S4_RetryInterval`. Not seen in a tested reference (UNVERIFIED until CPI test): `SmarTeam_RetryOnException`, `SmarTeam_IdleTimeout`, OData `maxRetryIterations` / `retryIntervalSec` / `whitelist*Headers` references | IFLOW_CONVENTIONS §1.4 | L2 (user, 2026-11-23) | Open |
| S12 | **Sender role:** children always `SSAB_MessagingSend_InternalOperations`; parents never changed, except a retrigger-only HTTPS sender in a SOAP/IDoc/AMQP parent (→ SSAB role). Replaces "always ask" for the role (F1). Update IFLOW_CONVENTIONS §1.4 | CLAUDE.md (applied: user's explicit instruction) + IFLOW_CONVENTIONS | L2 (user, 2026-11-23) | OK (CLAUDE.md); IFLOW_CONVENTIONS open |
| S13 | **Location ID always externalized with Proxy Type** (even empty) | CLAUDE.md (applied) + IFLOW_CONVENTIONS §1.4 | L2 (user, 2026-11-23) | OK (CLAUDE.md); IFLOW_CONVENTIONS open |
| S14 | **Monitoring headers per the user's blog** (SAP_Sender/SAP_Receiver/SAP_MessageType as `{{same name}}` in the first Content Modifier, SAP_ApplicationID by XPath, IDoc MessageType XPath, custom headers via UTIL_LogCustomHeaders) | CLAUDE.md (applied) + IFLOW_CONVENTIONS | L2 (user's blog, 2026-11-23) | OK (CLAUDE.md); IFLOW_CONVENTIONS open; gaps in the SmarTeam flows open |
| S15 | **Canvas and naming best practices** (user, 2026-11-23): no overlapping pools/steps (move neighbouring pools when a pool widens); participant names unique (sender, receiver, local process); plain system name for receivers, `MSAP_<Purpose>` only when `MSAP` is taken, `Retrigger` + process `Manual Retrigger`, `CI`, `CI_MAIL`; ask before renaming | CLAUDE.md (applied) + IFLOW_CONVENTIONS | L2 (user, 2026-11-23: I2024 overlap, I2023_P CPI fix, MSAP_FLOC, Manual Retrigger) | OK (CLAUDE.md); IFLOW_CONVENTIONS open |
| S4 | **Runtime `.jar` as input:** the build turns it into a design-time zip (keep `src/main/resources/**`, design MANIFEST, add `.project` + `metainfo.prop`). The rule is proven byte for byte on the I2049 jar/zip pair (`iflow_build_smarteam.py --selftest`). Import of a converted build in CPI is UNVERIFIED until the I2050 1.0.4 test | IFLOW_CONVENTIONS / tools/README | L2 (I2049 pair), L4 until tested | Open |

### Toolkit changes (SmarTeam, 2026-11-23)
- New `tools/iflow_build_smarteam.py`:
  - jar → design-time conversion with `--selftest`
  - MANIFEST parse/write with 72-byte wrapping
  - `error_end_to_message_end`
  - `insert_step_after` (copies a step and rewires the flows)
  - removal of unused parameters
  - typo check (`Maintanance`, `PDToHTTP` forbidden in the output)
- `tools/check_all_iflows.py` accepts `<Package>/<IFlowName>` entries and now also checks the I2050 child and parent.
- `iflow_lib.Params.keys()` now undoes java.util.Properties escapes (`Body\ Size` → `Body Size`), and `remove()` matches escaped keys. Before, parameters with spaces were reported as unused although `{{Body Size}}` used them (I2050_P). The FSAP checks still pass.
- Folder layout per CPI package (`iflows/<Package>/source/` + `iflows/<Package>/<IFlowName>/`), with `iflowdevelopment/` as the single drop folder. CLAUDE.md is updated (user choice, 2026-11-23).

## A5. Segment-level filter (ORDERS v1.2.0 feedback, 2026-11-24)
| # | Lesson | Where | Evidence | Status |
|---|---|---|---|---|
| S16 | **Filter at segment level, map the fields 1:1**: `createIf(qualifier [context = parent of the source segment] = X)` on the target segment; its fields are straight maps of the same source segment. SUPPRESS skips the children's contexts. A filtered chain only where the value is the element itself or a field mixes segments | CLAUDE.md + FORMAT_NOTES §3.5 (applied) | L2 (user's CPI mapping `… (1).zip`, Party SE/BY/CN; explanation confirmed in chat 2026-11-24) | OK (approved with the plan, 2026-11-24) |

## D. Other actions taken
| # | Action | Status |
|---|---|---|
| D1 | Files moved into the standard layout (schemas/, samples/, docs/) in ORDRSP, DESADV, INVOIC, NShift. Originals unchanged in content | Open |
| D2 | Two NShift XSDs downloaded from `https://service.web-ta.net/ws/services/ConsignmentWS?xsd=1/2` (approved by the user) | Open |
| D3 | ORDRSP input samples re-indented on disk were committed; user chose to keep them | OK |

## E. Import tests reported by the user
- ORDRSP v1.0.2: runs, "some fields missing" (C2).
- ORDRSP v1.0.3: tested by the user; fixes in CPI (E1EDK02 001, attribute contexts) taken over as v1.0.4. E1EDP03 made consistent in v1.0.5 (user).
- Proposal: add ORDRSP v1.0.5 (CPI download after the user's test) to `_reference/` as a new reference export (user's README entry, then "learn new references").
- DESADV v1.0.0, INVOIC v1.0.0: "everything works" (user, 2026-11-13). No CPI download yet, so no `feedback/` diff.
- NShift v1.0.1: "this works" (user, 2026-11-13). The target structure loads after the WSDL fix.
