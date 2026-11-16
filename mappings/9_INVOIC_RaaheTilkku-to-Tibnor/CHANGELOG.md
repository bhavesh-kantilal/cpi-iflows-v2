# CHANGELOG — Map_RaaheTilkkuHub_TibnorS4_Invoice_INVOIC

## 1.0.0 — 2026-11-16 15:58 CET
- First build from `1002663_INVOIC_Tilkku-to-Tibnor_MappingSpec_v0.1.xlsx`: rows 1–30, 82 target mappings.
- Source `Harmonized_Mill_Invoice_0_0_4_AoC.xsd`, target `INVOIC.INVOIC01.xsd`. Patterns of the Metocs INVOIC v1.0.2.
- Standard functions only, no UDF.
- Simulator copies of the input samples added (`_sim.xml` / `_utf8.xml`).
- Checks 1–7 passed (paths, well-formed XML, zip layout, envelope, no forbidden strings, schema references, no overlapping bricks).
- Checked by hand against the expected IDocs.
- Not yet tested in CPI. Open questions are in spec.md.
