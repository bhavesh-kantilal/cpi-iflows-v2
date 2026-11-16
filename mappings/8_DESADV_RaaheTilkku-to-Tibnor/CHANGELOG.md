# CHANGELOG — Map_RaaheTilkkuHub_TibnorS4_DeliveryNotice_DESADV

## 1.0.0 — 2026-11-16 15:58 CET
- First build from `1000761_DESADV_RaaheTilkku-to-Tibnor_MappingSpec_v0.1.xlsx`: rows 1–27, 56 target mappings.
- Source `DeliveryBatch_0_8_1.xsd` (samples are 0.8.4; user decision), target `DESADV.DELVRY01.xsd`. Grouping by line + first 8 characters of SinglePartId with standard functions (SplitByValue value change, no sort).
- New UDF `getBuyerOrderId` (port of the PO UDF; call-out in spec.md).
- Simulator copies of the input samples added (`_sim.xml` / `_utf8.xml`).
- Checks 1–7 passed (paths, well-formed XML, zip layout, envelope, no forbidden strings, schema references, no overlapping bricks).
- Grouping rules emulated against the 4 expected IDocs: all match.
- Not yet tested in CPI. Open questions are in spec.md.
