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
