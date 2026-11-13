# Hämeenlinna Metocs hub OrdrspInterchange → Tibnor ORDRSP / ORDERS01

- **Mapping name:** `Map_HammelinnaMetocsHub_TibnorS4_OrderConfirmation_ORDRSP` (v1.0.0 is built as two test variants, see Q2)
- **Spec source:** `25207_ORDRSP_HameenlinnaMetocs-to-Tibnor_MappingSpec_v0.1.xlsx` (draft v0.1, 12 Nov 2026), integration ID 25207 / IN-14528
- **Source:** `schemas/Ordrsp_1_0_0.xsd`, root `OrdrspInterchange`, targetNamespace `http://www.ruukki.com/schemas/eai/internal/production/eruukki`, `elementFormDefault="qualified"`
- **Target:** `schemas/ORDRSP.ORDERS02.xsd`, IDoc root `ORDERS01`, no namespace. The file name says ORDERS02 but the content is basic type ORDERS01, which the spec asks for. The name is kept as delivered.
- **Samples:**
  - input `samples/Input_AA_ORDRSP96A_MS_20261111_0919.xml` (METOCSHAP → Tibnor OY, PO 0046537330, change version 7, 15 items). It is UTF-8 with an encoding declaration, so no `_utf8` copy is needed.
  - expected output `samples/Output_IDOC_0000000020267720.xml`

## How I read the sheet
- **Sheet "Mapping"** has columns `#`, `Target field`, `Occ.`, `Source`, `Target rule`, `Sample value`, `Status`, `Notes`. Rows without `#` are section headings.
  - `X[@Type='CO']` means the occurrence of X whose attribute `Type` = `CO`.
  - `E1EDK02 (QUALF = '001')` means: create that segment with QUALF set to the constant.
- **"Value Mappings"**: VM-01 only (ApplicationId starts with `METOCS` → LI / LF / 0000080008). **"Not Mapped"**: hub data that is ignored. **"Open Points"**: OP-03 … OP-16.

## Design (target ← source, how)
Only functions from FORMAT_NOTES. No Groovy UDF is needed.

| # | Target | Built with |
|---|---|---|
| — | `ORDERS01`, `IDOC`, `EDI_DC40`, `E1EDK01`, `E1EDK02[1]`, `E1EDP02`, `E1EDP20` | empty constant (containers that always exist) |
| — | `IDOC/@BEGIN`, every `@SEGMENT` | constant `1` (as reference CLFMAS02) |
| — | `TABNAM`, `DIRECT` | constants `EDI_DC40`, `2`. Mandatory in the XSD, not in the spec; as reference CLFMAS02 |
| 1 | IDOCTYP / MESTYP | constants `ORDERS01` / `ORDRSP` |
| 2 | SNDPRT / SNDPFC / SNDPRN | `ifWithoutElse(startWith2(ApplicationId, 'METOCS'), const)` → LI / LF / 0000080008. Any other ApplicationId leaves these mandatory fields empty, so the mapping fails rather than send to a wrong partner |
| 3 | RCVPRT / RCVPRN | `LS` constant / `getProperty("RCVPRN")` |
| — | SNDPOR / RCVPOR | `getProperty("SNDPOR")` / `getProperty("RCVPOR")` (Q3) |
| 4–5 | SNDLAD / RCVLAD | copy InterchangeSender / InterchangeRecipient |
| 6 | STD / STDVRS / STDMES | constants `E` / `96A` / `ORDRSP` (Q4) |
| 7 | REFMES | not mapped (Q4) |
| 8 | E1EDK01-BELNR | `removeContexts(ifWithoutElse(Reference/@Type = 'CO', RefNo))` = "PO number" |
| 9 | E1EDK03 (IDDAT 012) / DATUM | `createIf` when DocumentId/Date[@Type='137'] exists; date copied (format 102 is already YYYYMMDD) |
| 10 | E1EDK02 (QUALF 001) / BELNR | `createIf` when the PO number exists; BELNR = PO number |
| 11 | E1EDK02[1] (QUALF 002) / BELNR | duplicate subtree; DocumentId/DocumentNo (mandatory in the source) |
| 12 | E1EDP01 | `createIf(not(stringEquals(mapWithDefault(type-12 PropertyText, 'ITEM CANCELLED'), 'ITEM CANCELLED')))` per Item. An Item with no type-12 property gets the default and is skipped like a cancelled one |
| 13, 17 | POSEX, E1EDP02-ZEILE | `formatNumber(LineNo, '#', '.')` (leading zeros, numeric source) |
| 14, 19 | MENGE, E1EDP20-WMENG | Quantity[@Type='21']/QuantityValue |
| 15 | MENEE | `iF('MTR', unit = 'M', unit)` on Quantity[@Type='21']/MeasureUnit |
| 16 | E1EDP02 (QUALF 001) / BELNR | PO number repeated per Item: `useOneAsMany(PO no, LineNo [context OrderResponseMessage], LineNo)` |
| 18, 20 | E1EDP03 (IDDAT 001) / DATUM, E1EDP20-EDATU | Date[@Type='55'][@Format='718'] → `substring(start 9, count 8)` = end of the range. E1EDP03 ← `createIf` when that date exists; without it EDATU is left out |
| 21 | E1EDP19 (QUALF 001) / IDTNR | `createIf` when AddArticleNo[@Type='IN'] exists; IDTNR = copy |

### Queue alignment (why some sources carry a context)
An attribute such as `Quantity/@Type` sits on the Quantity level, so its default context is the Item. A child field such as `Quantity/QuantityValue` has the Quantity as its default context. To compare them value by value, the child field gets `context = Item`. This applies to Quantity (QuantityValue, MeasureUnit), Property (PropertyText) and Reference (RefNo, context OrderResponseMessage). `Date` and `AddArticleNo` carry their value on the same level as their attributes, so they need no context.
- **Known risk:** this pairing assumes every Quantity has a MeasureUnit and every Property a PropertyText (both optional in the XSD). The hub writes empty elements (`<PropertyText/>`) in all samples, so it holds today.

### Sample check (by hand, against the expected output)
All 15 items: POSEX 10 … 150, MENGE = type-21 quantity, MENEE MTR, DATUM = EDATU = end of the 718 range (e.g. 20261207-20261220 → 20261220), IDTNR = IN article. Header: BELNR 0046537330, E1EDK03 20261111, E1EDK02 001/0046537330 and 002/764930. EDI_DC40: LI/LF/0000080008, SNDLAD 00372389445756, RCVLAD 003723894430, E/96A/ORDRSP. Every sample item has a type-12 property, so no item is skipped.
- Fields in the sample IDoc that the SAP receiver fills itself (MANDT, DOCNUM, DOCREL, STATUS, OUTMOD, CREDAT, CRETIM) are not mapped. REFMES is not mapped (Q4).

## Decisions
- **2026-11-13 Q1 Name.** `Map_HammelinnaMetocsHub_TibnorS4_OrderConfirmation_ORDRSP`, chosen by the user. It keeps the ORDERS mapping's spelling "Hammelinna".
- **2026-11-13 Q2 Source namespace.** The source XSD has a targetNamespace with qualified elements. The sample XML puts every element in that namespace through a default `xmlns="…/eruukki"` on the root, so the XML itself has no prefix. No reference has a fully qualified namespaced source; the references only show a prefix on the root (MAT, CCM) or on one mid-path element (JE).
  - The user asked for **two variants to test**, to learn the right form from the import:
    - `…_ORDRSP_NsAllSteps`: `ns0:` on every element step (my reading of the XSD).
    - `…_ORDRSP_NsRootOnly`: `ns0:` on the root only (the pattern the references show).
  - Both declare `ns0` = the eruukki URI and keep the XSD link at 3 elems (as for other XSDs). Everything else is identical. **UNVERIFIED** until the import test. Only the variant that works stays, under the plain mapping name.
- **2026-11-13 Q3 Ports.** SNDPOR, RCVPOR and RCVPRN ← `getProperty` with those property names, as in reference CLFMAS02. The iFlow sets them (for the simulator: set them as properties). RCVPRT is the constant `LS` (row 3).
- **2026-11-13 Q4 Rows 6–7 (OP-06).** STD/STDVRS/STDMES = constants `E`/`96A`/`ORDRSP`, as in Implema's IDoc today. REFMES stays empty.
- **2026-11-13 TABNAM/DIRECT.** Mandatory in the IDoc XSD, not in the spec: constants `EDI_DC40` / `2`, as in reference CLFMAS02.
- **2026-11-13 One message per interchange (OP-08).** The target IDoc allows one `IDOC`, so `IDOC` comes from an empty constant and the mapping assumes one OrderResponseMessage per interchange, as in all 6 sample sets. If the hub ever sends several, the iFlow must split them before the mapping.
- **2026-11-13 Item filter (#12)** uses only standard functions (no UDF). "ITEM CANCELLED" is an exact match, as in the spec. Not tested with a cancelled item: the sample has none. It relies on the runtime skipping the child values of a suppressed E1EDP01.
- **2026-11-13 Unit 'M' → 'MTR' (#15)** uses `iF` instead of FixValues, because FixValues' "use key when not found" numbering is still UNVERIFIED (FORMAT_NOTES §5 Q1).
- **2026-11-13 Files moved** into the standard layout: XSDs → `schemas/`, sample XMLs → `samples/` (contents unchanged).

## Open points from the sheet (not blocking the build)
- OP-03 Tilkku / Raahe ApplicationIds (VM-01 has only METOCS…).
- OP-06 whether Tibnor needs SNDLAD/RCVLAD/STD…; OP-07 RCVPRN per environment (now a property).
- OP-10 PDF file name, OP-11 BELNR content, OP-13 price, OP-15 cancelled items, OP-16 items without a type-12 property.
