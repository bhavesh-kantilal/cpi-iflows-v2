# CHANGELOG — Map_HammelinnaMetocsHub_TibnorS4_OrderConfirmation_ORDRSP

## 1.0.5 — 2026-11-15 11:36 CET
- `E1EDP03` now uses the same Item-context Date chain as DATUM/EDATU (user: keep segment and fields consistent). Before, the segment count was right only because every item has exactly one format-718 date; the values were paired with the wrong Dates.
- Logically identical to the user's CPI download except E1EDP03 (as in the user's screenshot after the change). All checks passed.

## 1.0.4 — 2026-11-15 11:29 CET
Takes over the user's CPI fixes (`feedback/feedback_v2.docx`, CPI download `feedback/Map_…_ORDRSP (1).zip`; logically identical to the download):
- `E1EDK02` (QUALF 001) was missing: it now comes from `SplitByValue(removeContexts(ifWithoutElse(@Type = CO, RefNo)))` instead of `createIf` without `removeContexts`. `E1EDK02/BELNR` and `E1EDK01/BELNR` use the same chain.
- `Date/@Type`, `Date/@Format` (DATUM, EDATU) and `AddArticleNo/@Type` (E1EDP19, IDTNR): context = Item, so each attribute lines up with its element's value.
- `E1EDP03` taken over exactly as downloaded (attributes without context). Asked whether that is intended.
- Expected output sample re-indented by the user (content unchanged).
- All checks passed. The self-test passes.

## 1.0.3 — 2026-11-15 10:49 CET
Applies the user's feedback document `feedback/Feedback.docx`:
- `E1EDP03`, `DATUM`, `EDATU` ← the format-718 Date chain (no `createIf`, which suppressed other items' segments). DATUM/EDATU = end of range via the new UDF `substringSafe(value, '9', '17')` (from `udf_library/`), so `20261220` again.
- `E1EDP19` ← the IN-article chain (no `createIf`).
- `MENEE` ← `FixValues` M → MTR with "Use Key" (`vmstrategy 2`) instead of `iF`.
- `E1EDP02/BELNR` ← `CopyValue(PO number, 0)` instead of `useOneAsMany`.
- Layout: no overlapping bricks; shared logic only where it can be drawn cleanly (toolkit change, new overlap check).
- All checks passed. The self-test passes. Not yet tested in CPI. CopyValue on a queue with suppressed values is to be checked.

## 1.0.2 — 2026-11-13 06:05 CET
Applies the user's CPI download of v1.0.1 (`feedback/`, compared with `tools/cpimm/diff.py`, 2 differences, both taken over):
- **Source XSD link:** a 4th `<elem>` with the targetNamespace `http://www.ruukki.com/schemas/eai/internal/production/eruukki`. Without it, CPI did not load the source XSD on import ("Add source message").
- `E1EDP03/DATUM` and `E1EDP20/EDATU`: direct mapping of the format-718 date, without `substring` (user's temporary fix). **Known wrong:** the value is the full range `YYYYMMDD-YYYYMMDD` (17 characters) instead of the end date (spec rows 18, 20). Open, see spec.md.
- The build is now logically identical to the CPI version (diff: no differences). All checks passed. The self-test passes.
- Still open from the user's test: "some fields missing", to be checked by the user.

## 1.0.1 — 2026-11-13 05:57 CET
Fixes from the user's import test and their existing PO mapping of the same source (spec.md):
- One mapping under the plain name, with `ns0:` on every source element step (the NsAllSteps variant worked). The two variant zips are removed.
- No context settings on source fields any more. In v1.0.0, `mapWithDefault` after a context change made the queues drift apart, so no E1EDP01 was created.
- `E1EDP01` ← `removeContexts(ifWithoutElse(and(Property/@Type = 12, not(PropertyText = ITEM CANCELLED)), const ""))`, as PO G_SG26.
- Item values (MENGE, MENEE, WMENG, DATUM, EDATU, IDTNR) use the PO chain: `ifWithoutElse` filter → `removeContexts` → `SplitByValue(Each Value)`.
- `E1EDK03`, `E1EDK02`, `E1EDP03` and `E1EDP19` ← `createIf(qualifier condition)`.
- `E1EDP02/BELNR`: `useOneAsMany` takes `removeContexts(LineNo)` instead of a context setting.
- All checks passed. The self-test still passes. Not yet run in CPI.

## 1.0.0 — 2026-11-13 05:06 CET
- First build from `25207_ORDRSP_HameenlinnaMetocs-to-Tibnor_MappingSpec_v0.1.xlsx`: rows 1–21, as 58 target mappings.
- Source `Ordrsp_1_0_0.xsd` (OrdrspInterchange, namespace eruukki). Target `ORDRSP.ORDERS02.xsd` (ORDERS01 IDoc).
- Standard functions only, no UDFs.
- Built as **two test variants**, which differ only in the source path prefixes (spec.md, Q2):
  - `…_ORDRSP_NsAllSteps.zip`: `ns0:` on every source element step
  - `…_ORDRSP_NsRootOnly.zip`: `ns0:` on the source root only
- Checks passed for both:
  - every source and target path exists in the XSDs
  - all mandatory IDoc fields are mapped
  - all XML is well-formed
  - the zip layout matches the standalone references
  - no forbidden strings
- The self-test passes.
- Not yet tested in CPI. Open for the import test: which namespace variant works, and the item filter for skipped items (no sample has one).
