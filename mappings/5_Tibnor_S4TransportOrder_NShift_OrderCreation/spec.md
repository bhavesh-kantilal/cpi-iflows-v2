# Tibnor S/4 TM freight order → nShift ConsignmentWS `book`

- **Mapping name:** `Map_TibnorS4_NShift_TransportOrder_Book`. I chose it from the pattern `Map_<Src>_<Tgt>_<Object>_<MsgType>`, because no name was given. Renaming it is one line in `build_mapping.py`.
- **Spec:** `S4TM-NShift_TransportOrder_Book_MappingSpec_v0.1.xlsx`, written by me in the layout of the user's other specs. **No source spec exists:** every rule is a best guess (user, 13 Nov 2026) from:
  - the S/4 schema
  - the nShift documentation `docs/ConsignmentWS(eng).pdf`
  - the samples
- **Process:** S/4 TM creates a freight order (transport request). CPI books it in nShift, which passes it to the carrier.
- **Method:** `book` (user), which creates a BOOKED consignment. `save` would store it unbooked.
- **Source:** `schemas/S4_TransportationOrderRequest_Out.wsdl` (byte copy of the user's `Source.wsdl`), root `TransportationOrderRequest`, namespace `http://sap.com/xi/SAPGlobal20/Global`, unqualified children. Only the root carries `ns0:`, as in MAT.
- **Target:** `schemas/NShift_ConsignmentWS.wsdl`, root element `book`, namespace `http://www.spedpoint.com/consignment/types`.
  - The user's `Target.wsdl` imports its types from `https://service.web-ta.net/ws/services/ConsignmentWS?xsd=1` and `?xsd=2`. The user approved downloading them (13 Nov 2026); they are kept unchanged in `schemas/downloaded/`.
  - `tools/wsdl_inline.py` copies them into `<types>` as separate schemas joined by namespace-only imports, the layout of the SAP WSDLs in `_reference/`.
  - `book`, `Consignment`, `Part`, `GoodsItem`, `email`, … are local unqualified elements. The leaf fields (`id`, `name`, `weight`, `date`, …) are global elements of `…/consignment/types/v1_0`, so they carry `ns2:` mid-path (FORMAT_NOTES §2.2, JE pattern). The prefixes were checked against the XSD for every target path.
- **Samples:**
  - `samples/Input.XML`: freight order 6100007031, 1 vehicle item, 5 top-level packages, 3 house waybills, 4 stops. UTF-8 with no xsi attributes, so no simulator copy is needed.
  - `samples/Output.xml`: an nShift **`save`** request from another company (Ovako, template TRE71_FCA). It shows the target XML style only, not the expected result of Input.XML.

## Design
See the Mapping sheet for all 22 rows. In short:

| Target | Source / rule |
|---|---|
| `AuthenticationToken/*` | `getProperty` NShift_UserName / NShift_GroupName / NShift_Password |
| `transactionId`, `Consignment/@orderNo` | freight order number `BaseBusinessTransactionDocumentReference/ID` |
| `Consignment/@templateName` | `getProperty` NShift_TemplateName |
| `Part` consignor / `Part[1]` consignee / `Part[2]` deliveryAddress | ShipperParty / ConsigneeParty / ShipToLocation: id, name, street + house no., postcode, city, country; Communication (phone, e-mail) only when present |
| `GoodsItem` | top-level packages: UDF `goodsItemFlags` (flag + SSCC per Item) → `removeContexts(ifWithoutElse(flag, const ""))`; values via `ifWithoutElse(flag, value)` → `removeContexts` → `SplitByValue` (PO pattern) |
| `GoodsItem` fields | pieces (no decimals), gross / net weight kg (0.00), volume hl ÷ 10 = m3, L/W/H mm ÷ 10 = cm, units kg / m3 / cm, packageType VM-01, tag + `PackageIds/code` = SSCC, notes = Description |
| `TransportProduct` | `PaymentInstruction/@value` CC → C else P; `Tod` = Incoterm + location; `Pickup/date`, `Delivery/date` = UDF `toLocalDate` |
| `Target/date` | = delivery date (required) |

### UDFs (only where no standard function does the job)
- **`scripts/goodsItemFlags.groovy`:** multi-output, context type.
  - A goods row is an item of category PKG/PRD whose parent is not PKG/PRD. That needs a parent lookup across items.
  - Output 1 returns each item's `Package/ID`. That field sits one level below Item, so pairing it with its item in standard functions would hit the queue-alignment problem from ORDRSP v1.0.0.
  - All inputs are flattened with standard functions; parent and package ids are paired with `useOneAsMany(Item/ID, node, node)`, as in DESADV.
- **`scripts/toLocalDate.groovy`:** S/4 sends UTC (`2026-11-11T22:00:00Z`). nShift wants the local calendar day without a time zone (doc 4.1.13: a time zone is recalculated to Stockholm time). The UDF converts with the location's SAP time zone code (`EET`), falling back to UTC.

### Expected result for Input.XML (Python model of the rules)
- orderNo / transactionId `6100007031`
- consignor `0005022936` Tibnor Metals Oy, Tuotekatu 3, 33840 Tampere FI
- consignee `0005007810` SUOMEN PIIPPUTUKKU OY, LÄÄNINRAJANKATU 6, 05800 HYVINKÄÄ FI
- deliveryAddress `1154` PETER TEST OY, TESTGATAN 5, 65100 VAASA FI
- 5 GoodsItems:
  - item 70 Helpall PX: 301.00 kg, 0.326 m3, 120 × 80 × 34 cm
  - items 130 / 110 / 90 / 60 Bunt BE: 456.73 / 368.56 / 228.37 / 730.01 kg
  - each with its SSCC. Total 2084.67 kg = the vehicle item's 2084.662 kg, which supports the goods-row rule.
- PaymentInstruction `P`, Tod `CPB` / HYVINKÄÄ, Pickup `2026-11-09`, Delivery and Target `2026-11-12`

## Assumptions (best guess; each one needs confirmation)
- **A1 One consignment per freight order.** The sample freight order is multi-drop: 3 house waybills, 3 unloading points, per-package consignee / ship-to. The mapping books it as ONE consignment: header consignee, header ship-to (last stop) as delivery address, all top-level packages. The likely correct design is one `book` per house waybill (iFlow split + per-HWB mapping) → OP-01.
- **A2** The freight order number is `BaseBusinessTransactionDocumentReference/ID` (TypeCode 1122).
- **A3** consignor = ShipperParty (the pickup address); ShipFromLocation is not mapped.
- **A4** Goods rows = top-level packages (or unpacked products) of the item hierarchy; noOfPackages = their pieces (1 each in the sample).
- **A5** `templateName` comes from the exchange property `NShift_TemplateName`; the template selects carrier and product. The carrier (PreferredCarrierParty DSV) is not sent.
- **A6** Credentials come from exchange properties set by the iFlow (password from a Secure Parameter, e.g. read by a script). They never sit in the mapping.
- **A7** `transactionId` = freight order number: a re-send returns the first booking (nShift dedupe). Changes would need another approach → OP-05.
- **A8** Units are always KGM, HLT and MMT in the TM output; nShift gets kg, m3 and cm (the other company's sample uses cm-like values: 620 × 20 × 20).
- **A9** Package types: Bunt → BE, Helpall → PX, other → PK (FixValues, "use default value", as ORDERS). The real codes are carrier-dependent → OP-04.
- **A10** Phone = `Telephone/Number/SubscriberID` (without country or area code), e-mail = `Email/URI`, only when present (none in the sample). No contact person in the source.
- **A11** PaymentInstruction: CC → C (collect), everything else → P (prepaid, sample `PP`).
- **A12** The Incoterm is copied as-is (the sample has `CPB`, not an Incoterms code → OP-10).
- **A13** Dates = the requested pickup / delivery start in the local time zone of the ship-from / ship-to location. Target/date = delivery date.
- **A14** WSDL links: elem 3 = the message *element* (`book`, `TransportationOrderRequest`), elem 4 = its namespace. For `book` this is **UNVERIFIED**: in all references the message and element share one name; here the message is `ConsignmentEndpoint_book` → OP-12.

## Decisions
- **2026-11-13** Use method `book` (user).
- **2026-11-13** Best-guess rules with assumptions; no mapping sheet (user).
- **2026-11-13** Download the two NShift XSDs from the WSDL import URLs and inline them into a self-contained WSDL copy (user approved). The originals `Source.wsdl` / `Target.wsdl` are kept unchanged in `schemas/`.
- **2026-11-13** Files moved: samples → `samples/`, WSDLs → `schemas/`, PDF → `docs/`.

## Import test v1.0.0 → v1.0.1 (2026-11-13)
- **User:** the WSDL was missing objects in CPI (in the mapping and when loaded by hand).
- **Cause, my bug in `tools/wsdl_inline.py`:** the downloaded XSDs refer to their own types as `tns:…`, with `tns` declared on their schema root. Moving the schema elements into the WSDL with lxml dropped that declaration, because `tns` is used only inside attribute values. So `tns` resolved to the WSDL's own `tns` (`http://www.spedpoint.com/consignment`), and all 151 type / element references inside the NShift schemas pointed to a namespace with no definitions. CPI showed `book` with nothing below it.
  - The path check did not catch it, because it matches types by local name only.
- **Fix:**
  - `wsdl_inline.py` splices the schemas in as text, keeping each schema root's own `xmlns:tns`. Before writing, it compiles the merged schema set; the compile rejects the old file and accepts the new one.
  - New build check `schema_ref_errors` in `tools/cpimm/check.py`: every `type=` / `ref=` / `base=` reference in a zip's XSD or WSDL must resolve to a definition in its namespace. It passes on every reference and mapping schema and reports the 151 errors in the v1.0.0 zip.
- The mapping logic is unchanged.
- **User, 2026-11-13: v1.0.1 "works".** Adding the new check to the CLAUDE.md build-check list waits for the user's review (`REVIEW.md` A1).

## Test 2026-11-15: XSDs as separate resources instead of inlined (user's question)
The user remembers that CPI resolves a WSDL's imports when the XSDs are imported into the same mapping, so no inlined copy would be needed. Two test variants, with the same mapping logic as v1.0.2, built with `py -I build_mapping.py --wsdl-import-test` into `build/test_wsdl_import/`:
- **TestA** `…_Book_TestA.zip`: the user's `Target.wsdl` byte for byte (`schemas/NShift_ConsignmentWS_urlimport.wsdl`). Its imports still point to `https://service.web-ta.net/…?xsd=1/2`. This tests whether CPI matches the imported XSDs **by namespace**.
- **TestB** `…_Book_TestB.zip`: the same WSDL with only the two `schemaLocation` values changed to the file names `ConsignmentWS_xsd1.xsd` / `ConsignmentWS_xsd2.xsd` (`schemas/NShift_ConsignmentWS_fileimport.wsdl`). This tests whether CPI matches them **by file name**. Offline, the WSDL schema compiles together with the two XSDs next to it.
- Both zips contain no XSD. The XSDs to import are `build/test_wsdl_import/xsd_to_import/ConsignmentWS_xsd1.xsd` and `…xsd2.xsd`, unchanged from the download.
- Build checks: everything passes except the expected 5 unresolved type references per zip (the types are in the XSDs that are imported in CPI).
- **Result (user's CPI test, 2026-11-15): neither works.**
  - **TestA:** imports, but the `book` structure below AuthenticationToken / Consignment stays orange (unresolved), and the simulation is not possible.
  - **TestB:** the same.
  - Selecting either WSDL by hand as the target message fails with `Cannot import file 'NShift_ConsignmentWS_fileimport.wsdl'; XSD: Type reference 'http://www.spedpoint.com/consignment/types/v1_0#Consignment' is unresolved` (and the same for AuthenticationToken, Error, GoodsItem, ServiceException …). The URL-import WSDL gives the same error.
  - **Conclusion:** CPI reads a WSDL on its own. It does not follow `schemaLocation` to the internet address, nor to a file name, nor to XSDs imported into the same mapping. The types must be inside the WSDL, as in the inlined `NShift_ConsignmentWS.wsdl` (v1.0.1/v1.0.2, working). The rule in CLAUDE.md / FORMAT_NOTES §1.1 stays.
  - Not tested yet: a WSDL and its XSDs uploaded together as one archive, or a `schemaLocation` path into CPI's `xsd/` folder (`../xsd/…`).

### Follow-up test 2026-11-15 (user: try both before ruling anything out)
Same build command, more output in `build/test_wsdl_import/`:
- **TestC** `…_Book_TestC.zip` (one archive): the WSDL with file-name imports (as TestB) **plus both XSDs in the same `wsdl/` folder** of the mapping zip. The WSDL and its XSDs reach CPI together, side by side (an XSD in `wsdl/` is seen in reference DIR).
- **upload_archive_NShift_ConsignmentWS_with_xsds.zip**: only the WSDL (file-name imports) and the two XSDs, flat, for a manual upload in "Add target message", if CPI accepts an archive there.
- **TestD** `…_Book_TestD.zip` (schemaLocation path): the WSDL imports `../xsd/ConsignmentWS_xsd1.xsd` / `…xsd2.xsd` (`schemas/NShift_ConsignmentWS_xsdpathimport.wsdl`), and the XSDs are inside the zip in `xsd/`, CPI's XSD resource folder. No manual step.
- **Result (user's CPI test, 2026-11-15): TestC works, TestD works.** The full `book` structure loads (AuthenticationToken, Consignment, transactionId). The manual upload archive was not tried (user: not needed).
  - The three WSDLs differ **only** in the two `schemaLocation` values (lines 6–7). Everything else is byte-identical to the user's `Target.wsdl`:
    - original: `https://service.web-ta.net/ws/services/ConsignmentWS?xsd=1` / `?xsd=2`
    - TestB/C: `ConsignmentWS_xsd1.xsd` / `ConsignmentWS_xsd2.xsd`
    - TestD: `../xsd/ConsignmentWS_xsd1.xsd` / `../xsd/ConsignmentWS_xsd2.xsd`
  - **What it shows:** CPI resolves `schemaLocation` as a **relative file path from the WSDL's own folder** (`wsdl/`); it does not fetch URLs and does not search by namespace.
    - TestB and TestC use the same WSDL. B failed because the XSDs imported by hand landed in CPI's `xsd/` folder, not next to the WSDL. C works because the XSDs are in `wsdl/`.
    - TestD works because `../xsd/` points from `wsdl/` to the `xsd/` folder.
  - So there are three working options: inline the XSDs into the WSDL (v1.0.2), XSDs next to the WSDL with file-name imports (C), or XSDs in `xsd/` with `../xsd/` imports (D). In C and D the original XSD files stay unchanged and only two attribute values in the WSDL change.
- **Decision 2026-11-15 (user): TestD is the default.** NShift v1.0.3 uses it: the WSDL keeps its imports, as `../xsd/` paths, and the XSDs sit in `xsd/`. The inlined WSDL is no longer used. `tools/wsdl_inline.py` stays available as the alternative. Rule in CLAUDE.md and FORMAT_NOTES §1.1.
