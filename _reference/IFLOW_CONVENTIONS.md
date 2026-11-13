# iFlow patterns and naming conventions

This file comes from the four iFlow exports in `_reference/` plus your answers in the setup Q&A (2026-11-13). A source in brackets marks where each point came from. "Q&A" means you decided it; anything else was observed in the files.

## 1. Message path: Parent → JMS → Dispatcher → PD child → target

```
Sender system ──HTTPS──▶ I<nnnn>_P_…_HTTPToJMS ──JMS queue──▶ I0701_P_JMSDispatcher_… ──ProcessDirect──▶ I<nnnn>_…_PDTo<Target> ──▶ target
                         (parent)                 I0701_MSAP_    (dispatcher)            /${header.       (child)
                         sets header                PlantMaintenance                     SSAB_Dispatcher_
                         SSAB_Dispatcher_ReceiverIFlow                                   ReceiverIFlow}
```

### 1.1 Parent flow, e.g. `I2052_P_DocumentInfoRecord_Update_SmarTeam_HTTPToJMS`
- **HTTPS sender**: `urlPath=/I2052_P_DocumentInfoRecord_Update_SmarTeam_HTTPToJMS`, which is `/` plus the iFlow name. [I2052P .iflw]
- **Set Monitoring Identifiers** (Content Modifier):
  - The header `SAP_ApplicationID` is read by XPath from the payload (`//MessageId`).
  - Properties such as `CH_DocumentInfoRecord` are also read by XPath. [I2052P .iflw]
- **Set JMS Dispatcher** (Content Modifier): the header `SSAB_Dispatcher_ReceiverIFlow` is set to `{{SSAB_Dispatcher_ReceiverIFlow}}`. [I2052P .iflw]
  - The externalized value is the child iFlow name: `I2052_DocumentInfoRecord_Update_DOCMAS05_CLFMAS02_SmarTeam_MSAP_PDToIDoc`. [I2052P parameters.prop]
- **Send to JMS**: a JMS receiver writes to `QueueName_outbound=I0701_MSAP_PlantMaintenance`, which is the dispatcher's queue. [I2052P .iflw]
- **Response**: a Content Modifier builds a synchronous ack (`<DocumentInfoRecordUpdateResponse>` holding the request and response message IDs). [I2052P .iflw]
- Local processes are "Main Process" and "Log payload". [I2052P .iflw]

### 1.2 Dispatcher, e.g. `I0701_P_JMSDispatcher_MSAP_PlantMaintenance`
- **JMS sender**: `QueueName_inbound={{JMS_QueueName}}`, which is `I0701_MSAP_PlantMaintenance`. [I0701 .iflw, parameters.prop]
- A Content Modifier copies the header into property `CH_SSAB_Dispatcher_ReceiverIFlow`. It also sets a custom status from `${header.SSAB_Dispatcher_ReceiverIFlow.split('_')[0]}`, which is the interface number. [I0701 .iflw]
- **MaxRetries gateway**: when `${header.SAPJMSRetries} > '{{MaxRetries}}'` (2), the message goes to a JMS receiver for the DLQ `{{JMS_QueueName}}_D` and ends in an escalation end. [I0701 .iflw, parameters.prop]
- Otherwise the **ProcessDirect receiver** sends to `address=/${header.SSAB_Dispatcher_ReceiverIFlow}`. [I0701 .iflw]
- One dispatcher serves one target system and area. Any child flow is reached through the header value. [I0701 .iflw, README]

### 1.3 Child flow, e.g. `I2052_DocumentInfoRecord_Update_DOCMAS05_CLFMAS02_SmarTeam_MSAP_PDToIDoc`
- **ProcessDirect sender**: `address=/I2052_DocumentInfoRecord_Update_DOCMAS05_CLFMAS02_SmarTeam_MSAP_PDToIDoc`, which is `/` plus the iFlow name. This must equal the parent's `SSAB_Dispatcher_ReceiverIFlow` value. [I2052 .iflw, I2052P parameters.prop]
- The child keeps the parent's **interface number** but drops `_P_`. [I2052 vs I2052P]
- **Sequential Multicast**, with one branch per IDoc in this example. Each branch has:
  - a Mapping step: `Map_DOCMAS05` → `Map_SmarTeam_MSAP_DIR_DOCMAS05`, `Map_CLFMAS02` → `Map_SmarTeam_MSAP_DIR_CLFMAS02`
  - a "Set Attachment Name" step
  - a "Log Payload" call
  - [I2052 .iflw]
- **IDoc to SAP**: an External Call over a ProcessDirect receiver to `{{MSAP_IDocEndpoint}}`, which is `/I2004_MSAP_IDOCReceiver`, a shared IDoc sender flow. [I2052 .iflw, parameters.prop]
- IDoc control values are externalized and read in the mapping with `getProperty`: `SNDPOR`, `SNDPRT`, `SNDPRN`, `RCVPOR`, `RCVPRT`, `RCVPRN`, `ClassType` and others. [I2052 parameters.prop, `Map_SmarTeam_MSAP_DIR_CLFMAS02.mmap`]
- A child flow can also call RFC directly. I0115 uses an RFC receiver (`{{RFCDestination}}` = `RFC_QR1_100`) and a JMS receiver to `I0151_SendEmail` for e-mail. [I0115 .iflw, parameters.prop]

### 1.4 Shared pieces seen in every flow
- **Script collections**, referenced through `scriptBundleId` and the MANIFEST `Require-Capability`: [all MANIFEST.MF, .iflw]
  - `UTIL_LogCustomHeaders` (`logCustomHeaders.groovy`)
  - `UTIL_LogPayloadAsAttachment` (`logPayloadAsAttachment.groovy`)
  - `UTIL_CaptureCamelError`
  - `UTIL_GetValueMapping`
- **"Log Payload"** is a local process with "Log Payload As Attachment". The `LogPayload=True` parameter switches it. [I2052P, I2052, I0115]
- **"Set Monitoring Identifiers"** is a Content Modifier at the start of the main process. [I2052P, I2052]
- **Common externalized parameters**: `SAP_Sender`, `SAP_Receiver`, `UserRole` (e.g. `SSAB_MessagingSend_SmarTeam`), `HTTPSessionReuse`, `Timeout`, and `MaxRetries`. [parameters.prop files]
- The **customer prefix** `SSAB_` is used for custom headers (`SSAB_Dispatcher_ReceiverIFlow`) and roles. `AllowedHeaders=SSAB.*` is set in the dispatcher. [I0701 parameters.prop]
- Header and property names copied in flows use the `CH_` prefix (`CH_SmarTeamMessageId`, `CH_DocumentInfoRecord`). [I2052P, I2052 .iflw]

## 2. Naming conventions

### 2.1 iFlows
| Kind | Pattern | Example |
|---|---|---|
| Parent | `I<nnnn>_P_<Object>_<Action>_<SrcSys>_<Sender>To<Receiver>` | `I2052_P_DocumentInfoRecord_Update_SmarTeam_HTTPToJMS` |
| Dispatcher | `I<nnnn>_P_JMSDispatcher_<TgtSys>_<Area>` | `I0701_P_JMSDispatcher_MSAP_PlantMaintenance` |
| Child (PD) | `I<nnnn>_<Object>_<Action>[_<MsgTypes>]_<SrcSys>_<TgtSys>_<Sender>To<Receiver>` | `I2052_DocumentInfoRecord_Update_DOCMAS05_CLFMAS02_SmarTeam_MSAP_PDToIDoc` |

- `I<nnnn>` is a 4-digit interface number. The parent and child of one interface share it. The dispatcher has its own number. [references]
- `_P_` marks a parent (entry) flow. The dispatcher also carries `_P_`. [README, references]
- **`<Sender>To<Receiver>`**:
  - The **sender** is always the real inbound adapter: `HTTP`, `JMS` or `PD`.
  - The **receiver** names the adapter, except for IDoc. An IDoc is sent over ProcessDirect to the shared IDoc flow, but the name still says `IDoc` so the target is clear. Example: `PDToIDoc`. [Q&A]
- Systems are written as short codes: `SmarTeam`, `MSAP`, `GSAP`, `Medius`. [references]
- ProcessDirect address = `/` + the iFlow name. HTTPS urlPath = `/` + the iFlow name. [I2052, I2052P, I0115]

### 2.2 Message mappings
- **Pattern for new mappings: `Map_<Src>_<Tgt>_<Object>_<MsgType>`.** Example: `Map_SmarTeam_MSAP_DIR_DOCMAS05`. [Q&A] It can be revised later if names get too long.
- The `.mmap` file name, the mapping step's `mappingname`, and the standalone zip name are all equal to the mapping name. [I2052 .iflw, standalone zips]
- In the iFlow, the step name can be short (`Map_DOCMAS05`) while the mapping is long. [I2052 .iflw]
- You give the name in chat for each mapping. It can differ from the folder name in `mappings/`. [Q&A]

### 2.3 JMS queues
- Dispatcher queue = `<DispatcherNo>_<TgtSys>_<Area>`, e.g. `I0701_MSAP_PlantMaintenance`. Its DLQ adds the suffix `_D`. [I0701, I2052P]
- Other queue example: `I0151_SendEmail`, which feeds `I0151_P_UTIL_SendEmailWithAttachments_JMSToMail`. [I0115 .iflw]

### 2.4 Other names
- Groovy UDF scripts use lowerCamel or PascalCase function names, and the file name matches the main function (`concatText.groovy`, `GetDeliveryDetails.groovy`). [mapping exports]
- Externalized parameters are PascalCase or `SAP_`-style (`MSAP_IDocEndpoint`, `SAP_Sender`). JMS parameters use `JMS_*`. [parameters.prop files]

## 3. Observed deviations (legacy, do not copy)
| What | Where | Rule today |
|---|---|---|
| `.iflw` file names left over from templates: `IC00001_ZHR_INTERFACE_PR4_500_SalesforceJMSToOData.iflw`, `I00002_P_IDocDispatcher_SAPHR_IDocToProcessDirect.iflw`, `I0083_P_Invoice_Medius_IFSSE_HTTPToJMS.iflw` | I2052, I2052P, I0701, I0115 | **Open question for the iFlow phase**: should the `.iflw` name equal the iFlow name? |
| `I0115_…_JMSToRFC` starts with a ProcessDirect sender | I0115 | It would be `PDToRFC` today [Q&A] |
| `MapToRFC_BAPI_INCOMINGINVOICE_GETDETAIL` targets `BAPI_INCOMINGINVOICE_CREATE1`, and `Map_Material_SmartTeam` doesn't follow the pattern | mapping exports | Use `Map_<Src>_<Tgt>_<Object>_<MsgType>` |
| Mappings bundled but never used by a step: `MapSpecialTaxCases`, `MapTaxBaseAmount`, `MapToRFC_BAPI_ACC_DOCUMENT_POST_OTM` (I0115), `Map_SmartTeam_MSAP_CreateDIR` (I2052P) | I0115, I2052P | Don't bundle unused mappings |
| Typos kept in artifact names: `GetompletelyDeductibleTaxPercentage.groovy`, `DetemineText.groovy`, `CreditMemo_ReverseCharge_PartiallyDeductubile.xslt` | I0115, I2052 | Spell new names correctly |
| Duplicate parameter keys with typos: `JMSMaxetryInterval` / `JMSMaxRetryInterval`, `JMS_ExponentialBackOff` / `JMS_ExponentialBackoff` | I0701 parameters.prop | — |
