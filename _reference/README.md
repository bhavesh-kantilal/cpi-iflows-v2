# Reference exports (customer: SSAB, exported 2026-11-13)

## MapToRFC_BAPI_INCOMINGINVOICE_GETDETAIL
- Medius Invoice XML → BAPI_INCOMINGINVOICE_CREATE1 MIRO (Supplier Invoice)
- Shows: UDFs (Groovy), value mapping lookup, header/item contexts, complex UDFs, Context Handling

## MapToRFC_BAPI_ACC_DOCUMENT_POST
- Medius XML → Accounting Document
- Shows: UDFs (Groovy), value mapping lookup, header/item contexts, complex UDFs, Duplicate Subtree, Context Handling

## Map_SmarTeam_MSAP_DIR_CLFMAS02
- Custom XSD / XML to IDoc Mapping for CLFMAS.CLFMAS02
- Shows: Context Handling, Functions, etc.

## Map_SmarTeam_MSAP_DIR_DOCMAS05
- Custom XSD / XML to IDoc Mapping for DOCMAS.DOCMAS05
- Shows: Context Handling, Functions, etc.

## Map_Material_SmartTeam
- SOAP Product PRODUCTMDMBULKREPLICATEREQUEST to SmarTeam custom XSD
- Shows: Basic mapping

## CostCentertoMedius
- SOAP CostCentreReplicationBulkRequest → Medius REST API (JSON/OpenAPI), cost centres as dimension values
- Shows: JSON target (root array), Groovy UDFs, concat, iFS

## MM_MediusInvoice_To_IFSSE
- Medius Invoice to a flat file. The XML is flat and is then converted to CSV (conversion happens in the iFlow)
- Shows: flat row/field XSD target, getHeader, getProperty, TransformDate, FixValues, Groovy UDFs

## MapBPToDDSJDBC
- Business Partner SOAP is mapped to a JDBC schema with UPDATE_INSERT
- Shows: JDBC statement XSD (dbTableName/@action, table, access, key), Groovy UDF

## MapToJournalEntryRequest
- Medius Supplier Invoice is mapped to the Journal Entry API in SAP
- Shows: SOAP JournalEntryBulkCreateRequest target, custom fields namespace (ZZ1_), duplicate subtree, value mapping lookups, many Groovy UDFs

## SupplierMastertoMedius
- Business Partner SOAP is mapped to a Supplier master in Medius
- Shows: JSON target with nested arrays and duplicate subtree, isNil, ifSWithoutElse, value mapping, Groovy UDFs

---

# iFlow exports (in `iflows/`)
Whole iFlows: drop `<iFlowName>.zip` into `_reference/iflows/` and add a line here. `tools/catalog.py` links every message mapping to the iFlow steps before and after it.

## I0115_Invoice_Medius_GSAP_ProcessPostedInvoices_JMSToRFC
- Has my most complex iFlow
- Handles Medius Invoice processing and then pushes messages to subsequent flows for attachment etc.

## I2052_P_DocumentInfoRecord_Update_SmarTeam_HTTPToJMS
- Shows my parent iFlow that gets a message over HTTP and writes to JMS -> Common JMS Queue
- Most of my iFlows will follow this _P_ notation for Parent flows

## I0701_P_JMSDispatcher_MSAP_PlantMaintenance
- Shows my JMS Dispatcher that reads messages from JMS queue (written by above parent flow)
- Routes to below PD flow I2052_DocumentInfoRecord_Update_DOCMAS05_CLFMAS02_SmarTeam_MSAP_PDToIDoc

## I2052_DocumentInfoRecord_Update_DOCMAS05_CLFMAS02_SmarTeam_MSAP_PDToIDoc
- Shows a simple iFlow where I get a message from my JMS Dispatcher over PD and post an IDoc over PD

---

# Generated mappings (added 2026-11-15, evidence level L3)
Built by the toolkit in this repo (`mappings/<folder>/build/`), imported and tested by the user in CPI. **Not CPI downloads**: they show what works in CPI, not how CPI itself writes a mapping (for that, the original exports above are the evidence, L1). Each has its own `spec.md` and `CHANGELOG.md` in `mappings/`.

## Map_TibnorS4_HammelinnaMetocsHub_PurchaseOrder_ORDERS02 (v1.1.1)
- Tibnor S/4 IDoc ORDERS02 → Hämeenlinna Metocs hub OrdersMessage (XSD, no namespace)
- Shows: partner/qualifier filters on IDoc segments (removeContexts(ifWithoutElse(stringEquals…))), FixValues tables with default (vmstrategy 1), container constants + createIf, duplicate subtrees (Party, Reference, PartyId), formatNumber `#` / `0.###`, count, getProperty, UDFs removezeros + cropText/hasBestText

## Map_HammelinnaMetocsHub_TibnorS4_OrderConfirmation_ORDRSP (v1.0.5)
- Hub OrdrspInterchange (namespaced XSD, qualified) → Tibnor S/4 IDoc ORDRSP/ORDERS01
- Shows: `ns0:` on every source step + namespace as 4th link elem, attribute context = Item (Date/@Type vs Date), item segments from filtered chain (ifWithoutElse → removeContexts → SplitByValue), CopyValue 0 for header→item, FixValues Use Key (vmstrategy 2), createIf + removeContexts rule, library UDF substringSafe. Contains the user's own CPI corrections (v1.0.4)

## Map_HammelinnaMetocsHub_TibnorS4_DeliveryNotice_DESADV (v1.0.1)
- Hub DeliveryBatch (namespaced XSD) → Tibnor S/4 IDoc DESADV/DELVRY01
- Shows: multi-output Groovy UDF (groupByHeat, outputs 0–6 incl. plain arg for 0), flattening with useOneAsMany(line field, SinglePart, SinglePart), TransformDate, CopyValue 0 per group

## Map_HammelinnaMetocsHub_TibnorS4_Invoice_INVOIC (v1.0.1)
- Hub Invoice (XSD, no namespace) → Tibnor S/4 IDoc INVOIC/INVOIC01 (MM)
- Shows: attribute filters with mapWithDefault (PO pattern), attribute context on AddArticleNo/@Type and DocumentId/Date/@Type, CopyValue, repeating segment from source node (E1EDK04 ← Tax), concat with delimiter, formatNumber `0000000000`

## Map_TibnorS4_NShift_TransportOrder_Book (v1.0.3)
- S/4 TM TransportationOrderRequest (WSDL, unqualified) → nShift ConsignmentWS `book` (WSDL with imports)
- Shows: WSDL target whose message ≠ element name (link elem 3 = `book`), WSDL importing XSDs by relative path `../xsd/…` with XSDs in `xsd/`, mid-path namespace prefix on leaf elements (`ns2:`), multi-output context UDF (goodsItemFlags), single-value UDF with time zones (toLocalDate), FixValues with default, div/formatNumber unit conversion
