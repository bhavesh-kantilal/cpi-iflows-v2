# CHANGELOG — IXXXX_P_PurchaseOrder_ORDERS_ORDERS02_TibnorS4_IDocToJMS

## 1.0.1 — 2026-11-23 18:05 CET
- `ReceiverDetermination.groovy` streams the body into XmlSlurper with `parse(message.getBody(java.io.Reader))`. Before, it used `parseText(getBody(String))`, which the CPI script editor flags as High.
- RCVPRN: leading zeros are removed only when the value is all digits. A logical system or other alphanumeric value (e.g. `TS4CLNT100`) is compared as is.
- New build check `script_parse_errors`: fails on Groovy that parses XML without streaming.

## 1.0.0 — 2026-11-23 17:45 CET
- First build, cloned from our I2023_P_…_IDocToJMS 1.0.14.
- Receiver determination:
  - RCVPRN 25200 (leading zeros ignored) → queue `I0707_FinMessageHub`, child `IXXXX_PurchaseOrder_ORDERS_ORDERS02_TibnorS4_FinMessageHub_HameenlinnaMetocs_JMSToMQ`
  - no match → Error End
- `SAP_Sender` = `TibnorS4`, `SAP_MessageType` = `ORDERS.ORDERS02`. New property `CH_PurchaseOrder`. `Enviroinment` renamed to `Environment`.
- All build checks passed: check_iflow, layout, participant names, monitoring headers, fixed adapter values.
