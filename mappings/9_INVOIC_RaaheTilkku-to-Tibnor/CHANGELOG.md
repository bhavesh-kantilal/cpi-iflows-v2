# CHANGELOG — Map_RaaheTilkkuHub_TibnorS4_Invoice_INVOIC

## 1.0.3 — 2026-11-24 20:30 CET
- EDI_DC40, E1EDKA1 (LF) and E1EDKA1[1] (RE) ← empty constant; the mill check `InterchangeSender = <mill GLN>` is removed, because the parent iFlow already routes by mill. `E1EDK04/MWSKZ ← Tax/@Type` 1:1: `removeContexts` → `SplitByValue` removed (the attribute already has one context per Tax).
- Only these targets changed (semantic diff). All build checks passed.

## 1.0.2 — 2026-11-24 16:40 CET
- Segment-level filters (user 2026-11-24, Q2 a+b): E1EDK04 ← createIf(Tax/MonetaryAmount/@Type [context Invoice] = 176), MWSBT 1:1; E1EDP26 ← createIf(Item/MonetaryAmount/@Type [context Item] = 38), BETRG 1:1. No segment when the amount type is missing (before: always).
- All checks passed. Semantic diff: only these 4 targets changed. Not tested in CPI.

## 1.0.1 — 2026-11-24 15:10 CET
- Segment-level filters (rule of 2026-11-24, user's ORDERS v1.2.0): EDI_DC40 ← createIf(is_mill), sender fields constants; E1EDKA1 (LF) and E1EDKA1[1] (RE) ← createIf(is_mill), PARTN constant.
- Kept as filtered chains (rule limits): E1EDK01 (is_380 with CURCY), E1EDK05 (sum condition), item qualified values, header values.
- Semantic diff: only the targets above changed. All checks passed. Not yet tested in CPI.

## 1.0.0 — 2026-11-16 15:58 CET
- First build from `1002663_INVOIC_Tilkku-to-Tibnor_MappingSpec_v0.1.xlsx`: rows 1–30, 82 target mappings.
- Source `Harmonized_Mill_Invoice_0_0_4_AoC.xsd`, target `INVOIC.INVOIC01.xsd`. Patterns of the Metocs INVOIC v1.0.2.
- Standard functions only, no UDF.
- Simulator copies of the input samples added (`_sim.xml` / `_utf8.xml`).
- Checks 1–7 passed (paths, well-formed XML, zip layout, envelope, no forbidden strings, schema references, no overlapping bricks).
- Checked by hand against the expected IDocs.
- Not yet tested in CPI. Open questions are in spec.md.
