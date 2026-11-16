# Tibnor ORDERS02 → Raahe Tilkku hub OrdersMessage

- **Mapping name:** `Map_TibnorS4_RaaheTilkkuHub_PurchaseOrder_ORDERS02` (user, 2026-11-16)
- **Interface:** 1002129 – Tibnor SSABEuropeRaaheTilkku [80067] EDI ORDERS out. No iFlow known (mapping only, user 2026-11-16).
- **Spec source:** `1002129_ORDERS_Tibnor-to-RaaheTilkku_MappingSpec_v0.1.xlsx` (draft v0.1, 16 Nov 2026). The Hämeenlinna Tilkku spec 1002249 has the same rules except Property ZMA.
- **Source:** `schemas/ORDERS.ORDERS02.xsd`, root `ORDERS02` (copied from the Metocs ORDERS mapping)
- **Target:** `schemas/Harmonized_Purchase_Order_0_0_7.xsd`, root `OrdersMessage` (copied from the Metocs ORDERS mapping)
- **Shared logic:** `build_mapping.py` holds `build(mill)`. The Hämeenlinna Tilkku mapping (`mappings/10_ORDERS_Tibnor-to-HameenlinnaTilkku/`) calls it with its own VM-01 values and without ZMA.
- **Reference:** `reference/PO-Mapping_ORDERS93A_TIBNOR_to_PurchaseOrder.txt` (today's PO mapping EDI → hub)
- **Samples:** 5 sets in `samples/<date>_<PO>/` (input IDoc, Implema EDI, expected hub output).
  - The input IDocs are Windows-1252 without an encoding declaration. Simulator copies: `Input_IDOC_*_utf8.xml`.
  - Two originals are **not well-formed XML**: a raw `<` in VALUE_TXT (`T<51mm…`, PO 46540739 and 46541012) and a raw `&` (PO 46541012). The `_utf8` copies escape them (`&lt;`, `&amp;`); the originals are unchanged.

## How I read the sheet
Sheet "Mapping": `#`, `Target field`, `Occ.`, `Source`, `Target rule`, `Sample value`, `Status`, `Notes`. Rows without `#` are headings. `X[@Type='CO']` = the occurrence of X with that attribute. "Value Mappings" VM-01 (per mill), VM-04 (per Tibnor company), VM-05 (price basis). "Open Points" OP-01 … OP-16.

## Design (target ← source, how)
| # | Target | Built with |
|---|---|---|
| 1–3 | SchemaId, SchemaVersion, MessageFunction | constants `EDI.ORDER`, `Harmonized_Purchase_Order_0_0_7.xsd`, `9` |
| 4 | OrderType | `ifWithoutElse(BSART = 'NB', '105')` (OP-03: other types unknown, left out) |
| 5 | InterchangeSender | FixValues VM-04 on E1EDKA1[AG]-PARTN (0010/0310/0500) |
| 6, 8 | InterchangeRecipient, MessageRoutingOutbound | FixValues VM-01 on E1EDKA1[LF]-PARTN, **this mill's row only** (`0000080067` → `00372389445741` / `RAMF.M.TILKKU`); routing + `getProperty("HubEnvironment")` |
| 7 | MessageRoutingInbound | `concat('SSCO.M.EDI', getProperty("HubEnvironment"))` |
| 9, 11 | DocumentNo, Reference CR | `formatNumber(BELNR, '#')` |
| 10, 12 | DocumentId/Date (4/102), Date (137/102) | E1EDK03 IDDAT 012 DATUM (qualifier pattern) |
| 13–17 | Party BY = `Party` | PartyId ZZZ = FixValues VM-04 (0100/0300/0500); NAME1; `Contact` ← `createIf(BNAME ≠ '')`, ContactName `trim(BNAME)`, CommId TE = TELF1 as it is |
| 18–19 | Party MF = `Party[1]` | `formatNumber(LF-PARTN, '#')` |
| 20–25 | Party CN = `Party[2]` | PartyId `formatNumber(mapWithDefault(WE-PARNR, '0'), '#')`; NAME1; STRAS; PFACH only when not empty; AddressLine3 = `concat(substring(concat(PSTLZ, 8 spaces), 0, 8), toUpperCase(ORT01))` |
| 26 | Currency 5 | E1EDK01-CURCY |
| 27–28 | TermsOfDelivery 6 / Location 1 | as Metocs: `createIf` + straight maps, E1EDK17 QUALF 001 |
| 29–31 | Item, LineNo, ArticleNo IN | Item ← E1EDP01; `formatNumber(POSEX, '#')`; `removezeros(E1EDP19[QUALF 001]-IDTNR)` (context E1EDP01) |
| 32 | `Property` (44) | `hasBestText(TDID [ctx E1EDP01])` → `trim(substringSafe(KTEXT 001, 0, 35))`, same value in Code and Text |
| 33–44 | `Property[1]` … `Property[14]` | UDF `itemCharacteristic` per characteristic (see below), order ZPF, ZTY, 12, 1, 53, 8, 35 BT, 35 TP, 17 BT, 17 TP, 59, ZPI, ZED, ZMA |
| 45–48 | `Measurement` … `[3]` LN/WD/TH/ID | `itemCharacteristic` VALUE → `formatNumber '0.##'`, unit `MMT` |
| 49–50 | `Quantity` 21 | container constant; `formatNumber(MENGE, '0.###')`; MENEE |
| 51–54 | `Quantity[1]` LL | only when MAX_COILWEIGHT exists: MAX_PACK_WEIGHT, KGM, MIN_COILWEIGHT, MAX_COILWEIGHT |
| 55 | Item/Date 2/102 | E1EDP20-EDATU (one E1EDP20 per item, OP-08) |
| 56–57 | Price AAA | container constant; VPREI; `iF('PT', PMENE = TNE or (PMENE = KGM and PEINH = 1000), PMENE)` (VM-05) |
| 58 | Item/Reference CR | `concat(CopyValue(order no, 0), IDTNR, ' ')` |
| 59–60 | Package | only when SSAB_PC exists: VALUE (CodeSet 92), VALUE_TXT |
| 61–64 | Item/Party CN | header CN values with `CopyValue(…, 0)`; City = header AddressLine3 value |
| 65 | NumberOfLineItems | `count(POSEX [context IDOC])` |

### Item characteristics: UDF `itemCharacteristic`
E1CUCFG/E1CUVAL sit **beside** the items at IDOC level and point to their item by POSEX. The samples have 1–3 E1CUCFG per item, so the n-th E1CUCFG is not the n-th item.
- Inputs, each in one context: item POSEX `[context IDOC]`, E1CUCFG-POSEX repeated per E1CUVAL (`useOneAsMany`), CHARC, `mapWithDefault(VALUE)`, `mapWithDefault(VALUE_TXT)` (in their own context, then `removeContexts`), and the CHARC name as a constant.
- Outputs: 0 = VALUE, 1 = VALUE_TXT, one value per item (empty when the item lacks it).
- In the mapping: `SplitByValue[each]` (one context per item), then node and fields `ifWithoutElse(value ≠ '', …)` from the same per-item chain.
- Values are returned as sent, not trimmed (KVALITET `' S355G10+M MDS-Y20'` keeps its space, as today).

### Sample check (rules emulated in Python against the 5 expected outputs + the 5 Hämeenlinna Tilkku sets)
- Properties, Measurements, Quantity LL and Package: **values identical** in all 10 sets.
- **Order differs** in 6 Raahe items (PO 46540776, 46541041): today Property 8 (TIKKU_GROUP) comes after ZED/ZMA there, before 35 elsewhere (Implema's own order, not explained by the spec). In one Hämeenlinna item the Measurements come LN, TH, WD. The mapping always writes the spec order (duplicate subtrees). See open question Q1.
- Not emulated: the CPI runtime itself. Test in the CPI simulator with the `_utf8.xml` copies.

## UDF call-outs (R2)
- **Bhavesh, I built `itemCharacteristic`** (`scripts/itemCharacteristic.groovy`) **because** the properties, measurements, tolerance and package (#33–54, #59–60) come from the E1CUVAL of the item's own configurations, which are linked to the item only by POSEX, and an item has 1–3 E1CUCFG. **Standard alternative:** align E1CUCFG with E1EDP01 by position, or an XSLT step in the iFlow that moves E1CUVAL under its E1EDP01. **Why not:** position fails with several E1CUCFG per item, no standard function joins two queues by a key, and no iFlow work is in scope (user 2026-11-16). Please review.
- **Reused unchanged:** `removezeros` (reference CostCentertoMedius, IDTNR may contain letters), `hasBestText` from `TibnorOrdersHelpers.groovy` (Metocs ORDERS; an item without any E1EDPT1 must give "false", which an array UDF does), `substringSafe` (udf_library; KTEXT may be shorter than 35).

## Open questions
- **Q1 Property / Measurement order.** iFlow: none known › mapping `Map_TibnorS4_RaaheTilkkuHub_PurchaseOrder_ORDERS02` › `/OrdersMessage/Item/Property[5]` (Type 8, TIKKU_GROUP). The mapping writes the spec order; today's output puts Property 8 after ZED/ZMA for some items. The XSD does not fix the order of Property occurrences. Is the order important for the hub?
- **Q2 Spaces in a constant.** `/OrdersMessage/Party[2]/AddressLine3` = `concat(substring(concat(WE-PSTLZ, const '        '), start 0, count 8), toUpperCase(WE-ORT01))`. **UNVERIFIED** whether CPI keeps a constant of 8 spaces. If it trims it, `substring` fails for postal codes shorter than 8 characters. Please check in the simulator (expected `2074    EIDSVOLL VERK`).
- Spec open points not decided here: OP-01 (TST routing values), OP-03 (other order types), OP-05/06/07/09–12, OP-16 (coils for Raahe).

## Decisions
| Date | Question | Answer | Impact |
|---|---|---|---|
| 2026-11-16 | Folder and name | Folder `6_ORDERS_Tibnor-to-RaaheTilkku` (pattern of folders 1–2); name `Map_TibnorS4_RaaheTilkkuHub_PurchaseOrder_ORDERS02` | `.mmap` and zip name |
| 2026-11-16 | The spec covers both Tilkku mills: build both into one mapping? | **Raahe only**: one mapping per mill; Hämeenlinna Tilkku gets its own (folder 10) | VM-01 has only this mill's row; ZMA is sent |
| 2026-11-16 | Characteristics sit beside the items, linked by POSEX | User: "try to solve it with the graphical mapping in a UDF and call it out" | UDF `itemCharacteristic` + standard per-item chains; call-out above |
| 2026-11-16 | OP-14 city upper case | **Standard `toUpperCase`** ('Sölvesborg' → 'SÖLVESBORG', today 'SöLVESBORG') | No UDF; differs from today for ä/ö/å |
| 2026-11-16 | iFlow steps | None: mapping only (user) | No sort/XSLT step; all logic in the mapping |
| 2026-11-16 | Environment suffix PRD/TST (#7–8) | Same as Metocs ORDERS Q3: exchange property `HubEnvironment` (my default, stated to the user) | iFlow / simulator must set the property |
| 2026-11-16 | Values as sent | Today's output keeps leading spaces of VALUE_TXT; the UDF does not trim | like-for-like |
| 2026-11-16 | Not well-formed sample originals | Escaped only in the `_utf8` copies | Originals unchanged |
