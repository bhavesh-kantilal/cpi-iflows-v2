# Tibnor ORDERS02 → Hämeenlinna Metocs hub OrdersMessage

- **Mapping name:** `Map_TibnorS4_HammelinnaMetocsHub_PurchaseOrder_ORDERS02`
- **Spec source:** `25200_ORDERS_Tibnor-to-HameenlinnaMetocs_MappingSpec_v0.1.xlsx` (draft v0.1, 12 Nov 2026)
- **Source:** IDoc `ORDERS.ORDERS02.xsd`, root `ORDERS02` (_schema file missing_)
- **Target:** `Harmonized_Purchase_Order_0_0_7.xsd`, root `OrdersMessage`, no namespace in the sample (_schema file missing_)
- **Samples:**
  - input `Input_IDOC_0000000020247467.xml` (Tibnor OY, PO 0046540580, 1 item)
  - expected output `Output_AA_ORDERS96A_AM_20261110_1342.xml`

## How I read the sheet
- **Sheet "Mapping"** has columns `#`, `Target field`, `Occ.`, `Source`, `Target rule`, `Sample value`, `Status`, `Notes`.
  - Rows without `#` are section headings.
  - `X[@Type='CR']` means: set attribute `Type` to that constant on node X.
  - `E1EDKA1[AG]` means the E1EDKA1 segment where `PARVW = AG`.
  - `E1EDK17[QUALF=001]` means the E1EDK17 segment where `QUALF = 001`.
- **Sheet "Value Mappings"** has the VM-01/02/04 tables. **"Not Mapped"** lists IDoc data that is ignored. **"Open Points"** lists business questions.
  - I don't block on open points the spreadsheet already answers or marks "keep as today".

## Design (target → source → how)
Functions used are only those in FORMAT_NOTES.

| # | Target | Rule | Built with |
|---|---|---|---|
| 1–2 | Header/SchemaId, SchemaVersion | constants | `const` |
| 3–4 | MessageFunction, OrderType | `'105'` | `const` (OrderType: BSART NB only, OP-03) |
| 5 | InterchangeSender | VM-04 on AG-PARTN | FixValues table 0010/0310/0500 |
| 6 | InterchangeRecipient | `00372389445756` | `const` |
| 7–8 | MessageRoutingInbound/Outbound | `SSCO.M.EDI`/`HAPU.M.METOCS` + PRD/TST | `concat(const, getProperty(<env property>))`, **Q3** |
| 9–10 | DocumentNo, Reference CR | E1EDK01-BELNR | copy; `@Type` const |
| 11–12 | Reference ZZ / ZOT | `S` / `TPO` | duplicate subtree `Reference`, `Reference[1]`, `Reference[2]` |
| 13–31 | Party SE / BY | see VM tables | duplicate subtree `Party`, `Party[1]`, `Party[2]` in **sample order SE, BY, CN** |
| 14, 24, 32 | PartyId ZTI | MDM lookup (OP-21 open) | **Q4** |
| 15, 16 | BY PartyId 100, PartyName1 | VM-04 | FixValues on AG-PARTN |
| 17–20 | BY address | AB/AS fixed; OY = WE address | `iF(AG-PARTN = 0500, WE-field, FixValues(AG-PARTN))`. For AddressLine2, OY = leave out |
| 22–23 | BY Contact / CommId TE | AG-BNAME, AG-TELF1 without `-` and spaces | `replaceString` twice |
| 25–27 | SE PartyId 100, names | VM-01 (vendor 80008) | FixValues on LF-PARTN |
| 28–31 | SE address | BA partner | qualifier filter on PARVW = BA |
| 33 | CN PartyId 100 | AB/AS prefix + WE-LIFNR; none for OY | `createIf(AG-PARTN ≠ 0500)` + `concat` |
| 34–39 | CN name/address | WE partner; postal code without spaces | qualifier filter on PARVW = WE |
| 40 | Currency | `EUR`, Type 5 | `const` |
| 41–42 | TermsOfDelivery | E1EDK17 QUALF 001 LKOND / LKTEXT | qualifier filter |
| 43 | Item | one per E1EDP01 | `Item` ← E1EDP01 |
| 44 | LineNo | POSEX without leading zeros | UDF `removezeros` (copied from reference CostCentertoMedius) |
| 45 | AddArticleNo UA | E1EDP19 QUALF 001 IDTNR without leading zeros | qualifier filter + `removezeros` |
| 46 | Property 44 | first 35 chars of KTEXT, only if the item has TDID `BEST` | `substring(0,35)`; the "has BEST" test needs a small UDF, see Decisions |
| 47–48 | Quantity, MeasureUnit | MENGE without trailing zero decimals; MENEE | `formatNumber` pattern `0.###` (UNVERIFIED pattern behaviour) |
| 49 | Date Type 2 / Format 102 | first E1EDP20-EDATU | copy (first value per item) |
| 50–51 | Price AAA | VPREI, PMENE | copy |
| 52 | NumberOfLineItems | count(E1EDP01) | standard `count` is not in the references → UDF, see Decisions |

### Sample checks
The expected output for PO 0046540580 (Tibnor OY) matches the rules above:
- BY address = WE address
- no CN PartyId
- `PropertyText` = the first 35 characters of KTEXT (`…50x4x600`)
- quantity `432`

The output contains only these Party fields:
- SE: ZTI and 100 ids, Name1/Name2, AddressLine1/3, PostalCode, Country
- BY: ZTI and 100 ids, Name1, AddressLine1/3, PostalCode, Country, Contact
- CN: Name1, AddressLine1/3, PostalCode, Country (no AddressLine2, because PFACH is empty)

## Questions (blocking)
- **Q1 Schemas.** Please put `ORDERS.ORDERS02.xsd` and `Harmonized_Purchase_Order_0_0_7.xsd` in `schemas/`. Without them the mapping can't reference its structures and I can't check paths.
- **Q2 Mapping name.** Proposal: `Map_TibnorS4_MetocsHub_PurchaseOrder_ORDERS02`.
- **Q3 Environment suffix.** Which exchange property holds `PRD`/`TST`?
- **Q4 ZTI party numbers.** The MDM lookup decision (OP-21) is still open. What should the mapping do for now?

## Decisions
- **2026-11-13 Q1 Schemas.** The user is adding both XSDs.
  - `ORDERS.ORDERS02xsd` arrived; its name is missing the dot before `xsd`. All 27 source paths used are in it.
  - The target XSD is still pending.
- **2026-11-13 Q2 Name.** `Map_TibnorS4_HammelinnaMetocsHub_PurchaseOrder_ORDERS02`, as given by the user.
- **2026-11-13 Q3 Environment suffix.** The user will settle the property later. For now it's the placeholder exchange property `HubEnvironment` (constant `ENV_PROPERTY` in `build_mapping.py`).
  - `MessageRoutingInbound` = `concat("SSCO.M.EDI", getProperty("HubEnvironment"))`.
  - The iFlow must set the property, or set it in the mapping simulator when testing.
- **2026-11-13 Q4 ZTI.** Inline FixValues tables with the known GLN→ZTI pairs from the "Value Mappings" sheet.
  - BY and CN: no hit → element left out.
  - SE: fallback `0003092`, as row 24 says.
- **2026-11-13 Party order** follows the sample output (SE, BY, CN), not the spreadsheet order.
- **2026-11-13 VM-01 and VM-04** are inline FixValues tables, so no extra Value Mapping artifact is needed. They use "use default value" (vmstrategy 1). The FixValues numbering is UNVERIFIED, so check it in the editor after import.
- **2026-11-13 UDFs:**
  - `removezeros.groovy` is copied unchanged from reference CostCentertoMedius.
  - New `TibnorOrdersHelpers.groovy`:
    - `cropText(text, max)` for row 46 (35 characters). The reference `cropString` is fixed at 50.
    - `hasBestText(TDID[])` for row 46.
    - `countValues(values[])` for row 52. The standard `count` function is not in the references.
- **2026-11-13 Empty optional fields** (e.g. CN AddressLine2 when PFACH is empty) are not created. The sample output has none.
- **2026-11-13 Item Date** takes EDATU directly and assumes one E1EDP20 per item. OP-10 says all samples have one.
