# I2050_MaintenanceBOM_MSAP_SmarTeam_JMSToHTTP

Child iFlow of the SSAB Simplified Pipeline / JMS dispatcher pattern (CPI package SmarTeam). The parent `I2050_P_MaintenanceBOM_MSAP_AMQPToJMS` (package MSAPPlantMaintenanceMasterData) puts the message on queue `I0700_SmarTeam`. The dispatcher then calls this flow over ProcessDirect `/I2050_MaintenanceBOM_MSAP_SmarTeam_JMSToHTTP`. The flow maps the maintenance BOM (`MaintBOM_Mapping`), POSTs it to SmarTeam and logs the response.

Before v1.0.4 the flow was named `I2050_MaintananceBOM_MSAP_SmarTeam_PDToHTTP`. Its history is in `iflows/SmarTeam/I2050_MaintananceBOM_MSAP_SmarTeam_PDToHTTP/`.

- Source: `iflows/SmarTeam/source/I2050_MaintananceBOM_MSAP_SmarTeam_PDToHTTP.jar` (Bhavesh's export, v1.0.3, 2026-11-23)
- Build: `py -I tools/iflow_build_smarteam.py --only I2050_MaintenanceBOM_MSAP_SmarTeam_JMSToHTTP` (`build_i2050_child`)
- Shared helpers: `tools/iflow_lib.py`

## Flow (Main Process)
Start → Set Monitoring Identifiers (CH_BillOfMaterial, CH_BillOfMaterialCategory, CH_BillOfMaterialVariant, CH_Plant, CH_TechnicalObject) → Log Payload → Set Custom Header → MSAP_SmartTeam (mapping) → Set AttachmentName (OutputPayload) → Log Payload → Send to SmarTeam (HTTP) → Set AttachmentName (SmartTeamResponse + **CH_SmarTeamWorkId**) → **Set Custom Header** → Log Payload → End

SmarTeam response (L2, user 2026-11-23):
```xml
<InboundResponse>
  <Accepted>true</Accepted>
  <Message>Message accepted and stored.</Message>
  <WorkId>1514739</WorkId>
</InboundResponse>
```

## Parameters (v1.0.4)
| Parameter | Used in | Value |
|---|---|---|
| AllowedHeaders | runtime allowed headers | `SSAB.*\|SAP.*` (since 1.0.6) |
| HTTPS_Authorization / HTTPS_UserRole / HTTPS_CSRFProtected / HTTPS_BodySize | Manual Retrigger HTTPS sender | RoleBased / SSAB_MessagingSend_InternalOperations / 0 / 40 |
| HTTP_Session_Reuse | HTTP session | onIntegrationFlow |
| LogPayload / LogPayloadSize | Log Payload | true / 512 |
| SAP_Sender / SAP_Receiver / SAP_MessageType | monitoring headers | MSAP / SmarTeam / MaintenanceBOM |

## Decisions
| Date | Question | Answer | Impact |
|---|---|---|---|
| 2026-11-23 | "Integration Process from Source" ended in "Error End 1" (L2, user: change it to a success end) | Message End | `EndEvent_734103` gets a Message End (`MessageEndEvent/version::1.1.0`), the structure of the I2018 export `EndEvent_734105`. The name is now "End" |
| 2026-11-23 | Log the SmarTeam WorkId (L2, user) | Custom header `SmarTeamWorkId`, using the normal CH_ pattern | Row `CH_SmarTeamWorkId` (xpath `/InboundResponse/WorkId` since 1.0.5, java.lang.String) in Content Modifier "Set AttachmentName" after Send to SmarTeam. Then a new Script step "Set Custom Header" (`UTIL_LogCustomHeaders` / `logCustomHeaders.groovy`, a copy of the existing step) |
| 2026-11-23 | Log the earlier CH_ properties a second time? | **Lesson (L2, user):** CPI does not duplicate a custom header value that is already logged. A changed value is added as a new line, and the old one stays | The earlier CH_ properties stay as they are. No Delete rows |
| 2026-11-23 | Typo `Maintanance` (L2, user) | Fix it, and use the new naming: children are `…_JMSToHTTP` even though they start with ProcessDirect. The PD address = `/<child name>` | New iFlow ID `I2050_MaintenanceBOM_MSAP_SmarTeam_JMSToHTTP`, used in the MANIFEST, `.project`, the PD address and the HTTPS retrigger path. `SAP_MessageType=MaintenanceBOM`. **CPI imports this as a new artifact:** undeploy the old one once the parent points to the new name |
| 2026-11-23 | Remove unused parameters (L2, user) | Yes | Removed the 7 `JMSReceiver_*`, the 7 `JMSSender_*`, `MaxRetries` and `SAP_Message_name`. `JMSSender_QueueName` was `I2018_SmarTeam` (copy leftover) |
| 2026-11-23 | iflw file name `I0579_CostCentreGroupHierarchyReplication_FSAP_MSAP_JMSToSOAP.iflw` (copy leftover) (L2, user: fix it) | File name = iFlow name | `I2050_MaintenanceBOM_MSAP_SmarTeam_JMSToHTTP.iflw` (I0539 build precedent) |
| 2026-11-23 | Input is a runtime `.jar`, not a design-time zip | Convert it in the build | The build keeps `src/main/resources/**`, writes a design-time MANIFEST, and adds `.project` + `metainfo.prop`. The rule comes from the I2049 jar/zip pair of the same version (L2). `--selftest` proves it byte for byte |

| 2026-11-23 | Set Monitoring Identifiers XPaths wrong (L2, user, with sample `BOMHeader/MaintBOMHeader_Type`) | Fix them; **no `local-name()`** unless asked or logically needed (the source has no namespace) | v1.0.5: `/BOMHeader/MaintBOMHeader_Type/<field>` for CH_BillOfMaterial, CH_BillOfMaterialCategory, CH_BillOfMaterialVariant (now really BillOfMaterialVariant), CH_Plant, CH_TechnicalObject, SAP_ApplicationID. Checked against `MaintBOMInput.xsd`. WorkId: `/InboundResponse/WorkId` |

| 2026-11-23 | Allowed Headers (L2, user: for this and all child iFlows) | Externalized `AllowedHeaders` = `SSAB.*\|SAP.*` | 1.0.6: default changed from `SSAB.*`. The build script sets it for every child and fails if Allowed Headers is not `{{AllowedHeaders}}` |
| 2026-11-23 | Step name of the logCustomHeaders.groovy step (L2, user, screenshot: "LogCustomHeaders" for all iFlows) | `LogCustomHeaders` | 1.0.7: renamed from 'Set Custom Header' (2 steps). The build names every such step this way and fails on any other name |
| 2026-11-23 | SmarTeam adapter not externalized (L2, user: "we always externalize adapters"; rule already in CLAUDE.md, missed in the first round) | Externalize every setting of the SmarTeam HTTP receiver | 1.0.8: 12 `SmarTeam_*` parameters, defaults = old fixed values, propdef references like the I0539 Medius receiver (L3). `SmarTeam_RetryOnException` and `SmarTeam_IdleTimeout` (pooledConnectionIdleTimeout, ms) are not in the I0539 set: UNVERIFIED until the CPI test |

## Open points (not changed)
- Step names in the parent still contain `MaintananceBOMXML` / `MaintananceBOM_Event`. These are handled in the parent round.
