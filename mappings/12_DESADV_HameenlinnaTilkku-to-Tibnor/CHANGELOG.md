# CHANGELOG — Map_HammelinnaTilkkuHub_TibnorS4_DeliveryNotice_DESADV

## 1.0.1 — 2026-11-24 15:10 CET
- Segment-level filters (rule of 2026-11-24, user's ORDERS v1.2.0): EDI_DC40 ← createIf(is_mill), sender fields constants; E1ADRM1 ← createIf(is_mill), PARTNER_ID constant. (logic shared with DESADV_RaaheTilkku-to-Tibnor)
- Kept as filtered chains (rule limits): Header values and the grouping chains of E1EDL24.
- Semantic diff: only the targets above changed. All checks passed. Not yet tested in CPI.

## 1.0.0 — 2026-11-16 15:58 CET
- First build from `1000761_DESADV_RaaheTilkku-to-Tibnor_MappingSpec_v0.1.xlsx`: rows 1–27, 56 target mappings.
- Same build logic as the Raahe Tilkku DESADV; groups by heat number, one E1EDL11 per SinglePart (VM-02).
- UDF `getBuyerOrderId` (as Raahe).
- Simulator copies of the input samples added (`_sim.xml` / `_utf8.xml`).
- Checks 1–7 passed (paths, well-formed XML, zip layout, envelope, no forbidden strings, schema references, no overlapping bricks).
- Grouping rules emulated against the 3 expected IDocs: all match.
- Not yet tested in CPI. Open questions are in spec.md.
