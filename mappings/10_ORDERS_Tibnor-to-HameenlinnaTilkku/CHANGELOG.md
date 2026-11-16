# CHANGELOG — Map_TibnorS4_HammelinnaTilkkuHub_PurchaseOrder_ORDERS02

## 1.0.0 — 2026-11-16 15:58 CET
- First build from `1002249_ORDERS_Tibnor-to-HameenlinnaTilkku_MappingSpec_v0.1.xlsx`: rows 1–65 without ZMA, 176 target mappings.
- Same build logic as the Raahe Tilkku ORDERS (`mappings/6_…/build_mapping.py`), Hämeenlinna Tilkku VM-01 values.
- UDFs as the Raahe mapping.
- Simulator copies of the input samples added (`_sim.xml` / `_utf8.xml`).
- Checks 1–7 passed (paths, well-formed XML, zip layout, envelope, no forbidden strings, schema references, no overlapping bricks).
- Rules emulated against the 5 expected outputs: values match; Measurement order differs for one item.
- Not yet tested in CPI. Open questions are in spec.md.
