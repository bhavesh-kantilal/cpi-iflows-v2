# CHANGELOG — IXXXX_PurchaseOrder_ORDERS_ORDERS02_TibnorS4_FinMessageHub_HameenlinnaMetocs_JMSToMQ

## 1.0.1 — 2026-11-24 15:20 CET
- Mapping `Map_TibnorS4_HammelinnaMetocsHub_PurchaseOrder_ORDERS02` v1.2.0: the user's simplified Party logic (segment-level filters), plus CN street, Contact and TermsOfDelivery in the same style.

## 1.0.0 — 2026-11-23 17:45 CET
- First build:
  - flow shape from our I2018 SmarTeam child 1.1.5
  - IBM MQ receiver from I2034 1.0.10, unchanged: 17 `IBMMQ_*` parameters, plus 3 settings newly externalized
- Mapping `Map_TibnorS4_HammelinnaMetocsHub_PurchaseOrder_ORDERS02` v1.1.1, with its UDFs and XSDs.
- New property `HubEnvironment` = `{{HubEnvironment}}` (default TST), IDoc monitoring keys, response steps removed.
- All build checks passed: check_iflow, layout, participant names, monitoring headers, fixed adapter values.
