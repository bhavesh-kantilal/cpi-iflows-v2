# I2050_P_MaintenanceBOM_MSAP_AMQPToJMS

Parent iFlow of the SSAB Simplified Pipeline (CPI package MSAPPlantMaintenanceMasterData; the build lives in `iflows/SmarTeam/` next to its child).
- **Input:** an Event Mesh event over AMQP, queue `ssab/msap/ad1/I2050/MaintenanceBOM`.
- **Lookup:** it reads the maintenance BOM from MSAP (OData `API_BILL_OF_MATERIAL_SRV`) and filters on BOM usage.
- **Receiver determination:** `ReceiverDetermination.groovy` sets queue `I0700_SmarTeam` and receiver iFlow `I2050_MaintenanceBOM_MSAP_SmarTeam_JMSToHTTP`.
- **Output:** it sends the message to JMS. The SmarTeam dispatcher then calls the child over ProcessDirect.

- Source: `iflows/SmarTeam/source/MSAPPlantMaintenanceMasterData_artifacts (1).zip` → folder `I2050_P_MaintenanceBOM_MSAP_AMQPToJMS` (Bhavesh's export, v1.0.3, 2026-11-23)
- Build: `py -I tools/iflow_build_smarteam.py --only I2050_P_MaintenanceBOM_MSAP_AMQPToJMS` (`build_i2050_parent`)
- Child: `iflows/SmarTeam/I2050_MaintenanceBOM_MSAP_SmarTeam_JMSToHTTP/`

## Decisions
| Date | Question | Answer | Impact |
|---|---|---|---|
| 2026-11-23 | Receiver iFlow name after the child rename (L2, user) | The new child name | `ReceiverDetermination.groovy`: `I2050_MaintananceBOM_MSAP_SmarTeam_PDToHTTP` → `I2050_MaintenanceBOM_MSAP_SmarTeam_JMSToHTTP`. **Deploy parent and child together.** Messages already on `I0700_SmarTeam` still carry the old name |
| 2026-11-23 | Typos (L2, user: fix them) | Fix | AttachmentName `MaintananceBOM_Event.json` → `MaintenanceBOM_Event.json`, `MaintananceBOMXML` → `MaintenanceBOMXML`, step "Intial Properties" → "Initial Properties". The unused parameter `Contition` is removed |
| 2026-11-23 | Remove unused parameters (L2, user) | Yes | Removed 18: `Address`, `Authorization`, `CSRF Protected`, `CSRF_Protected`, `Contition`, `Credential Name`, `Custom Query Options`, `HTTP_Address` (was `/I2049_P_…`, copy leftover), `Location ID`, `Reuse Connection`, `S4`, `S4_Address`, `S4_Authentication`, `S4_CSRF`, `S4_Credential`, `S4_LocationID`, `S4_Proxy`, `UserRole` |
| 2026-11-23 | iflw file name `I0040_P_EDI_DESADV_B30_AMQPToJMS.iflw` (copy leftover) (L2, user) | File name = iFlow name | `I2050_P_MaintenanceBOM_MSAP_AMQPToJMS.iflw` |

| 2026-11-23 | Rename the parameters with spaces? (L2, user: yes) | `<System>_<Setting>` | `S4 Address` → `S4_Address`, `S4 Authentication` → `S4_Authentication`, `S4 Credential Name` → `S4_CredentialName`, `S4 Location ID` → `S4_LocationID`, `S4 CSRF Protected` → `S4_CSRFProtected`, `S4 Reuse Connection` → `S4_ReuseConnection`, `proxy Type` → `S4_ProxyType` (OData receiver); `Body Size` → `HTTPS_BodySize` (HTTPS retrigger sender, the same name as in the child). Default values are unchanged. **Configured values on the tenant under the old names are not carried over:** check them after import |

| 2026-11-23 | Bhavesh's CPI changes in 1.0.5 (L2) | Taken over into the build | Externalized `clearStaleConnection` → `S4_DeleteIdleConnection` (true) and `maxIdleTimeout` → `S4_IdleTimeout` (300). **CSRF off for OData GET calls** (`S4_CSRFProtected=false`): a GET needs no CSRF token. metainfo `source=MSAP` |
| 2026-11-23 | `S4_DeleteIdleConnnectopn` is misspelt | Fixed in 1.0.6 (CLAUDE.md: fix misspelt parameter names) | `S4_DeleteIdleConnection`. **Set its tenant value again** |

| 2026-11-23 | LogPayloadSize missing? (L2, user: "always defaulted to 512 for 512 kb, externalized") | It was never externalized (empty constant in 1.0.3 and 1.0.5), not dropped by a build | 1.0.7: property row = `{{LogPayloadSize}}`, parameter `LogPayloadSize=512`. New build check: no empty LogPayload / LogPayloadSize row. I2049_P has the same gap (its own round) |

## Build input
From 1.0.6 on, the build starts from Bhavesh's CPI version 1.0.5 (`source/I2050_P_MaintenanceBOM_MSAP_AMQPToJMS.zip`). The 1.0.4 changes are already in it.
