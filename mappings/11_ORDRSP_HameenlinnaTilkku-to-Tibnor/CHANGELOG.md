# CHANGELOG — Map_HammelinnaTilkkuHub_TibnorS4_OrderConfirmation_ORDRSP

## 1.0.0 — 2026-11-16 15:58 CET
- First build from `1002257_ORDRSP_Tilkku-to-Tibnor_MappingSpec_v0.1.xlsx`: rows 1–25, 71 target mappings.
- Same build logic as the Raahe Tilkku ORDRSP, Hämeenlinna Tilkku VM-01 values.
- UDF `substringSafe` (unchanged).
- Simulator copies of the input samples added (`_sim.xml` / `_utf8.xml`).
- Checks 1–7 passed (paths, well-formed XML, zip layout, envelope, no forbidden strings, schema references, no overlapping bricks).
- Checked by hand against the 2 expected IDocs.
- Not yet tested in CPI. Open questions are in spec.md.
