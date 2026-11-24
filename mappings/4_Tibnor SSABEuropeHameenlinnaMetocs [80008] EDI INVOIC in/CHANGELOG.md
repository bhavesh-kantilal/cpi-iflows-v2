# CHANGELOG — Map_HammelinnaMetocsHub_TibnorS4_Invoice_INVOIC

## 1.0.4 — 2026-11-24 16:20 CET
- Segment-level filters (user 2026-11-24, Q2):
  - `E1EDK04` ← createIf(Tax/MonetaryAmount/@Type [context Invoice] = 176); MWSBT ← Tax/MonetaryAmount/MonetaryValue 1:1 (a Tax has exactly one MonetaryAmount). A Tax without a 176 amount gives no E1EDK04 (before: one per Tax).
  - `E1EDP01/E1EDP26` ← createIf(Item/MonetaryAmount/@Type [context Item] = 38); BETRG ← MonetaryValue 1:1. An item without a type-38 amount gives no E1EDP26 (before: always, empty BETRG).
- All checks passed. Semantic diff: only these 4 targets changed. Not tested in CPI.

## 1.0.3 — 2026-11-24 15:10 CET
- Segment-level filters (rule of 2026-11-24, user's ORDERS v1.2.0): EDI_DC40 ← createIf(is_metocs), sender fields constants; E1EDKA1 (LF) and E1EDKA1[1] (RE) ← createIf(is_metocs), PARTN constant.
- Kept as filtered chains (rule limits): E1EDK01 BSART/FKART_RL/FKTYP (is_380: the segment also carries CURCY), E1EDK04 MWSBT, E1EDP26 BETRG, E1EDP19 IDTNR and the item Quantity values (qualified values inside an item / tax line), header values (currency, date, PO number).
- Semantic diff: only the targets above changed. All checks passed. Not yet tested in CPI.

## 1.0.2 — 2026-11-15 13:38 CET
- Rule R4 (CLAUDE.md): no `mapWithDefault` after a context change when the new context can hold several occurrences. `AddArticleNo/@Type` [context Item] (IDTNR) now goes into the filter directly. An item can carry several AddArticleNo (UA, MF, HS), and `mapWithDefault` doesn't fill gaps after a context change.
- The same function also builds `DocumentId/Date/@Type` [context DocumentId] (E1EDK03/DATUM, E1EDP03/DATUM) without `mapWithDefault`. There is one Date per DocumentId, so the result is the same.
- All checks passed. Re-test in CPI recommended (IDTNR, dates).

## 1.0.1 — 2026-11-15 11:43 CET
- Applies the rules accepted in the review of 2026-11-15:
  - PO number and invoice date on every item (E1EDP02/BELNR, E1EDP03/DATUM) use `CopyValue(value, 0)` instead of `useOneAsMany`.
  - Attribute context: `AddArticleNo/@Type` (IDTNR) gets context Item, and `DocumentId/Date/@Type` (header DATUM) gets context DocumentId, because each is compared with its own element's value.
  - New editor layout (no overlaps).
- The output should be unchanged for the samples. Re-test in CPI recommended.

## 1.0.0 — 2026-11-13 06:47 CET
- First build from `25224_INVOIC_HameenlinnaMetocs-to-Tibnor_MappingSpec_v0.1.xlsx`: rows 1–29, as 77 target mappings.
- Source `Harmonized_Mill_Invoice_0_0_4_AoC.xsd` (Invoice, no namespace). Target `INVOIC.INVOIC01.xsd` (INVOIC01).
- Standard functions only, using the user's PO filter pattern and the ORDRSP conventions. No UDF.
- Simulator copies `samples/*/Input_*_sim.xml` added.
- Checks passed: paths, well-formed XML, zip layout, no forbidden strings. The self-test passes.
- The rules were checked in Python against the 5 expected IDocs. Everything matches except ZEILE for METOCSTO (assumption A1).
- Not yet tested in CPI. Assumptions A1–A7 are in spec.md.
