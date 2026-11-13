# CHANGELOG — Map_TibnorS4_HammelinnaMetocsHub_PurchaseOrder_ORDERS02

## 1.1.0 — 2026-11-13
Applies the user's feedback and CPI edits (`feedback/` export, compared with `tools/cpimm/diff.py`):
- `Item/LineNo`: `formatNumber(POSEX, '#', '.')` instead of the `removezeros` UDF (numeric source).
- `NumberOfLineItems`: standard `count(POSEX)` instead of the `countValues` UDF, which is removed from `TibnorOrdersHelpers.groovy`.
- `Item/Quantity`, `Item/Price`: container ← empty constant.
- `Contact`, `TermsOfDelivery`, `Location`, `Item/Property`: container ← `createIf(condition)` instead of a source value.
- **Not taken over:** the CPI edit `Reference`/`Reference[1]`/`Reference[2]` ← empty constant. Reference is a simple-content element whose text is the value, so the edit would drop BELNR, 'S' and 'TPO' (spec rows 10–12, expected sample output). Waiting for the user to confirm.
- All checks passed. The self-test still passes.

## 1.0.0 — 2026-11-13
- First build from `25200_ORDERS_Tibnor-to-HameenlinnaMetocs_MappingSpec_v0.1.xlsx`: all 52 rows, as 87 target mappings.
- Source `ORDERS.ORDERS02.xsd` (ORDERS02). Target `Harmonized_Purchase_Order_0_0_7.xsd` (OrdersMessage).
- UDFs: `removezeros.groovy` (from reference CostCentertoMedius) and the new `TibnorOrdersHelpers.groovy` (`cropText`, `hasBestText`, `countValues`).
- Checks passed:
  - every source and target path exists in the XSDs
  - no mandatory target element is left unmapped
  - all XML is well-formed
  - the zip layout matches the standalone references
  - no forbidden strings
- Not yet tested in CPI. Open for the import test: the FixValues "use default value" numbering, `formatNumber` pattern `0.###`, and the placeholder property `HubEnvironment`.
