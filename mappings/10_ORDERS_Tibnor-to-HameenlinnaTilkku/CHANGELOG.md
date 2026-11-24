# CHANGELOG — Map_TibnorS4_HammelinnaTilkkuHub_PurchaseOrder_ORDERS02

## 1.0.1 — 2026-11-24 15:10 CET
- Segment-level filters (rule of 2026-11-24, user's ORDERS v1.2.0): Party BY/MF/CN ← createIf(E1EDKA1/PARVW [context IDOC] = AG/LF/WE), fields 1:1 from that E1EDKA1; TermsOfDelivery ← createIf(E1EDK17/QUALF [context IDOC] = 001), LKOND/LKTEXT 1:1. Change: a Party is now created only when its partner segment exists (before: always); TermsOfDelivery for every QUALF 001 segment (before: only when LKOND had a value). (logic shared with ORDERS_Tibnor-to-RaaheTilkku)
- Kept as filtered chains (rule limits): Header InterchangeSender/Recipient/MessageRoutingOutbound (header fields from the AG/LF partner), the ship-to copied onto every item (CopyValue of header values), DocumentId/Date (E1EDK03 IDDAT 012), the item characteristics (itemCharacteristic UDF) and ArticleNo.
- Semantic diff: only the targets above changed. All checks passed. Not yet tested in CPI.

## 1.0.0 — 2026-11-16 15:58 CET
- First build from `1002249_ORDERS_Tibnor-to-HameenlinnaTilkku_MappingSpec_v0.1.xlsx`: rows 1–65 without ZMA, 176 target mappings.
- Same build logic as the Raahe Tilkku ORDERS (`mappings/6_…/build_mapping.py`), Hämeenlinna Tilkku VM-01 values.
- UDFs as the Raahe mapping.
- Simulator copies of the input samples added (`_sim.xml` / `_utf8.xml`).
- Checks 1–7 passed (paths, well-formed XML, zip layout, envelope, no forbidden strings, schema references, no overlapping bricks).
- Rules emulated against the 5 expected outputs: values match; Measurement order differs for one item.
- Not yet tested in CPI. Open questions are in spec.md.
