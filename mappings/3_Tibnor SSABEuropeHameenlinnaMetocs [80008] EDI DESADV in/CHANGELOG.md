# CHANGELOG — Map_HammelinnaMetocsHub_TibnorS4_DeliveryNotice_DESADV

## 1.0.2 — 2026-11-24 15:10 CET
- Segment-level filters (rule of 2026-11-24, user's ORDERS v1.2.0): EDI_DC40 ← createIf(is_metocs), sender fields constants; E1ADRM1 ← createIf(is_metocs), PARTNER_ID constant.
- Kept as filtered chains (rule limits): PO number / cargo id header values (used in several segments), the groupByHeat UDF chain for E1EDL24.
- Semantic diff: only the targets above changed. All checks passed. Not yet tested in CPI.

## 1.0.1 — 2026-11-15 11:43 CET
- Applies the rules accepted in the review of 2026-11-15:
  - Header values on every delivery item (ARKTX, E1EDL43 BELNR/DATUM, E1EDL41 BSTNR/BSTDT, ABRDT) use `CopyValue(value, 0)` instead of `useOneAsMany`.
  - New editor layout (no overlaps).
- The output should be unchanged. Re-test in CPI recommended.

## 1.0.0 — 2026-11-13 06:47 CET
- First build from `25208_DESADV_HameenlinnaMetocs-to-Tibnor_MappingSpec_v0.1.xlsx`: rows 1–27, as 58 target mappings.
- Source `DeliveryBatch_0_8_1.xsd` (namespace otc: `ns0:` on every step, namespace as the 4th link elem). Target `DESADV.DELVRY01.xsd` (DELVRY01).
- E1EDL24 per line + heat via the new multi-output UDF `groupByHeat.groovy`. Everything else uses standard functions and the user's PO filter pattern.
- Simulator copies `Samples/*/Input_*_sim.xml` added.
- Checks passed: paths, well-formed XML, zip layout, UDF script present, no forbidden strings. The self-test passes.
- The rules were checked in Python against the 5 expected IDocs: 11 of 11 items match. The Groovy UDF has not run yet.
- Not yet tested in CPI. Assumptions A1–A8 are in spec.md.
