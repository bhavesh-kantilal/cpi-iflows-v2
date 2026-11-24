# CHANGELOG — Map_RaaheTilkkuHub_TibnorS4_OrderConfirmation_ORDRSP

## 1.0.2 — 2026-11-24 16:40 CET
- Segment-level filters (user 2026-11-24, Q1): E1EDKA1 (AG) ← createIf(Party/@Role [context OrderResponseMessage] = BY), E1EDKA1[2] (LF) ← createIf(… = SE); PARTN ← ifWithoutElse(PartyId/@Type [context Party] = ZTI, PartyId) within that Party (useOneAsMany removed). No E1EDKA1 AG/LF when the Party is missing (before: always, possibly empty).
- All checks passed. Semantic diff: only these 4 targets changed. Not tested in CPI.

## 1.0.1 — 2026-11-24 15:10 CET
- Segment-level filters (rule of 2026-11-24, user's ORDERS v1.2.0): EDI_DC40 ← createIf(is_mill), sender fields constants; E1EDK02 (QUALF 001) ← createIf(Reference/@Type [context OrderResponseMessage] = CO), BELNR 1:1.
- Kept as filtered chains (rule limits): E1EDKA1 AG/LF: PARTN is the ZTI PartyId inside the Party (own-value filter), so it stays a chain. Item values as in Metocs ORDRSP.
- Semantic diff: only the targets above changed. All checks passed. Not yet tested in CPI.

## 1.0.0 — 2026-11-16 15:58 CET
- First build from `1002257_ORDRSP_Tilkku-to-Tibnor_MappingSpec_v0.1.xlsx`: rows 1–25, 71 target mappings.
- Source `Ordrsp_1_0_0.xsd` (ns0: on every step), target `ORDRSP.ORDERS02.xsd` (ORDERS01). Patterns of the Metocs ORDRSP v1.0.6.
- UDF `substringSafe` (udf_library, unchanged).
- Simulator copies of the input samples added (`_sim.xml` / `_utf8.xml`).
- Checks 1–7 passed (paths, well-formed XML, zip layout, envelope, no forbidden strings, schema references, no overlapping bricks).
- Checked by hand against the expected IDoc.
- Not yet tested in CPI. Open questions are in spec.md.
