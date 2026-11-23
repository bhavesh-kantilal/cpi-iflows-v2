# CHANGELOG — I2050_P_MaintenanceBOM_MSAP_AMQPToJMS

## 1.0.6 — 2026-11-23 10:45 CET
Built from Bhavesh's CPI version 1.0.5 (`source/I2050_P_MaintenanceBOM_MSAP_AMQPToJMS.zip`).
- The misspelt parameter `S4_DeleteIdleConnnectopn` is renamed to `S4_DeleteIdleConnection` (iflw, prop, propdef). Set its value on the tenant again (default true).

## 1.0.5 — 2026-11-23 (Bhavesh, in CPI)
- OData Lookup MaintenanceBOM: Delete Idle Connection → `{{S4_DeleteIdleConnnectopn}}` (true) and Idle Timeout → `{{S4_IdleTimeout}}` (300) are externalized.
- `S4_CSRFProtected=false`: the call is a GET, so no CSRF token is needed.
- metainfo `source=MSAP`.

## 1.0.4 — 2026-11-23 10:10 CET
Built from Bhavesh's export 1.0.3 (package MSAPPlantMaintenanceMasterData).
- Receiver determination now names the renamed child `I2050_MaintenanceBOM_MSAP_SmarTeam_JMSToHTTP`. Deploy it together with child 1.0.4.
- Typos fixed: attachment names `MaintenanceBOM_Event.json` and `MaintenanceBOMXML`, step "Initial Properties".
- Removed 18 unused parameters (`HTTP_Address` was a copy from I2049_P; the `S4_*` set and the spaced `Address`/`Authorization`/… copies were unused).
- Renamed 8 parameters with spaces to `S4_*` / `HTTPS_BodySize` (e.g. `S4 Address` → `S4_Address`, `proxy Type` → `S4_ProxyType`). The defaults are unchanged, but values configured on the tenant must be set again.
- The iflw file is renamed to `I2050_P_MaintenanceBOM_MSAP_AMQPToJMS.iflw`.
