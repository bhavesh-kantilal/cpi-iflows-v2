# Actions to review

The user asked (2026-11-13) to review all actions of this session later. This list collects what was done or proposed without a full review. Nothing in **Proposed** is applied until the user approves it.

Status: `Open` = not reviewed yet · `OK` = reviewed and accepted · `Changed` = reviewed and changed · `Rejected`

## A. Proposed rule changes (waiting for approval, NOT applied)
| # | Proposal | Where | Why | Status |
|---|---|---|---|---|
| A1 | Add to "Checks before finishing a build": **6. All type / element references in the zip's XSD and WSDL files resolve** (`check.py: schema_ref_errors`; runs inside every build already). | CLAUDE.md | NShift v1.0.0: a WSDL whose types did not resolve passed every check, and CPI showed an empty Consignment | Open |
| A2 | In the sample-files rule, refer to `tools/sim_copy.py` for the `*_sim.xml` copies | CLAUDE.md | Same step, done by a tool since DESADV/INVOIC | Open |
| A3 | Rule for target WSDLs that import XSDs by URL: download (with approval), keep them in `schemas/downloaded/`, build a self-contained copy with `tools/wsdl_inline.py` | CLAUDE.md or FORMAT_NOTES §1.1 | CPI does not fetch external imports (NShift) | Open |
| A4 | Note in FORMAT_NOTES §2.2: WSDL link elem 3 = message **element** name, once CPI confirms it on NShift (`book` vs message `ConsignmentEndpoint_book`) | FORMAT_NOTES | Still UNVERIFIED (NShift OP-12) | Open |
| A5 | FixValues **"Use Key" = `vmstrategy 2`**, empty default (user feedback ORDRSP 2026-11-15; closes part of §5 Q1) | FORMAT_NOTES §3.11, §5 | ORDRSP MENEE | Open |
| A6 | Optional **item** segments (E1EDP03, E1EDP19…) come from the filtered value chain (`ifWithoutElse` → `removeContexts` → `SplitByValue`), **not** from `createIf` on a per-child condition: its SUPPRESS values hide the segments of other items | FORMAT_NOTES §3.5/§3.6 + CLAUDE.md conventions | ORDRSP feedback 2026-11-15 | Open |
| A7 | Header value on every item: **`CopyValue` index 0** instead of `useOneAsMany` (once the ORDRSP test confirms BELNR) | CLAUDE.md conventions | ORDRSP feedback 2026-11-15 | Open |
| A8 | **Layout rule:** share logic between targets only when the canvas stays clean (no overlap, shared brick in one column); otherwise split. Build check `layout_overlaps` | CLAUDE.md conventions + checks list | ORDRSP feedback 2026-11-15 | Open |
| A9 | **`udf_library/`** in the folder layout: reusable UDFs, copied unchanged into a mapping's `scripts/`. Rule: standard `substring` first, `substringSafe` only when the length is not certain | CLAUDE.md | ORDRSP feedback 2026-11-15 | Open |
| A10 | Apply A6/A7 to DESADV and INVOIC too (they use `useOneAsMany` / `createIf` the same way), and rebuild ORDERS, DESADV, INVOIC, NShift with the new layout at their next version | mappings | Consistency | Open |
| A11 | **Attribute context rule:** an attribute's default context is its own element. When it is compared with that element's own value (`Date/@Type` vs `Date`, `AddArticleNo/@Type` vs `AddArticleNo`), set the attribute's context to the parent (e.g. Item). Not needed when it is compared with a child element (`Quantity/@Type` + `QuantityValue`). This changes the CLAUDE.md rule "no context settings on lower-level source fields" | CLAUDE.md conventions + FORMAT_NOTES §3.6 | ORDRSP v1.0.4 (user's CPI fix) | Open |
| A12 | **createIf rule:** a segment with `createIf` gets `removeContexts` after it and straight child maps; never `createIf` on the segment together with `ifWithoutElse` on its fields. Otherwise build the segment and its fields from one filtered chain | CLAUDE.md conventions + FORMAT_NOTES §3.5 | ORDRSP v1.0.4 (feedback_v2) | Open |
| A13 | Check DESADV, INVOIC and NShift for the same patterns (attribute vs its own element, header `createIf` without `removeContexts`) | mappings | Consistency | Open |

## B. Toolkit changes made without separate approval (already committed)
| # | Change | Commit | Status |
|---|---|---|---|
| B1 | `Builder.out(x, 0)` writes a plain `<arg>` instead of `from="0"` (FORMAT_NOTES §3.10). ORDERS/ORDRSP builds are logically unchanged. | c051eb8 | Open |
| B2 | New `tools/sim_copy.py` (simulator copies without `xsi:` attributes) | c051eb8 | Open |
| B3 | New `tools/wsdl_inline.py` (self-contained WSDL). v1 lost namespace declarations; fixed and self-checking since 75a7f4d | 7fcc03c, 75a7f4d | Open |
| B4 | New build check `schema_ref_errors` in `tools/cpimm/check.py`, run by `check_build` for every zip | 75a7f4d | Open |
| B5 | Group-aware layout + clean-or-split sharing in `Builder.finish` / `_layout`; build check `layout_overlaps`. In-memory test: all 5 mappings 0 overlaps, logic unchanged (diff) | ORDRSP v1.0.3 commit | Open |
| B6 | New `udf_library/` (README + `substringSafe.groovy`) | ORDRSP v1.0.3 commit | Open |

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

## D. Other actions taken
| # | Action | Status |
|---|---|---|
| D1 | Files moved into the standard layout (schemas/, samples/, docs/) in ORDRSP, DESADV, INVOIC, NShift. Originals unchanged in content | Open |
| D2 | Two NShift XSDs downloaded from `https://service.web-ta.net/ws/services/ConsignmentWS?xsd=1/2` (approved by the user) | Open |
| D3 | ORDRSP input samples re-indented on disk were committed; user chose to keep them | OK |

## E. Import tests reported by the user
- ORDRSP v1.0.2: runs, "some fields missing" (C2).
- ORDRSP v1.0.3: tested by the user; fixes in CPI (E1EDK02 001, attribute contexts) taken over as v1.0.4. Open: E1EDP03 without context, intended?
- DESADV v1.0.0, INVOIC v1.0.0: "everything works" (user, 2026-11-13). No CPI download yet, so no `feedback/` diff.
- NShift v1.0.1: "this works" (user, 2026-11-13). The target structure loads after the WSDL fix.
