# Reference iFlow Scan — Full Findings
Scanned: all 18 iFlow ZIPs under `_reference/iflows/`, 2026-11-15

---

## 1. iFlow Inventory

| iFlow | Version | Type | Sender | Receiver | Queue |
|---|---|---|---|---|---|
| I0048_CostCenter_COSMAS…_GSAP_Medius_JMSToREST | 1.0.10 | Old child (own queue) | GSAP | Medius REST | `I0048_MEDIUS` |
| I0050_InternalOrder_…_GSAP_Medius_JMSToREST | 1.0.14 | Old child | GSAP | Medius REST | `I0050_MEDIUS` |
| I0083_Invoice_Medius_IFSSE_…_JMSToSFTPToDS | 1.0.45 | Old child (complex) | JMS | SFTP + DS + Medius | own queue |
| I0115_Invoice_Medius_FSAP_…_PDToSOAP | 1.31 | Child (PD) | ProcessDirect | FSAP SOAP | — |
| I0115_Invoice_Medius_GSAP_…_JMSToRFC | 1.229 | Old child (own queue) | JMS | GSAP RFC | own queue |
| I0161_Project_…_GSAP_Medius_JMSToREST | 1.0.13 | Old child | GSAP | Medius REST | `I0161_MEDIUS` |
| I0540_CostCenter_FSAP_Medius_JMSToREST | 1.0.26 | Old child | FSAP | Medius REST | `I0540_MEDIUS` |
| I0541_InternalOrder_FSAP_Medius_JMSToREST | 1.0.16 | Old child | FSAP | Medius REST | `I0541_MEDIUS` |
| I0544_BusinessPartner_FSAP_Medius_JMSToREST | 1.0.47 | Old child | FSAP | Medius REST | `I0544_MEDIUS` |
| I0544_BusinessPartner_FSAP_StreamServeDDS_JMSToJDBC | 1.0.9 | Old child | FSAP | StreamServeDDS JDBC | `I0544_StreamServeDDS` |
| I0545_WBSElement_FSAP_Medius_JMSToREST | 1.0.13 | Old child | FSAP | Medius REST + OData | `I0545_MEDIUS` |
| I0701_P_JMSDispatcher_MSAP_PlantMaintenance | 1.1 | **Dispatcher** | JMS | ProcessDirect | `I0701_MSAP_PlantMaintenance` + `_D` |
| I2018_Material_MSAP_SmarTeam_PDToHTTP | 1.0.5 | Child (PD→HTTP) | ProcessDirect | SmarTeam HTTP | reads `I2018_SmarTeam` (old) |
| I2023_Equipment_…_MSAP_SmarTeam_PDToHTTP | 1.0.4 | Child | ProcessDirect | SmarTeam HTTP | reads `I2023_SmarTeam` |
| I2024_FunctionLocation_…_MSAP_SmarTeam_PDToHTTP | 1.0.4 | Child | ProcessDirect | SmarTeam HTTP | reads `I2024_SmarTeam` |
| I2051_P_DocumentInfoRecord_Create_SmarTeam_HTTPToODATA | 1.0.1 | Parent (HTTP→OData, no JMS) | SmarTeam HTTPS | MSAP OData | — |
| I2052_DocumentInfoRecord_Update_…_SmarTeam_MSAP_PDToIDoc | 1.0.4 | Child (PD→IDoc) | ProcessDirect | MSAP IDoc | — |
| I2052_P_DocumentInfoRecord_Update_SmarTeam_HTTPToJMS | 1.0.3 | **Parent (_P_, HTTP→JMS)** | SmarTeam HTTPS | JMS | writes to dispatcher queue |

---

## 2. JMS Queues

### Old pattern (one queue per interface — being migrated)
- `I0048_MEDIUS`, `I0050_MEDIUS`, `I0161_MEDIUS` (GSAP→Medius)
- `I0540_MEDIUS`, `I0541_MEDIUS`, `I0544_MEDIUS`, `I0545_MEDIUS` (FSAP→Medius)
- `I0544_StreamServeDDS`
- `I2018_SmarTeam`, `I2023_SmarTeam`, `I2024_SmarTeam` (old per-interface SmarTeam queues — still active)
- `I_SmarTeam_D` — shared DLQ already in use for I2018/I2023/I2024

### New dispatcher pattern
- `I0701_MSAP_PlantMaintenance` + `I0701_MSAP_PlantMaintenance_D`
- Planned from PPTX: `I0700_SmarTeam` + `I0700_SmarTeam_D` (not yet live in references)

Queue naming: old = `I<interfaceId>_<System>`; new dispatcher = `I<dispatcherId>_<System>_<Area>`.
DLQ always = queue name + `_D`.

---

## 3. ProcessDirect Addresses

| Address | Used in |
|---|---|
| `/I2018_Material_MSAP_SmarTeam_PDToHTTP` | I2018 retrigger endpoint |
| `/I2023_Equipment_…_PDToHTTP` | I2023 retrigger |
| `/I2024_FunctionLocation_…_PDToHTTP` | I2024 retrigger |
| `/I2052_DocumentInfoRecord_Update_…_PDToIDoc` | I2052 retrigger + I2052_P parameter |
| `/I0115_Invoice_Medius_FSAP_…_PDToSOAP` | I0115_FSAP retrigger |
| `/I0115_Invoice_Medius_GSAP_…_JMSToRFC` | I0115_GSAP retrigger |
| `/${header.SSAB_Dispatcher_ReceiverIFlow}` | I0701 dispatcher → any child |
| `/I0096_P_MasterData_MDMLookup_PDToHTTP` | I0083 → lookup service |
| `/I0084_P_Invoice_Medius_GetInvoiceAttachment_PDToREST` | I0083 → attachment fetch |
| `{{MSAP_IDocEndpoint}}` | I2052 → IDoc sender (parameterised) |

ProcessDirect address = iFlow name exactly. Retrigger via HTTPS is kept on every child.

---

## 4. Headers and Properties

| Name | Set by | Read by | Purpose |
|---|---|---|---|
| `SSAB_Dispatcher_ReceiverIFlow` | Parent (_P_) "Set JMS Dispatcher" Enricher | Dispatcher ProcessDirect route | Names the target child iFlow |
| `SAP_MessageProcessingLogCustomStatus` | Dispatcher (`split('_')[0]`) + Parent | MPL / queue monitor | Shows interface ID (e.g. `I2018`) |
| `SAP_ApplicationID` | XPath from payload (`//MessageId`) | MPL | Business key for MPL search |
| `AllowedHeaders=SSAB.*` | parameters.prop | CPI runtime | Passes all SSAB_* headers through adapters |
| `CH_*` prefix | Content Modifiers | Local | e.g. `CH_DocumentInfoRecord`, `CH_SmarTeamMessageId` |

---

## 5. Groovy Scripts

### UTIL bundles (not bundled locally — referenced via Require-Capability)
- `UTIL_LogPayloadAsAttachment` → `logPayloadAsAttachment.groovy` — every flow
- `UTIL_LogCustomHeaders` → `logCustomHeaders.groovy` — every flow
- `UTIL_CaptureCamelError`
- `UTIL_GetValueMapping`

### Scripts bundled locally by iFlow
| Script | iFlow(s) |
|---|---|
| `concatText.groovy` | I2018, I2023, I2024 (SmarTeam children) |
| `DetemineText.groovy` *(SAP typo — keep as-is)* | I2051_P, I2052, I2052_P |
| `customerMaster.groovy`, `getProperty.groovy`, `convertBoolean.groovy` | I0048, I0050, I0161 |
| `checkStatus.groovy`, `formatNumber.groovy` | I0050 |
| `removezeros.groovy`, `removeleadzeros.groovy`, `extractToken.groovy`, `removeControllA.groovy`, `ReplaceWithVirtualCompany.groovy` | I0540, I0544_Medius |
| `CleanNamespace.groovy`, `SupplierMaster.groovy`, `joinNames.groovy`, `CompareDates.groovy`, `getTaxID.groovy`, `identifierType.groovy` | I0544_Medius |
| `cropString.groovy` | I0544_StreamServeDDS |
| `ReplaceWithVirtualCompany.groovy` | I0541, I0545 |

---

## 6. Repeating Step Patterns

### Pattern A — Old JMSToREST/RFC (I0048, I0050, I0161, I0540–I0545)
```
Main Process (outer): Integration Process from Source [ProcessCallElement]
Integration Process from Source:
  Log Custom Headers [Script]
  → Set Identifier + Set Source Payload [Enricher ×2]
  → Set AttachmentName [Enricher]
  → Set Monitoring Identifiers [Enricher]
  → Log Payload × 3 [ProcessCallElement]   (IncomingPayload, pre-map, post-map)
  → [optional XSLT / Script]
  → Mapping
  → ExternalCall to receiver
Error Process:
  Main Process [ProcessCallElement] → Send To DLQ [Send] → MaxRetries [Gateway]
Log Payload subprocess: Log Payload As Attachment [Script]
```

### Pattern B — SmarTeam PDToHTTP child (I2018, I2023, I2024, I2049, I2050)
```
Main Process (outer): Main Process subprocess [ProcessCallElement]
Main Process subprocess (Process_28):
  Set Custom Header [Script]
  → Set Monitoring Identifiers [Enricher]
  → Set AttachmentName (IncomingPayload) [Enricher]
  → Log Payload [ProcessCallElement]
  → [optional Lookup subprocess]
  → Mapping
  → Set AttachmentName (OutputPayload) [Enricher]
  → Log Payload [ProcessCallElement]
  → Send to SmarTeam [ExternalCall/HTTP]
  → Set AttachmentName (SmartTeamResponse) [Enricher]
  → Log Payload [ProcessCallElement]
  → End
Log Payload subprocess (Process_12): Log Payload as Attachment [Script]
Manual Retrigger process (Process_734044)
```

### Pattern C — New Parent _P_ (HTTPToJMS) (I2052_P)
```
Integration Process From Source:
  Log Custom Headers [Script]
  → Set Monitoring Identifiers [Enricher]  (SAP_ApplicationID XPath + properties)
  → Set JMS Dispatcher [Enricher]
      header SSAB_Dispatcher_ReceiverIFlow = {{param: target child iFlow name}}
      header SAP_MessageProcessingLogCustomStatus = interface ID prefix
  → Content Modifier (build response)
  → Log Payload [ProcessCallElement]
  → Send to JMS [Send]  → dispatcher queue
```

### Pattern D — Dispatcher (I0701)
```
Integration Process:
  Log Custom Header [Script]
  → Set SAP_MessageProcessingLogCustomStatus [Enricher]
      value = ${header.SSAB_Dispatcher_ReceiverIFlow.split('_')[0]}
  → MaxRetries [Gateway]
      YES → Send to DLQ [Send] → Escalation End
      NO  → ProcessDirect /${header.SSAB_Dispatcher_ReceiverIFlow}
```

---

## 7. Dispatcher JMS Parameters (from parameters.prop / parameters.propdef)
```
JMS_AccessType=Non-Exclusive
JMS_ConcurentProcesses=1
JMS_ExpirationDays=30
JMS_InternalDLQ=1
JMS_RetryInterval=1
JMS_ExponentialBackoff=1
MaxRetries=2
AllowedHeaders=SSAB.*
```

---

## 8. UserRoles Seen
- `SSAB_MessagingSend_SmarTeam` — SmarTeam HTTPS senders (I2018, I2023, I2024 retrigger)
- `SSAB_MessagingSend_InternalOperations` — SmarTeam PDToHTTP retrigger
- `SSAB_MessagingSend_StripSAP` — plant maintenance dispatcher
