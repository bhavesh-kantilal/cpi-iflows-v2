# CPI Message Mapping export format — notes from the references

Everything here was taken from the exports in `_reference/`. Nothing comes from SAP documentation or general knowledge.
Items marked **UNVERIFIED** are my reading of the data, not something a reference proves. Ask before you rely on them.
Items marked **NOT COVERED** do not appear in any reference. If a build needs one, stop and ask.

## Source codes used in citations

| Code | File |
|---|---|
| MAT | `Map_Material_SmartTeam/mapping/Map_Material_SmartTeam.mmap` (+ `.zip`) |
| ACC | `MapToRFC_BAPI_ACC_DOCUMENT_POST/mapping/MapToRFC_BAPI_ACC_DOCUMENT_POST.mmap` (+ `.zip`) |
| INV | `MapToRFC_BAPI_INCOMINGINVOICE_GETDETAIL/mapping/MapToRFC_BAPI_INCOMINGINVOICE_GETDETAIL.mmap` (+ `.zip`) |
| CLF | `Map_SmarTeam_MSAP_DIR_CLFMAS02/mapping/Map_SmarTeam_MSAP_DIR_CLFMAS02.mmap` (+ `.zip`) |
| DOC | `Map_SmarTeam_MSAP_DIR_DOCMAS05/mapping/Map_SmarTeam_MSAP_DIR_DOCMAS05.mmap` (+ `.zip`) |
| DIR | `iflows/I2052_P_DocumentInfoRecord_Update_SmarTeam_HTTPToJMS/src/main/resources/mapping/Map_SmartTeam_MSAP_CreateDIR.mmap` |
| CCM | `CostCentertoMedius/mapping/CostCentertoMedius.mmap` (+ `.zip`) |
| FLAT | `MM_MediusInvoice_To_IFSSE/mapping/MM_MediusInvoice_To_IFSSE.mmap` (+ `.zip`) |
| JDBC | `MapBPToDDSJDBC/mapping/MapBPToDDSJDBC.mmap` (+ `.zip`) |
| JE | `MapToJournalEntryRequest/mapping/MapToJournalEntryRequest.mmap` (+ `.zip`) |
| SUP | `SupplierMastertoMedius/mapping/SupplierMastertoMedius.mmap` (+ `.zip`) |
| I0115 | `iflows/I0115_Invoice_Medius_GSAP_ProcessPostedInvoices_JMSToRFC/` (iFlow export) |
| I2052P | `iflows/I2052_P_DocumentInfoRecord_Update_SmarTeam_HTTPToJMS/` (iFlow export) |
| I2052 | `iflows/I2052_DocumentInfoRecord_Update_DOCMAS05_CLFMAS02_SmarTeam_MSAP_PDToIDoc/` (iFlow export) |
| I0701 | `iflows/I0701_P_JMSDispatcher_MSAP_PlantMaintenance/` (iFlow export) |

---

## 1. Zip / folder layout

### 1.1 Standalone Message Mapping export (the build target)
Sources: `Map_Material_SmartTeam.zip`, `MapToRFC_BAPI_ACC_DOCUMENT_POST.zip`, `MapToRFC_BAPI_INCOMINGINVOICE_GETDETAIL.zip`, `Map_SmarTeam_MSAP_DIR_CLFMAS02.zip`, `Map_SmarTeam_MSAP_DIR_DOCMAS05.zip`, `CostCentertoMedius.zip`, `MM_MediusInvoice_To_IFSSE.zip`, `MapBPToDDSJDBC.zip`, `MapToJournalEntryRequest.zip`, `SupplierMastertoMedius.zip`.

```
<MappingName>.zip
├── mapping/<MappingName>.mmap      exactly one .mmap; file name = mapping name
├── script/<udf>.groovy             only if the mapping uses Groovy UDFs
├── xsd/<schema>.xsd                XSD / IDoc XSD sources and targets
├── wsdl/<service>.wsdl             WSDL sources and targets (RFC or SOAP)
└── json/<api>.json                 OpenAPI/Swagger JSON sources and targets (CCM)
```

- The zip has **no** `META-INF/MANIFEST.MF`, `.project` or `metainfo.prop`. Those files appear only in iFlow exports.
- Entries sit at the zip root with no wrapper folder. The zip has no separate directory entries, only file entries. Compression is Deflate. Source: `unzip -v` on all five zips.
- Entry order is not alphabetical and differs between zips. **UNVERIFIED** whether CPI cares about the order.
- A folder appears only if it has files. For example, CLF and DOC have no `script/` and no `wsdl/`.
- The file extension is kept as exported, including upper case: `wsdl/DOC_WEBI_PRODUCTMDMBULKREPLICATEREQUEST.WSDL` (MAT).
- The `.mmap`, `.groovy`, `.xsd` and `.wsdl` files are byte-identical to the copies inside the iFlow exports. For example, ACC = `I0115/src/main/resources/mapping/MapToRFC_BAPI_ACC_DOCUMENT_POST.mmap` (85563 bytes each), and CLF/DOC = the copies in I2052.
- The `.mmap` still points to `src/main/resources/<folder>` even though the standalone zip uses flat folders (see §2.2). Generated mappings must keep that `src/main/resources/...` path.

### 1.2 iFlow export (for reference; the later iFlow phase)
Sources: I0115, I0701, I2052, I2052P.

```
<iFlowName>.zip
├── .project
├── metainfo.prop
├── META-INF/MANIFEST.MF
└── src/main/resources/
    ├── parameters.prop
    ├── parameters.propdef
    ├── scenarioflows/integrationflow/<name>.iflw
    ├── mapping/   *.mmap, *.xslt, *.xsl
    ├── script/    *.groovy, *.gsh
    ├── xsd/       *.xsd
    ├── wsdl/      *.wsdl (and an .xsd in I2052P)
    └── edmx/      *.edmx (I2052P)
```

- **`MANIFEST.MF`** (all four iFlows):
  - `Manifest-Version: 1.0`.
  - `Bundle-SymbolicName`, `Origin-Bundle-SymbolicName`, `Bundle-Name` and `Origin-Bundle-Name` = the iFlow name.
  - Lines are wrapped with a leading-space continuation. The symbolic name is split mid-word, e.g. `...HTTPToJM` / ` S` in I2052P.
  - `Bundle-ManifestVersion: 2`, `Bundle-Version` (e.g. `1.0.3` I2052P, `1.229` I0115, `1.1` I0701), `SAP-BundleType: IntegrationFlow`, `SAP-NodeType: IFLMAP`, `SAP-RuntimeProfile: iflmap`.
  - A long `Import-Package` and `Import-Service` list.
  - `Require-Capability` lists the script collections used, e.g. `scriptcollection.UTIL_LogCustomHeaders;resolution:=optional;bundleType:String="ScriptCollection";source:String="reference"`.
- **`.project`** (I2052P): an Eclipse `projectDescription`.
  - `<name>` = the iFlow name.
  - Builder `org.eclipse.jdt.core.javabuilder`.
  - Natures `org.eclipse.jdt.core.javanature`, `com.sap.ide.ifl.project.support.project.nature` and `com.sap.ide.ifl.bsn`.
- **`metainfo.prop`** (all iFlows): 3 lines.
  ```
  #Store metainfo properties
  #<timestamp UTC>
  description=
  ```
- The `.iflw` file name does **not** match the iFlow name in three of four exports. See IFLOW_CONVENTIONS.md, "Observed deviations".
- **NOT COVERED**: a MANIFEST for a standalone Message Mapping artifact. None exists, and the build target does not need one.
- **WSDLs that import XSDs** (`<xsd:import namespace="…" schemaLocation="…"/>`): CPI resolves `schemaLocation` **only as a relative file path from the importing file's own folder**. It does not fetch `https://` URLs, and it does not match imported XSDs by namespace. **CONFIRMED 2026-11-15** by the user's NShift tests (`mappings/5_…/spec.md`):

  | Test | `schemaLocation` in the WSDL (`wsdl/`) | XSDs | Result |
  |---|---|---|---|
  | A | `https://service.web-ta.net/…?xsd=1` (original) | imported by hand into the mapping | structure unresolved |
  | B | `ConsignmentWS_xsd1.xsd` | imported by hand (land in `xsd/`) | structure unresolved |
  | C | `ConsignmentWS_xsd1.xsd` | in the zip's `wsdl/`, next to the WSDL | **works** |
  | D | `../xsd/ConsignmentWS_xsd1.xsd` | in the zip's `xsd/` | **works** |

  - **Default (user decision 2026-11-15): D.** Keep the XSDs unchanged in `xsd/`, and change only the `schemaLocation` values in a copy of the WSDL to `../xsd/<file>.xsd`. The toolkit packs every relatively imported file automatically (`package.py`), and the checks follow the imports.
  - **Alternative:** inline the schemas into the WSDL (`tools/wsdl_inline.py`, NShift v1.0.1/v1.0.2, works). One inline `<schema>` per namespace, joined by namespace-only `<import namespace="…"/>`, as in the SAP WSDLs of the references (CCM, JE, SUP, MAT). Each inlined schema must keep its own `xmlns:tns` declarations; otherwise `type="tns:…"` silently points to the WSDL's `tns` (NShift v1.0.0: empty Consignment in CPI). See `docs/explained/wsdl-imports-and-namespaces.md`.

---

## 2. The .mmap file

### 2.1 Encoding and envelope
Sources: all 18 `.mmap` files (13 originals + CCM, FLAT, JDBC, JE, SUP).

- The whole document is on **one line**, with no line breaks and no trailing newline. It is UTF-8 with **no BOM** and **no `<?xml ...?>` prolog**. The first bytes are `<xiObj`.
- Skeleton (MAT):

```xml
<xiObj xmlns="urn:sap-com:xi">
  <idInfo xmlns="" VID="01"><vc caption="LOCAL" sp="-1" swcGuid="00000000000000000000000000000000" vcType="S"><clCxt consider="A"/></vc><key typeID="XI_TRAFO" version=""/><version>1.0</version></idInfo>
  <documentation xmlns=""><description/></documentation>
  <generic xmlns="">
    <admInf><modifBy></modifBy><modifAt></modifAt><modifAtLong>{epoch millis}</modifAtLong><owner/></admInf>
    <lnks> ... schema + UDF links (§2.2, §3.9) ... </lnks>
    <textInfo loadedL="EN"><textObj id="{32 hex}" masterL="EN" type="0"><texts lang="EN"><text label=""/><text label="21327ec998d3248b3333da4cbe20b699"></text></texts></textObj></textInfo>
  </generic>
  <AdditionalProperties xmlns=""> ... 4 Property entries ... </AdditionalProperties>   <!-- optional, see below -->
  <content xmlns="">
    <tr:XiTrafo xmlns:tr="urn:sap-com:xi:mapping:xitrafo">
      <tr:MetaData><mappingtool version="XI7.1"><project version="XI7.1">
        <libstorage> ... </libstorage>
        <transformation> ... Dst bricks ... <namespaces>...</namespaces> </transformation>
        <testData><instances/></testData>
        <ViewState></ViewState>
        <pcont/>
      </project></mappingtool></tr:MetaData>
      <tr:ByteCodeJar/><tr:SourceStructure/><tr:TargetStructure/>
      <tr:Multiplicity>1:1</tr:Multiplicity>
      <tr:SourceParameters><tr:Parameter><tr:Position>1</tr:Position><tr:Minoccurs>1</tr:Minoccurs><tr:Maxoccurs>1</tr:Maxoccurs></tr:Parameter></tr:SourceParameters>
      <tr:TargetParameters><tr:Parameter><tr:Position>1</tr:Position><tr:Minoccurs>1</tr:Minoccurs><tr:Maxoccurs>1</tr:Maxoccurs></tr:Parameter></tr:TargetParameters>
    </tr:XiTrafo>
  </content>
</xiObj>
```

- `modifBy`, `modifAt` and `owner` are empty in every reference. `modifAtLong` is a Unix epoch in milliseconds, e.g. `1793287868129` in MAT.
- `textObj id` is a 32-hex value that differs per file. **UNVERIFIED**: probably a random GUID.
- The second `text label` is the same value `21327ec998d3248b3333da4cbe20b699` in 17 of the 18 `.mmap` files. The exception is `MapSpecialTaxCases.mmap` (I0115). **UNVERIFIED** what it means. Copy it unchanged.
- `AdditionalProperties` appears in MAT, CLF, DOC, DIR, CCM, JDBC, JE, SUP and the two I0115 tax mappings. It does **not** appear in ACC, INV, FLAT or `MapToRFC_BAPI_ACC_DOCUMENT_POST_OTM.mmap`. It is not tied to age: CCM has an older `modifAtLong` than ACC but still has it. **UNVERIFIED** what triggers it. When present it contains, in this order:
  - `externalNameSpace`
  - `choiceOccurrence`
  - `groupsOccurrence`
  - `topLevelChoiceOccurrenceApplied`

  Each entry is `<Property Applicable="BOTH"><PropertyName>…</PropertyName><PropertyValue>RESOLVED</PropertyValue></Property>`.
  - **Variations found by the toolkit self-test:**
    - MAT, CLF, DOC and DIR have all 4 entries.
    - CCM, JDBC, JE, SUP and `MapTaxBaseAmount` have only the first 3 (no `topLevelChoiceOccurrenceApplied`).
    - The legacy `MapSpecialTaxCases` has only `externalNameSpace`.
  - New builds include all 4. **CONFIRMED 2026-11-13**: the ORDERS v1.0.0 build with 4 entries imported and ran in CPI. Whether the block is *required* stays untested.
- **Blank `xmlns=""`:** `idInfo`, `documentation`, `generic`, `AdditionalProperties` and `content` carry `xmlns=""` in every file except FLAT, which has none of them. New builds include it, like the majority; the ORDERS build imported fine.
- `Multiplicity` is always `1:1`, with exactly one source parameter and one target parameter. **NOT COVERED**: 1:n, n:1, and mapping parameters.
- `testData/instances` is always empty and `ViewState` is always empty. **NOT COVERED**: stored test instances.

### 2.2 Source and target schema references (`generic/lnks`)
Each mapping has one `lnkRole role="SOURCE_IFR_MESS"` and one `lnkRole role="TARGET_IFR_MESS"`, both with `kpos="1"`. Each holds `<lnk rMode="R"><key typeID="…" version="1.1">` with `<elem>` children.

| Kind | typeID | elem 1 | elem 2 | elem 3 | elem 4 | Source |
|---|---|---|---|---|---|---|
| XSD | `xsd` | file name | `src/main/resources/xsd` | root element name | — | ACC source `Medius_Invoice.xsd` / `root`; MAT target `SmarTeam.xsd` / `SAPMasterData` |
| IDoc XSD | `xsd` | `CLFMAS.CLFMAS02.xsd` | `src/main/resources/xsd` | `CLFMAS02` | — | CLF target; DOC target `DOCMAS.DOCMAS05.xsd` / `DOCMAS05` |
| WSDL (RFC) | `wsdl` | file name | `src/main/resources/wsdl` | message element (e.g. `BAPI_ACC_DOCUMENT_POST`) | `urn:sap-com:document:sap:rfc:functions` | ACC target, INV target |
| WSDL (SOAP) | `wsdl` | `DOC_WEBI_PRODUCTMDMBULKREPLICATEREQUEST.WSDL` | `src/main/resources/wsdl` | `ProductMDMBulkReplicateRequestMessage` | `http://sap.com/xi/SAPGlobal20/Global` | MAT source |
| WSDL whose message name ≠ element name | `wsdl` | `NShift_ConsignmentWS.wsdl` | `src/main/resources/wsdl` | the part's **element** name `book` (WSDL message is `ConsignmentEndpoint_book`) | the element's namespace `http://www.spedpoint.com/consignment/types` | NShift target. **CONFIRMED 2026-11-15**: the user's import of NShift v1.0.1 loaded the full `book` structure. In all other references message and element share one name |
| XSD in wsdl folder | `xsd` | `A_DocumentInfoRecordEntityPOST.xsd` | `src/main/resources/wsdl` | `A_DocumentInfoRecord` | — | DIR target |
| XSD with a targetNamespace | `xsd` | `Ordrsp_1_0_0.xsd` | `src/main/resources/xsd` | `OrdrspInterchange` | the targetNamespace URI, e.g. `http://www.ruukki.com/schemas/eai/internal/production/eruukki` | ORDRSP source. **CONFIRMED 2026-11-13** by the user's CPI download: without elem 4, CPI does not load the XSD on import ("Add source message") |
| JSON (OpenAPI 3.0.3) | `json` | `Medius_Swagger.json` | `src/main/resources/json` | `<api path>__$delim$__<HTTP METHOD>__$delim$__Request`, e.g. `/integration/masterdata/v1/dimensionValueImportBatches__$delim$__POST__$delim$__Request` | empty, written `<elem></elem>` (not `<elem/>`) | CCM target |

- **JSON targets (CCM)**:
  - The structure is the operation's request body schema. Here it is a top-level `type: array` of `#/components/schemas/IntegrationDimensionValueDto`.
  - Brick paths start at the pseudo root **`/__$$RoOt_ArRaY$$__`** for a root array, e.g. `/__$$RoOt_ArRaY$$__/companyId`. The `$` signs are literal.
  - The array node is mapped like a repeating node: `/__$$RoOt_ArRaY$$__` ← `/ns0:CostCentreReplicationBulkRequest/CostCentreReplicationRequestMessage`.
  - JSON targets need no `<namespaces>` entry; CCM's single `ns0` entry is for its SOAP source.
  - **UNVERIFIED**: the elem 3 form for responses, likely `__$delim$__Response`. **NOT COVERED**: root paths for an object (non-array) body.
  - Checking a JSON target path means checking the Swagger schema properties, not an XSD.
  - SUP uses the same Swagger file with operation `/integration/masterdata/v1/supplierImportBatches__$delim$__POST__$delim$__Request`.
  - Nested arrays and objects continue as plain steps, e.g. `/__$$RoOt_ArRaY$$__/paymentDetails/identifiers/erpSourceId`, with no extra array marker.
- **JDBC targets (JDBC)**: a hand-written statement XSD (`MapBPToDDSJDBC/xsd/DDS_JDBC.xsd`) with root `root` and no namespace:
  ```
  /root/StatementName/dbTableName/@action    ← const "UPDATE_INSERT"
  /root/StatementName/dbTableName/table      ← const "dbo.t_Receiver"
  /root/StatementName/dbTableName/access/<Column>   ← values to write
  /root/StatementName/dbTableName/key/<Column>      ← key used for update matching
  ```
  - In the XSD, `action` is a required attribute on `dbTableName`. Columns are optional elements under `access`, and the key column sits under `key`.
  - In the references only `UPDATE_INSERT` with one statement is seen. The rest of this section comes from **SAP documentation (external, not from the references)**, added at the user's request 2026-11-13. It describes the JDBC receiver "XML SQL Format":
    - The root and statement element names are free (here `root` and `StatementName`). One or more statements are allowed, each holding one `dbTableName`. That element name is fixed, and its `action` attribute is mandatory.
    - `action` values: `INSERT`, `UPDATE`, `UPDATE_INSERT`, `DELETE`, `SELECT`, `EXECUTE` (stored procedure) and `SQL_QUERY`. `SQL_QUERY` is written `SQL-QUERY` in one place in the docs.
    - `table` is optional and must be the first child. It holds the real table name and overrides the `dbTableName` name.
    - `access` lists the columns to write or read. It is absent for `DELETE`. `SELECT` must have exactly one `access`.
    - Key blocks (`key1`, `key2`, … in SAP's examples) hold the WHERE conditions. They are used for `UPDATE`, `UPDATE_INSERT`, `DELETE` and `SELECT`.
      - Columns inside one key block appear to be combined with AND, and separate key blocks with OR.
      - Column attribute `compareOperation`: `EQ` (default), `NEQ`, `LT`, `LTEQ`, `GT`, `GTEQ`, `LIKE`.
      - Your reference uses a single block named `key`, which works in your landscape.
    - Column attributes: `hasQuot="YES|NO"` to force or suppress quoting, and `isNull="TRUE"` to ignore the column in the WHERE clause.
    - `UPDATE_INSERT` runs UPDATE first and INSERTs if no row matched. It is not supported in batch mode.
    - Each statement gets a `<StatementName_response>` in the reply, which is only accessible on synchronous calls.
    - **NOT COVERED** (no reference or doc detail yet): EXECUTE stored-procedure parameters, SQL_QUERY placeholders, and batch payloads. Ask for a reference first.
    - Sources: [SAP Help: Document Formats for Message Protocol XML SQL Format](https://help.sap.com/saphelp_nw73/helpdata/en/2e/96fd3f2d14e869e10000000a155106/content.htm), [SAP Help: Configuring the Receiver JDBC Adapter](https://help.sap.com/saphelp_nw73/helpdata/en/48/465581929734d9e10000000a42189d/content.htm). These pages are SAP PI/NetWeaver documentation; the format is reused by Cloud Integration but may differ in details. **UNVERIFIED for CPI.**
- **Flat file targets (FLAT)**: a hand-written XSD `IFSSE.xsd` with no namespace, structured `root/row (maxOccurs unbounded)/<FIELD>`, where every field is `xs:string`. The `.mmap` maps `/root`, `/root/row` and `/root/row/<FIELD>` like any XSD target.
  - The XML-to-CSV conversion is **not** in the mapping; it happens later in the iFlow (README).

- In the XML, TARGET is listed **before** SOURCE in every `.mmap`. UDF `UsedFuncLib` links follow them.
- Paths in bricks begin with the root element: `/root/...` (ACC) or `/CLFMAS02/IDOC/...` (CLF).
- Namespaced roots carry a prefix. The prefix is declared at the end of `transformation`:
  ```xml
  <namespaces><properties><property name="{namespace URI}">{prefix}</property></properties></namespaces>
  ```
  - ACC: `urn:sap-com:document:sap:rfc:functions` → `ns0`, path `/ns0:BAPI_ACC_DOCUMENT_POST/...`.
  - INV: the same URI → `ns1`.
  - MAT: `http://sap.com/xi/SAPGlobal20/Global` → `ns3`, path `/ns3:ProductMDMBulkReplicateRequestMessage/...`.
  - CCM: the same URI → `ns0`, path `/ns0:CostCentreReplicationBulkRequest/...`. The same namespace gets a different prefix per mapping.
  - CLF and DOC have no namespaced root and no `<namespaces>` element.
  - **UNVERIFIED** how the prefix number is chosen.
- A path step gets a prefix only when that element is in a namespace. Usually that is the root alone: unqualified children and attributes have none, e.g. `/ns3:ProductMDMBulkReplicateRequestMessage/ProductMDMReplicateRequestMessage/Product/ProductInternalID` (MAT).
- **Qualified XSD** (`targetNamespace` plus `elementFormDefault="qualified"`): **every** element step gets the prefix, attributes none. Example: `/ns0:OrdrspInterchange/ns0:OrderResponseMessage/ns0:Item/ns0:Date/@Type`.
  - **CONFIRMED 2026-11-13** (ORDRSP): the CPI editor shows `ns0:` on every node. The root-only form showed the children as missing.
  - The payload itself may use a default `xmlns="…"` with no prefix. The prefix exists only in the `.mmap`.
- An element from **another** namespace gets its own prefix in the middle of the path, and each namespace gets its own `<namespaces>` entry.
  - JE: `/ns1:JournalEntryBulkCreateRequest/JournalEntryCreateRequest/JournalEntry/Item/ns2:ZZ1_SSABSourceSystem`
  - The declarations are `http://sap.com/xi/SAPSCORE/SFIN` → `ns1` and `http://SAPCustomFields.com/ZZ1_` → `ns2`.
  - This is the pattern for S/4 custom fields (`ZZ1_`). Other prefixes seen: JDBC `ns1` and SUP `ns0`, both for `http://sap.com/xi/SAPGlobal20/Global`.
- Attributes are written `/@name`, e.g. `/SAPMasterData/Descriptions/Description/@lang` (MAT) and `/CLFMAS02/IDOC/@BEGIN` (CLF).

---

## 3. Transformation: bricks

### 3.1 General brick model
Sources: all `.mmap` files.

- `transformation` holds one **Dst brick** per mapped target node:
  ```xml
  <brick gid="0" path="{target path}" type="Dst"><viewData x=".." y=".."/><arg>{one brick}</arg><group/></brick>
  ```
- Inside an `arg` is either a **Src brick**
  ```xml
  <brick gid="0" path="{source path}" type="Src"><viewData x=".." y=".."/></brick>
  ```
  or a **Func brick**
  ```xml
  <brick fname="{name}" fns="{namespace}" type="Func"><viewData/>{args}{bindings}</brick>
  ```
- Function inputs are `<arg>` for pin 0, then `<arg pin="1">`, `<arg pin="2">` and so on. They come **before** `<bindings>`.
- Function parameters are set in `<bindings><param name="…"><value>…</value></param></bindings>`. An empty value is written `<value/>`.
- `viewData x/y` are editor coordinates and have no effect on runtime. Every brick in the references has them, so generated bricks get them too. **CONFIRMED 2026-11-13**: generated coordinates (`tools/cpimm/build.py`, a simple left-to-right layout) import and display fine in the CPI editor (ORDERS v1.0.0).
- `gid="0"` appears on every Src and Dst brick. No other value is seen.
- Dst brick order is not schema order. In ACC, for example, `ACCOUNTGL/item` comes before `ACCOUNTGL`. **UNVERIFIED**: it is probably edit order, and probably does not matter.
- Attribute order inside `<brick>` is alphabetical: `context`, `fname`, `fns`, `gid`, `object_uid`, `path`, `type`. Checked across all `.mmap` files. The only combinations seen are `gid,path,type`; `context,gid,path,type`; `gid,object_uid,path,type`; `context,gid,object_uid,path,type`; `fname,fns,type`; `fname,fns,object_uid,type`; and `object_uid` alone.
- Every Dst brick ends with `<group/>` or `<group object_uid="gN"/>` (§3.7).

### 3.2 Direct field mapping
Source: MAT `/SAPMasterData/Id`.
```xml
<brick gid="0" path="/SAPMasterData/Id" type="Dst"><viewData x="152" y="33"/><arg><brick gid="0" path="/ns3:ProductMDMBulkReplicateRequestMessage/ProductMDMReplicateRequestMessage/Product/ProductInternalID" type="Src"><viewData x="30" y="33"/></brick></arg><group/></brick>
```
- Structure (parent) nodes are mapped as well:
  - Either to a source node, e.g. ACC `/ns0:BAPI_ACC_DOCUMENT_POST/ACCOUNTGL/item` ← `/root/invoice/codingLines`.
  - Or to an **empty constant**, which creates the node once, e.g. MAT `/SAPMasterData/Plants` and ACC `.../ACCOUNTGL`, `.../DOCUMENTHEADER`.

### 3.3 Constants
Source: MAT `/SAPMasterData/ObjectType`, ACC `.../DOCUMENTHEADER/OBJ_TYPE`.
```xml
<brick fname="const" fns="dflt" type="Func"><viewData x="30" y="33"/><bindings><param name="value"><value>Material</value></param></bindings></brick>
```
- An empty constant is `<value/>`.
- XML-special characters are escaped, e.g. `Design &amp; Plan` in MAT FixValues.

### 3.4 Standard functions (`fns="dflt"`)
Every standard function seen, with its parameters. An input count comes from the pins observed.

| fname | inputs (pins) | `<param>` names (example values) | Source |
|---|---|---|---|
| `const` | 0 | `value` | all |
| `getProperty` | 1 (const with property name) | — | MAT (`SAP_MessageProcessingLogID`), ACC (`DocumentType`), CLF (`SNDPOR`…) |
| `concat` | 2 | `delimeter` (sic, e.g. `_`) | ACC |
| `substring` | 1 | `start` `0`, `count` `10` | ACC, DOC |
| `toUpperCase` | 1 | — | MAT, DOC |
| `trim` | 1 | — | INV, JDBC, SUP |
| `getHeader` | 1 (const with header name, e.g. `targetPartnerId`) | — | FLAT |
| `mul` | 2 | — | JE |
| `isNil` | 1 | — | SUP (`not(isNil(x))` as a condition) |
| `length` | 1 | — | DOC |
| `replaceString` | 3 | — | ACC, INV, DOC |
| `indexOf2` | 2 | — | INV |
| `startWith2` | 2 | — | ACC, INV |
| `stringEquals` | 2 | — | MAT, ACC, INV, DOC |
| `greater`, `less` | 2 | — | INV, DOC / ACC, INV |
| `and`, `or` | 2 | — | ACC, INV |
| `not` | 1 | — | ACC, INV |
| `sum` | 1 (sums all values of the context) | — | ACC, INV |
| `sub`, `div` | 2 | — | ACC / `MapTaxBaseAmount.mmap` (I0115) |
| `neg` | 1 | — | ACC, INV |
| `formatNumber` | 1 | `nformat` `0000000000`, `separator` `.` | ACC, INV |
| `formatNumber` with `#` | 1 | `nformat` `#`, `separator` `.`: **removes leading zeros** from a numeric value (`00010` → `10`). **CONFIRMED** in the user's CPI edit of the ORDERS mapping (POSEX → LineNo, 2026-11-13). The user's rule: use it whenever the source is always numeric. | ORDERS feedback |
| `formatNumber` with `0.###` | 1 | removes trailing zero decimals (`432.000` → `432`). **CONFIRMED**: the ORDERS v1.0.0 output matched the sample. | ORDERS |
| `count` | 1 | none (no `<bindings>`): the number of values in the input's context. **CONFIRMED** in the user's CPI edit: `count(POSEX [context /ORDERS02/IDOC])` → NumberOfLineItems. | ORDERS feedback |
| `counter` | 0 | `ini`, `inc` | ACC, INV |
| `CopyValue` | 1 | `nnumber` `0` | ACC, INV, DOC. **User rule (2026-11-15):** a header value on every item (e.g. PO number → E1EDP02/BELNR) is `CopyValue(value, 0)`, not `useOneAsMany`. **CONFIRMED** in ORDRSP v1.0.3/v1.0.4 (BELNR on every item, also when the source queue is `removeContexts(ifWithoutElse(…))`). |
| `mapWithDefault` | 1 | `default_value` | ACC, INV |
| `TransformDate` | 1 | `iform` `yyyy-MM-dd`, `oform` `yyyyMMdd`, `calend` (`<calend_props><fd>1</fd><md>1</md><le>true</le></calend_props>`) | INV |
| `currentDate` | 0 | `oform` `yyyyMMdd`, `calend` (same calend_props) | CLF |
| `iF`, `iFS`, `ifWithoutElse`, `ifSWithoutElse`, `createIf` | see §3.5 | | |
| `removeContexts`, `collapseContexts`, `SplitByValue`, `useOneAsMany`, `formatByExample` | see §3.6 | | |
| `FixValues`, `valuemap` | see §3.10 | | |

- **`replaceString`** pins: 0 = input string, 1 = text to find, 2 = replacement. **CONFIRMED by user 2026-11-13** on DOC target OBJKY: if Type = BOM, then `toUpperCase(replaceString(TechnicalId, "-", ""))`, else TechnicalId.
- For other multi-input functions, check a reference brick before use.

### 3.5 If / else
- **`iF` / `iFS`** (if-then-else), seen in ACC `.../ACCOUNTGL/item/GL_ACCOUNT` (iFS) and INV (iF):
  - pin 0 = **then** value
  - pin 1 = **condition**
  - pin 2 = **else** value

  Example (ACC): `iFS(const "0000649100", stringEquals(dimension1,"UnplDelCosts"), formatNumber(dimension1))`.
  **CONFIRMED by user 2026-11-13**: the pin order is then, condition, else. If dimension1 = `UnplDelCosts`, the target gets the constant `0000649100`; otherwise it gets dimension1 formatted with `0000000000`.
  Still **UNVERIFIED**: the difference between `iF` and `iFS`. Probably `iFS` is the "keep context changes" variant.
- **`ifWithoutElse`**: pin 0 = **condition**, pin 1 = **then**, plus `<param name="keepss"><value>false</value></param>`. Source: MAT `/SAPMasterData/LongText`. **CONFIRMED by user 2026-11-13** (condition, then): if TypeCode = `GRUN`, concatenate all `SAPScriptLineText` values of that text into one field with the UDF `concatText`. **UNVERIFIED** what `keepss` means.
- **`ifSWithoutElse`** has the same pins and `keepss` param as `ifWithoutElse`. Source: SUP, e.g. `ifSWithoutElse(not(isNil(CashDiscountTermsCode)), CashDiscountTermsCode)`. **UNVERIFIED**: probably the "keep context changes" variant, by analogy with `iF`/`iFS`.
- **`createIf`**: 1 input (a boolean), used on structure nodes to create the node only when true. Source: ACC `.../ACCOUNTTAX/item` and `item[2]`.
  - **User convention (2026-11-13):** container ("tag") nodes come from an **empty constant**, or `createIf(condition)` when the node is optional. An element that carries its own value (simple content with attributes, e.g. `Reference`, `PartyId`) is **not** a tag and keeps its source value.
  - **`createIf` on a repeating condition needs `removeContexts` after it.** A condition on a repeating source (e.g. `Reference/@Type = 'CO'`, one value per Reference) has one context per occurrence; a target that occurs once only reads the first context. ORDRSP v1.0.3: `createIf(Reference/@Type = 'CO')` read only the first Reference (`ZLG`, false) and E1EDK02 was missing. **CONFIRMED 2026-11-15** (user's fix).
  - **User rule (2026-11-15):** a segment built with `createIf` (+ `removeContexts`) gets **straight maps** for its fields. Never combine `createIf` on the segment with `ifWithoutElse` on its fields (context problems). Otherwise build the segment **and** its fields from one filtered value chain: `ifWithoutElse(condition, value)` → `removeContexts` → `SplitByValue(Each Value)`, with the segment fed from the same chain.
  - **Optional item segments** (one per item, e.g. E1EDP03, E1EDP19): use that filtered value chain, **not** `createIf` on a per-child condition. Its SUPPRESS values hid the segments of other items (ORDRSP v1.0.2 → v1.0.3, user's queue screenshot). **CONFIRMED 2026-11-15**.

### 3.6 Context handling
- **`removeContexts`** (1 input): ACC, e.g. `removeContexts(/root/invoice/taxLines/taxCode)`.
- **`collapseContexts`** (1 input): ACC, INV.
- **`SplitByValue`** (1 input) with `<param name="type">`. **CONFIRMED by user 2026-11-13** from the CPI UI:
  - `0` = **Each Value**
  - `1` = **Empty Value**
  - `2` = **Value Change**

  Examples:
  - ACC TAX_CODE: `removeContexts` → SplitByValue(**2**, Value Change) → `collapseContexts` → SplitByValue(**0**, Each Value).
  - CLF `E1AUSPM/ATWRT`: SplitByValue(0, Each Value).
- **`useOneAsMany`** (3 inputs): pin 0 = value, pin 1 = repeat source, pin 2 = context source. Pins 1 and 2 often point to the same shared Src (`object_uid`). Sources: INV, CLF `/DocumentInfoRecordUpdateRequest/Characteristics/Characteristic/...`.
- **`formatByExample`** (2 inputs): ACC, INV.
- **Context of a source field** is the `context="{ancestor path}"` attribute on a Src brick. It sets the context to that ancestor (right-click → Context). Examples:
  - MAT: `<brick context="/ns3:…/Product" gid="0" path="/ns3:…/Product/Plant/PlantID" type="Src">`
  - INV: `context="/root/invoice"` on `/root/invoice/poLines/lineNumber`.
  - Without the attribute the source keeps its default parent context.
- **`mapWithDefault` after a context change does not fill the gaps.** **CONFIRMED 2026-11-13** in the user's ORDRSP v1.0.0 simulation. `context=Item` on `Property/PropertyText`, then `mapWithDefault`: the missing values were not added, the queues drifted apart, and no item was created.
  - The user's fix in CPI is to apply `mapWithDefault` in the field's own context first, then `formatByExample`.
- **Qualifier filter on repeating children (user's PO pattern, confirmed working in CPI on ORDRSP v1.0.1):**
  - Item node: `removeContexts(ifWithoutElse(condition, const ""))`
  - Item value: `ifWithoutElse(stringEquals(mapWithDefault(@Type), 'X'), mapWithDefault(value))` → `removeContexts` → `SplitByValue(Each Value)`
  - It assumes exactly one matching value per item.
- **Context of an attribute.** An attribute's default context is **its own element**. **CONFIRMED 2026-11-15** (user's CPI fix, ORDRSP v1.0.4):
  - Attribute compared with a **child** element (`Quantity/@Type` + `Quantity/QuantityValue`, `Reference/@Type` + `Reference/RefNo`): both are in the element's context and line up. **No context setting.**
  - Attribute compared with its **own element's value** (`Date/@Type`, `Date/@Format` vs `Date`; `AddArticleNo/@Type` vs `AddArticleNo`): the value sits in the **parent's** context. Set the attribute's `context` to the parent (e.g. `…/Item`), otherwise conditions pair with the wrong values.
  - A misaligned chain can still give the right **segment count** (a segment only counts values) while the **field values** are wrong (ORDRSP E1EDP03 v1.0.4 → v1.0.5). Feed a segment and its fields from the same aligned chain.
- **Functions on a queue run on all its values**, including those that a later `ifWithoutElse` filters out. Example: `substring(Date, 9, 8)` placed *before* the filter failed on a 6-character week date (ORDRSP v1.0.1, user's simulation). Value transforms that can fail (`substring` and the like) go **after** the filter. The failure is CONFIRMED; the explanation is my analysis.

### 3.7 Shared nodes and groups
- **Shared brick (one output feeding many inputs)**: the first use carries `object_uid="rN"` and the full content. Later uses are just `<brick object_uid="rN"/>`.
  - ACC: `<brick gid="0" object_uid="r17" path="/root/invoice/codingLines/dimensions/dimension1" type="Src">`, later `<arg><brick object_uid="r17"/></arg>`.
  - The same works for Func bricks, e.g. `collapseContexts … object_uid="r39"` in ACC.
  - References can cross Dst bricks, e.g. ACC `r308` used for `CUSTOMERCPD/CITY`, `NAME` and `POSTL_CODE`.
- **Group**: `<group object_uid="gN"/>` replaces `<group/>` on every Dst brick of a set edited together in one editor. Those are typically targets that share bricks, e.g. ACC `g21` on the CUSTOMERCPD fields that share `r308`.
- Numbering: `rN` and `gN` both run upward through the file in document order (ACC: r6, r17, r30 … and g0, g1, g2 …). They are separate counters, and the numbers are not contiguous. **CONFIRMED 2026-11-13: only uniqueness matters.** The ORDERS build numbers them r0, r1, … and g0, g1, …, and it imported and ran.
- **Rules found across all 13 standard references (65 of 65 cases, toolkit check):**
  - A brick gets an `object_uid` **only when it is reused**. No uid is ever left unreferenced.
  - Targets that share a brick always carry the **same** `<group object_uid="gN"/>`.
  - Groups exist **only** for that: there are no groups with a single target.
- **Dst-level `from`**: a target can take output *n* of a multi-output UDF directly with `<arg from="n">` on the Dst brick's own `arg` (ACC, ACC_OTM, INV, JE, SUP).

### 3.8 Duplicate subtree
Source: ACC (README: "Duplicate Subtree").

- Copies of a repeating target node use an index in the path:
  - the original stays `/ns0:BAPI_ACC_DOCUMENT_POST/ACCOUNTTAX/item`
  - the copies are `.../ACCOUNTTAX/item[1]` and `.../ACCOUNTTAX/item[2]`
  - children follow the same index, e.g. `.../item[2]/TAX_CODE` and `.../item[2]/COND_KEY`
- Also seen in:
  - DIR: `.../to_DocDesc/A_DocumentInfoRecordDescType[1]/...`
  - JE: `.../JournalEntry/ProductTaxItem[1]/...` and `ProductTaxItem[2]/...`, a SOAP sub-node
  - SUP: `/__$$RoOt_ArRaY$$__/externalSystemMetadata[1]/name`, inside a **JSON** target. The same index syntax works for JSON arrays.
- Each copy gets its own Dst brick for the node, usually `createIf` or a constant, and for each child.
- No other declaration of the duplicate exists anywhere in the file: `ViewState` and `pcont` are empty. **CONFIRMED 2026-11-13: nothing else is needed.** The ORDERS build uses `Reference[1]`/`[2]`, `Party[1]`/`[2]` and `PartyId[1]` with no other declaration, and CPI shows them as duplicated nodes (user screenshot) and produced the expected output.

### 3.9 Disabled target fields
Source: ACC, 28 cases, e.g. `.../CUSTOMERCPD/TAX_CATEGORY`.
```xml
<brick gid="0" path="..." type="Dst"><viewData x="0" y="0"/><group/><properties><property name="switchedOff">true</property></properties></brick>
```
- A disabled field has no `<arg>`, and `<properties>` comes after `<group/>`.

### 3.10 Groovy UDFs
Sources: MAT (`concatText`), ACC (5 scripts), INV (8 scripts), DIR (`DetemineText`).

- **Script location**: `script/<File>.groovy` in the zip. The `.mmap` refers to it as `src/main/resources/script`.
- **Declaration 1**, in `generic/lnks`: one `lnkRole` per script, numbered `kpos="1"`, `kpos="2"` …
  ```xml
  <lnkRole kpos="1" role="UsedFuncLib"><lnk rMode="R"><key typeID="gsh" version="1.1"><elem>concatText.groovy</elem><elem>src/main/resources/script</elem></key></lnk></lnkRole>
  ```
- **Declaration 2**, in `libstorage`:
  - First, the fixed empty `<entry name="usernamespace">` block. Copy it verbatim from MAT; it is identical in every file.
  - Then one entry per script, where the name is the script file name without `.groovy`, and `pos` matches `kpos`:
  ```xml
  <entry name="concatText"><libref><ref pos="1" role="UsedFuncLib"><key><key typeID="gsh" version="1.1"><elem>concatText.groovy</elem><elem>src/main/resources/script</elem><elem/><elem/><elem/></key></key><functions/></ref></libref></entry>
  ```
  Note that this `key` has 3 extra empty `<elem/>` and a nested `<key><key …>`. A mapping without UDFs has only the `usernamespace` entry (CLF, DOC).
- **Stale script declarations in exports**: an export can declare scripts in `lnks` and `libstorage` whose `.groovy` file is **not** in the zip.
  - JE declares 26 scripts but ships 17. The missing ones include `GetDocumentType` and `sumTaxes`.
  - SUP declares 7 but ships 5. `concatNames` and `concatnames` are missing.
  - Every missing script has zero calls (no `fns="<name>"`). Some shipped scripts are also never called, e.g. JE `formatnumber` and `Maptaxcodes`.
  - **Build rule**: generated mappings declare only scripts that are called, and every declared script is in `script/`. Do not copy stale declarations.
- **Calling a UDF**: `fname` = the Groovy function name and `fns` = the script name (file name without `.groovy`).
  - MAT: `fname="concatText" fns="concatText"`.
  - ACC: `fname="checkAndCalcTaxBaseAmount" fns="calculateTaxBaseAmount"`, and `fname="getDateDiff" fns="countTaxItem"`.
  - One script can hold several functions.
- **Array (context) UDFs**: a Groovy signature with `String[]` inputs and an `Output` parameter. The brick carries `<bindings><param name="context"><value/></param></bindings>`.
  - MAT `concatText(String[] is, Output output, MappingContext context)`.
  - INV `getConnectedValue(String[] sourceValue, String[] relatedValue, String[] requiredValue, Output output, MappingContext context)`, pins 0–2.
- **Single-value UDFs** (`def String f(String a, …)`) have **no** `context` binding.
  - ACC `determineVATDate(companyCode, VATDate, invoiceDate, finalBookingDate, receivedDate)`, pins 0–4.
  - `splitString(String, int, String)`.
- **Multi-output UDFs**: several `Output` parameters.
  - ACC `splitStringOTV(String[] is, Output Name, Output City, Output PostalCode, …)`.
  - The output is picked on the consuming `arg` with `from="n"`: `<arg from="1"><brick fname="splitStringOTV" … object_uid="r308">` for CITY, and `<arg from="2"><brick object_uid="r308"/>` for POSTL_CODE.
  - Output 0 uses a plain `<arg>` (NAME).
  - **CONFIRMED by user 2026-11-13**: outputs are numbered from 0 in Output-parameter order. ACC: Name = 0 → NAME (plain `<arg>`), City = 1 → CITY, PostalCode = 2 → POSTL_CODE.
- **Script conventions**:
  - Imports are `import com.sap.it.api.mapping.*` (most scripts) or `Output` and `MappingContext` imported one by one (MAT).
  - Most scripts keep SAP's commented template header (`customFunc1`/`custFunc2`), e.g. INV `splitString.groovy`.
  - The value-mapping API is used from a mapping UDF as `ITApiFactory.getApi(ValueMappingApi.class, null)`, in `MapToRFC_BAPI_ACC_DOCUMENT_POST/script/calculateTaxBaseAmount.groovy`. Some I0115 step scripts use it too, e.g. `NonDeductibleTaxLogic.groovy`.
  - `paymentBlock.gsh` in I0115 shows `.gsh` is also used as a script extension. It is not referenced from a mapping. **UNVERIFIED**.
- **NOT COVERED**: Java UDFs and `init`/`cleanup`/`globals` code. Those parts of `usernamespace` are always empty.

### 3.11 Value mapping and fixed values
- **`valuemap`**, a lookup against a Value Mapping artifact. Source: ACC `.../ACCOUNTTAX/item` (the `createIf` chain).
  ```xml
  <brick fname="valuemap" fns="dflt" type="Func"><viewData/><arg>{input}</arg><bindings>
    <param name="srcns"><value>newInterfaceFunction</value></param>
    <param name="srctype"><value/></param><param name="dstns"><value/></param><param name="dsttype"><value/></param>
    <param name="context"><value>http://sap.com/xi/XI</value></param>
    <param name="agency1"><value>GSAP_TaxCode</value></param><param name="schema1"><value>TaxCode</value></param>
    <param name="agency2"><value>GSAP_AccountKey</value></param><param name="schema2"><value>AccountKey</value></param>
    <param name="vmstrategy"><value>1</value></param>
    <param name="vmdefault"><value>NF</value></param>
  </bindings></brick>
  ```
  - agency1/schema1 = source agency/identifier; agency2/schema2 = target. Values seen: `GSAP_TaxCode`/`TaxCode` → `GSAP_AccountKey`/`AccountKey` and `GSAP_AccountKeyConditionKey`/`AccountKeyConditionKey`.
  - `srcns=newInterfaceFunction` and `context=http://sap.com/xi/XI` are the same in all 6 uses in ACC.
  - `vmstrategy` `1` = **Use Default Value** with `vmdefault` as the default. **CONFIRMED by user 2026-11-13** on ACC `ACCOUNTTAX/item`, where default `NF` means "create the item only if a value is found".
  - Values seen across the references: ACC 6× `1`/`NF`; JE 7× `1`/`N/A`, 3× `1`/empty, 1× `1`/`1`, 1× `1`/`NF`; SUP 1× `2`/empty. Meaning of `0` and `2` for valuemap: see the open question in §5.
- **`FixValues`**, an inline key→value table. Sources: MAT `/SAPMasterData/Status/Description`, ACC TAX_CODE, DOC.
  ```xml
  <bindings><param name="vmdefault"><value/></param><param name="vmstrategy"><value>2</value></param>
  <param name="table"><value><properties><property name="01">Design</property><property name="02">Design &amp; Plan</property></properties></value></param></bindings>
  ```
  - `vmstrategy` `2` with an empty `vmdefault` = **"Use Key"** (value not in the table → the input passes unchanged). **CONFIRMED 2026-11-15**: user's MENEE rule M → MTR (ORDRSP v1.0.3), and the user's earlier statement that MAT `Status/Description` (`2`/empty) is "Use Key" in the UI.
  - `vmstrategy` `1` + `vmdefault` = "Use Default Value" (ORDERS VM tables, imported and working).
- **NOT COVERED**: the Value Mapping artifact itself (`value_mapping.xml` etc.). No export exists in the references, and the I0115 MANIFEST shows only `scriptcollection.UTIL_GetValueMapping`.

---

## 3.12 What a CPI export changes (from the ORDERS feedback export, 2026-11-13)
- Downloading a Message Mapping from CPI gives the same layout as §1.1: `mapping/`, `script/`, `xsd/`.
- The `.mmap` came back in the standard envelope (the toolkit reads it back byte-identically). Groovy scripts came back unchanged.
- **XSDs are re-serialized:**
  - attributes reordered
  - CDATA sections unwrapped
  - the prolog joined to the first line

  The structure (all paths) is identical. Builds keep the user's original XSD files; compare a feedback export by paths, not bytes.

## 4. How iFlows reference mappings
Sources: `I2052/src/main/resources/scenarioflows/integrationflow/*.iflw`, `I0115/.../*.iflw`.

- A Message Mapping step is a `bpmn2:callActivity` with these `ifl:property` keys:
  - `activityType` = `Mapping`
  - `cmdVariantUri` = `ctype::FlowstepVariant/cname::MessageMapping/version::1.3.1`
  - `mappingType` = `MessageMapping`
  - `mappinguri` = `dir://mmap/src/main/resources/mapping/Map_SmarTeam_MSAP_DIR_DOCMAS05.mmap`
  - `mappingname` = `Map_SmarTeam_MSAP_DIR_DOCMAS05`
  - `mappingpath` = `src/main/resources/mapping/Map_SmarTeam_MSAP_DIR_DOCMAS05` (no extension)
  - `mappingReference` = `static`
- XSLT steps (I0115) use `mappinguri=dir://mapping/xslt/src/main/resources/mapping/<file>.xslt` and `mappingSource=mappingSrcIflow`.
- Every mapping in the references is a **local iFlow resource**. No step points to a separate Message Mapping artifact in the package. **NOT COVERED**: referencing a package-level Message Mapping artifact from an iFlow.

## 5. Open questions

Confirmed by the user on 2026-11-13 (now marked CONFIRMED above):
- the pin orders of `iF`/`iFS`, `ifWithoutElse` and `replaceString`
- the `SplitByValue` types
- `valuemap` `vmstrategy` 1
- multi-output `from` numbering

**Still open. Settle these with UI screenshots after the first example mapping is built.** The user knows the CPI UI, not the internal XML. Ask one item at a time, naming the mapping and field so the user can screenshot that function's settings.
1. ~~**FixValues `vmstrategy` numbers.**~~ **Settled 2026-11-15:** `2` = Use Key, `1` = Use Default Value (§3.11). Original question: the data shows `2`/empty (e.g. Material `Status/Description`, which the user says is "Use Key" in the UI) and `1`/`VST` (ACC). The user's first guess was 0 = Use Key, 1 = Default, 2 = Throw Exception, which conflicts with the data. Screenshot Material `Status/Description` and the ACC FixValues with `VST`.
2. **valuemap `vmstrategy` 2.** Seen in SUP `currencyCode` (FSAP/CountryCode → Medius/CurrencyCode). Screenshot that lookup's "if value not found" setting.
3. **`iF` vs `iFS`, and `ifWithoutElse` vs `ifSWithoutElse`.** Which UI checkbox differs (probably "Keep Context Changes")? What is `keepss` (probably "Keep Suppressed Values")?
4. **The standard function table (§3.4).** The user will check it with screenshots: text, boolean, arithmetic/format and node/date/context functions.
5. ~~File internals~~: **settled 2026-11-13** by the ORDERS v1.0.0 import (see §2.1, §3.1, §3.7, §3.8).
   - Generated `viewData`, uid/group numbering and duplicate subtrees work.
   - `AdditionalProperties` with 4 entries works. Whether it is *required* is untested and not needed.

Until these are settled, generated mappings copy the XML of a reference brick that has the same UI meaning. If the meaning is unclear, stop and ask.
