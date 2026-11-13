# CHANGELOG — Map_TibnorS4_HammelinnaMetocsHub_PurchaseOrder_ORDERS02

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
