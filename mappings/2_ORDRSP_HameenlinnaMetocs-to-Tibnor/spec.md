# Hämeenlinna Metocs hub OrdrspInterchange → Tibnor ORDRSP / ORDERS01

- **Mapping name:** `Map_HammelinnaMetocsHub_TibnorS4_OrderConfirmation_ORDRSP` (v1.0.0 was two test variants, see Q2; from v1.0.1 one mapping, `ns0:` on every source step)
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
| 9 | E1EDK03 (IDDAT 012) / DATUM | E1EDK03 ← `createIf(DocumentId/Date/@Type = '137')`; DATUM ← `ifWithoutElse(same condition, Date)` (format 102 is already YYYYMMDD) |
| 10 | E1EDK02 (QUALF 001) / BELNR | `createIf(Reference/@Type = 'CO')`; BELNR = PO number |
| 11 | E1EDK02[1] (QUALF 002) / BELNR | duplicate subtree; DocumentId/DocumentNo (mandatory in the source) |
| 12 | E1EDP01 | as the PO item node G_SG26: `removeContexts(ifWithoutElse(and(Property/@Type = '12', not(PropertyText = 'ITEM CANCELLED')), const ""))` |
| 13, 17 | POSEX, E1EDP02-ZEILE | `formatNumber(LineNo, '#', '.')` (leading zeros, numeric source) |
| 14, 19 | MENGE, E1EDP20-WMENG | PO pattern D_7140: `ifWithoutElse(mapWithDefault(Quantity/@Type) = '21', mapWithDefault(QuantityValue))` → `removeContexts` → `SplitByValue(Each Value)` |
| 15 | MENEE | `iF('MTR', unit = 'M', unit)` on the same chain for Quantity/MeasureUnit |
| 16 | E1EDP02 (QUALF 001) / BELNR | PO number once per Item: `useOneAsMany(PO no, removeContexts(LineNo), LineNo)` |
| 18, 20 | E1EDP03 (IDDAT 001) / DATUM, E1EDP20-EDATU | E1EDP03 ← `createIf(and(Date/@Type = '55', Date/@Format = '718'))`. Value as PO D_2380: `ifWithoutElse(same condition, substring(Date, start 9, count 8))` → `removeContexts` → `SplitByValue(Each Value)` = end of the range |
| 21 | E1EDP19 (QUALF 001) / IDTNR | E1EDP19 ← `createIf(AddArticleNo/@Type = 'IN')`; IDTNR as PO D_7140 (mapWithDefault on @Type and value, filter, removeContexts, SplitByValue) |

### Item values: the PO pattern (from v1.0.1)
No source field carries a context setting. Every filtered item value is built the way the user's existing PO mapping of the same hub source does it: filter with `ifWithoutElse`, then `removeContexts`, then `SplitByValue(Each Value)`, which gives one context per found value.
- **Assumption** (user, 2026-11-13: "a safe assumption"): every kept Item has exactly one type-21 Quantity, one format-718 Date and one IN article, and no Item is skipped by the #12 filter. If an Item lacks one of them, the values after it move up one Item. This affects EDATU, MENGE/WMENG/MENEE and IDTNR. For DATUM and IDTNR the parent segment is created per Item by `createIf`, so their k-th value goes to the k-th segment created.
- v1.0.0 instead put `context = Item` on child fields and applied `mapWithDefault` after that. **This did not work**: `mapWithDefault` no longer adds the missing values after a context change, so the queues drifted apart and no E1EDP01 was created (user's simulation, 2026-11-13).

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

## Import test v1.0.0 (2026-11-13, package Test_BK, user screenshots)
- **Both variants:** the user had to add the source message by hand in the editor after import. It is unclear which part of the generated source link CPI did not accept (perhaps a 4th `<elem>` with the namespace, as WSDL links have). This will be learned from the CPI download of the fixed variant.
- **NsRootOnly fails.** The CPI source tree shows `ns0:OrdrspInterchange / ns0:OrderResponseMessage / …`. The unprefixed `OrderResponseMessage` is shown orange, as missing.
- **NsAllSteps loads**: the CPI tree uses `ns0:` on every element step. It fails in the **simulator**, though:
  `The prefix "ns6" for attribute "ns6:schemaLocation" associated with an element type "OrdrspInterchange" is not bound.`
  - The simulator turns the root attributes (`@xmlns`, `@xmlns:xsi`, `@schemaLocation`) into test-input fields and loses the `xsi` prefix binding. This is a test-input problem, not a mapping problem.
  - Test copy `samples/Input_AA_ORDRSP96A_MS_20261111_0919_sim.xml`: the same as the original, without `xmlns:xsi` and `xsi:schemaLocation`. The original is unchanged.
  - **Open:** whether the iFlow runtime has the same problem with real hub payloads (which carry `xsi:schemaLocation`). Test it in the iFlow. If it fails, the iFlow must remove the attribute before the mapping.
- **Result:** `ns0:` on every element step is the right form for a qualified namespaced XSD source.

### User feedback on v1.0.0 → v1.0.1 (2026-11-13)
- NsAllSteps ran with the `_sim.xml` input, but most fields came out empty. In particular, no E1EDP01 was created (cause: see "Item values: the PO pattern" above).
- The user showed their existing **PO mapping of the same hub source** (towards EDI) and asked to follow it: **no UDF and no context handling on the lower levels.**
  - Item node G_SG26 ← `removeContexts(ifWithoutElse(and(@Type = 12, not(PropertyText = ITEM CANCELLED)), const ""))`
  - D_7140 (IN article) ← `ifWithoutElse(mapWithDefault(@Type) = IN, mapWithDefault(AddArticleNo))` → `removeContexts` → `SplitByValue(Each Value)`
  - D_2380 (date) ← `ifWithoutElse(and(@Type = 55, @Format = 718), substring(Date, 9, 17))` → `removeContexts` → `SplitByValue(Each Value)`. In PO that 3-input substring takes start and end; v1.0.1 uses the standard CPI `substring` with start 9 and count 8, which gives the same result.
  - D_7008_1 (PropertyText cropped to 35 characters) is the same pattern. It is not needed for ORDRSP.
- The user's own CPI test used a context UDF `checkItemToBeMapped` for E1EDP01. It is **not** used, because the user asked for the PO way without a UDF.
- **Decision:** v1.0.1 follows these patterns; the assumption is under "Item values". Source message link: still 3 elems. The user had to re-add the source message by hand in v1.0.0; it is open until a CPI download shows what CPI writes.

- **2026-11-13 Sample formatting.** Both input samples (original and `_sim.xml`) were re-indented on disk and committed with v1.0.1. The XML content is unchanged (canonical compare). The user decided to keep the indented files.

## Open points from the sheet (not blocking the build)
- OP-03 Tilkku / Raahe ApplicationIds (VM-01 has only METOCS…).
- OP-06 whether Tibnor needs SNDLAD/RCVLAD/STD…; OP-07 RCVPRN per environment (now a property).
- OP-10 PDF file name, OP-11 BELNR content, OP-13 price, OP-15 cancelled items, OP-16 items without a type-12 property.
