# CHANGELOG — Map_RaaheTilkkuHub_TibnorS4_OrderConfirmation_ORDRSP

## 1.0.0 — 2026-11-16 15:58 CET
- First build from `1002257_ORDRSP_Tilkku-to-Tibnor_MappingSpec_v0.1.xlsx`: rows 1–25, 71 target mappings.
- Source `Ordrsp_1_0_0.xsd` (ns0: on every step), target `ORDRSP.ORDERS02.xsd` (ORDERS01). Patterns of the Metocs ORDRSP v1.0.6.
- UDF `substringSafe` (udf_library, unchanged).
- Simulator copies of the input samples added (`_sim.xml` / `_utf8.xml`).
- Checks 1–7 passed (paths, well-formed XML, zip layout, envelope, no forbidden strings, schema references, no overlapping bricks).
- Checked by hand against the expected IDoc.
- Not yet tested in CPI. Open questions are in spec.md.
