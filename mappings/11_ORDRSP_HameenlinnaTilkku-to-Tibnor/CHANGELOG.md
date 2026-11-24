# CHANGELOG — Map_HammelinnaTilkkuHub_TibnorS4_OrderConfirmation_ORDRSP

## 1.0.1 — 2026-11-24 15:10 CET
- Segment-level filters (rule of 2026-11-24, user's ORDERS v1.2.0): EDI_DC40 ← createIf(is_mill), sender fields constants; E1EDK02 (QUALF 001) ← createIf(Reference/@Type [context OrderResponseMessage] = CO), BELNR 1:1. (logic shared with ORDRSP_RaaheTilkku-to-Tibnor)
- Kept as filtered chains (rule limits): E1EDKA1 AG/LF: PARTN is the ZTI PartyId inside the Party (own-value filter), so it stays a chain. Item values as in Metocs ORDRSP.
- Semantic diff: only the targets above changed. All checks passed. Not yet tested in CPI.

## 1.0.0 — 2026-11-16 15:58 CET
- First build from `1002257_ORDRSP_Tilkku-to-Tibnor_MappingSpec_v0.1.xlsx`: rows 1–25, 71 target mappings.
- Same build logic as the Raahe Tilkku ORDRSP, Hämeenlinna Tilkku VM-01 values.
- UDF `substringSafe` (unchanged).
- Simulator copies of the input samples added (`_sim.xml` / `_utf8.xml`).
- Checks 1–7 passed (paths, well-formed XML, zip layout, envelope, no forbidden strings, schema references, no overlapping bricks).
- Checked by hand against the 2 expected IDocs.
- Not yet tested in CPI. Open questions are in spec.md.
