# CHANGELOG — Map_TibnorS4_RaaheTilkkuHub_PurchaseOrder_ORDERS02

## 1.0.0 — 2026-11-16 15:58 CET
- First build from `1002129_ORDERS_Tibnor-to-RaaheTilkku_MappingSpec_v0.1.xlsx`: rows 1–65, 181 target mappings.
- Source `ORDERS.ORDERS02.xsd`, target `Harmonized_Purchase_Order_0_0_7.xsd` (copied from the Metocs ORDERS).
- New UDF `itemCharacteristic` (characteristics joined to the item by POSEX; call-out in spec.md). Reused unchanged: `removezeros`, `TibnorOrdersHelpers` (hasBestText), `substringSafe`.
- Simulator copies of the input samples added (`_sim.xml` / `_utf8.xml`).
- Checks 1–7 passed (paths, well-formed XML, zip layout, envelope, no forbidden strings, schema references, no overlapping bricks).
- Rules emulated in Python against the 5 expected outputs: values match; Property 8 order differs for 6 items (open question Q1).
- Not yet tested in CPI. Open questions are in spec.md.
