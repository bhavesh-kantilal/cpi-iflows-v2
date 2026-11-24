# Metocs hub Invoice → Tibnor INVOIC / INVOIC01 (message code MM)

- **Mapping name:** `Map_HammelinnaMetocsHub_TibnorS4_Invoice_INVOIC`
- **Spec source:** `25224_INVOIC_HameenlinnaMetocs-to-Tibnor_MappingSpec_v0.1.xlsx` (draft v0.1, 12 Nov 2026), integration ID 25224 / IN-14526
- **Source:** `schemas/Harmonized_Mill_Invoice_0_0_4_AoC.xsd`, root `Invoice`. It has **no targetNamespace**, so paths carry no prefix and the source link has 3 elems. The samples declare `Harmonized_Mill_Invoice_0_0_4.xsd`; OP-13 asks whether the `_AoC` variant is right.
- **Target:** `schemas/INVOIC.INVOIC01.xsd`, IDoc root `INVOIC01`
- **Old PO mapping:** `Reference/PO-Mapping_FIN_Invoice_to_INVOIC96A_TIBNOR_Tube.txt` (hub → EDIFACT; Implema built the IDoc from it)
- **Samples:** 5 sets in `samples/<date>_<invoice>/`: `Input_*.xml`, the Implema EDIFACT `Intermediate_*.xml` and the expected `Output_IDOC_*.xml`.
  - `Input_*_sim.xml` = the input without `xmlns:xsi` / `xsi:noNamespaceSchemaLocation`, for the mapping simulator (`tools/sim_copy.py`, CLAUDE.md). The originals are unchanged.

## How I read the sheet
- Sheet "Mapping": `#`, `Target field`, `Occ.`, `Source`, `Target rule`, `Sample value`, `Status`, `Notes`. `X[@Type='1']` = the occurrence whose attribute Type = 1.
- "Value Mappings": VM-01 (SourceSystem starts with `METOCS` → 80008), VM-03 (DocumentType 380 → INVO / LR / L).

## Design (target ← source, how)
Standard functions only. Qualifier filters follow the user's PO pattern (FORMAT_NOTES §3.6): `ifWithoutElse(stringEquals(mapWithDefault(@attr), 'X'), mapWithDefault(value))`, then `removeContexts` for header values, or `removeContexts` → `SplitByValue(Each Value)` for repeating values. No context settings on source fields.

| # | Target | Built with |
|---|---|---|
| — | `INVOIC01`, `IDOC`, `EDI_DC40`, `E1EDK01`, `E1EDKA1`, `E1EDKA1[1]`, `E1EDK02`, `E1EDK03`, `E1EDP02`, `E1EDP03`, `E1EDP19`, `E1EDP26`, `E1EDS01` | empty constant (containers that always exist); `@BEGIN`/`@SEGMENT` = `1`; `TABNAM`/`DIRECT` = `EDI_DC40`/`2` |
| 1 | IDOCTYP / MESTYP / MESCOD | constants `INVOIC01` / `INVOIC` / `MM` |
| 2 | SNDPRT / SNDPFC / SNDPRN | `ifWithoutElse(startWith2(Header/SourceSystem, 'METOCS'), const)` → LI / LF / 0000080008 |
| 3–4 | SNDPOR / RCVPOR / RCVPRN, RCVPRT | `getProperty` / constant `LS` (as ORDRSP) |
| 5–6 | SNDLAD / RCVLAD | Header/InterchangeSender / Header/RecipientIdentification |
| 7 | STD / STDVRS / STDMES, REFMES | `E` / `96A` / `INVOIC`, REFMES not mapped (as ORDRSP) |
| 8, 29 | E1EDK01-CURCY, E1EDS01-WAERQ | Currency[@Type='1']/CurrencyCode |
| 9–11 | BSART / FKART_RL / FKTYP | `ifWithoutElse(DocumentType = '380', const)` → INVO / LR / L |
| 12–13 | E1EDKA1 LF, E1EDKA1[1] RE / PARTN | duplicate subtree; `ifWithoutElse(METOCS, '80008')` |
| 14 | E1EDKA1[1]-NAME1 | `concat(Party[@Role='SE']/PartyName1, Party[@Role='BY']/CountryCode, delimeter '/')` |
| 15 | E1EDK02 009 / BELNR | DocumentId/DocumentNo |
| 16 | E1EDK03 012 / DATUM | DocumentId/Date[@Type='149'] (already YYYYMMDD) |
| 17–19 | E1EDK04 ← Tax (one per Tax) | MWSKZ ← `SplitByValue(removeContexts(Tax/@Type))` (the attribute sits in the Invoice context); MSATZ ← `iF('0', TaxRate = '0.00', TaxRate)`; MWSBT ← Tax/MonetaryAmount[@Type='176'] |
| 20 | E1EDP01 ← Item; POSEX | `formatNumber(LineNo, '#')` |
| 21–22 | MENGE / MENEE | Quantity[@Type='21'] value with `formatNumber '0.###'` / unit |
| 23 | E1EDP02 001 / BELNR | Reference[@Type='ON'] → `formatNumber '0000000000'` (10 digits, as ACC), once per item via `useOneAsMany(value, removeContexts(LineNo), LineNo)` |
| 24 | E1EDP02-ZEILE | `formatNumber(LineNo, '#')`. **A1** |
| 25 | E1EDP03 012 / DATUM | invoice date, once per item (`useOneAsMany`) |
| 26 | E1EDP19 001 / IDTNR | segment always created (as today); IDTNR ← AddArticleNo[@Type='UA'] |
| 27 | E1EDP26 003 / BETRG | Item/MonetaryAmount[@Type='38'] |
| 28 | E1EDS01 011 / SUMME | MonetaryAmount[@Type='39'] (gross) |

### Sample check (Python model of the rules against the 5 expected IDocs)
All header, tax, item and total values match, **except** ZEILE in 552-601893 (METOCSTO): LineNo `000001` gives `1`, but Implema sent `10` (A1). Also expected:
- `MSATZ` 0 / 25.50
- `MENGE` without decimals
- the PO number padded (`47856316` → `0047856316`)
- an empty E1EDP19 when there is no UA article

## Assumptions for later (user, 2026-11-13: "keep them as assumptions for later")
- **A1 ZEILE (OP-02):** LineNo without leading zeros for every mill. The METOCSTO sample would get `1` where Implema sent `10`. Needs a multi-line METOCSTO invoice or Tibnor's answer.
- **A2 Document type (OP-04):** only 380 is mapped. Any other type leaves BSART / FKART_RL / FKTYP empty.
- **A3 One PO per invoice (OP-10):** the header Reference ON goes to every item.
- **A4 PO number numeric:** `formatNumber '0000000000'` needs a numeric ON reference (all samples).
- **A5 One value per item:** each item has exactly one Quantity type 21, one MonetaryAmount type 38 and at most one UA article (PO pattern, see ORDRSP). With several items where one lacks a UA article, IDTNR values would move up an item.
- **A6 Control record** as ORDRSP: SNDPOR / RCVPOR / RCVPRN from exchange properties (today INOBIZ / SAPPRD / PRDCLNT100), STD constants, REFMES empty (OP-07).
- **A7 Non-METOCS SourceSystem:** SNDPRT/SNDPFC/SNDPRN and PARTN stay empty, so the mapping fails rather than post to a wrong vendor.

## Decisions
- **2026-11-13 Name** `Map_HammelinnaMetocsHub_TibnorS4_Invoice_INVOIC` (user).
- **2026-11-13 Control record** as ORDRSP (user).
- **2026-11-13 ZEILE** "ask later" (user) → A1.
- **2026-11-13 Files moved:** XSDs → `schemas/`. The empty `Test/` folder is left as it is.

- **2026-11-15 Rule R4 applied (user: "Docs + R4 fix only"):** no `mapWithDefault` around an attribute that has a `context=` setting (AddArticleNo/@Type → IDTNR). See CHANGELOG.

- **2026-11-24 Segment-level filters (v1.0.3, rule from the user's ORDERS v1.2.0 feedback, L2).** EDI_DC40 ← createIf(is_metocs), sender fields constants; E1EDKA1 (LF) and E1EDKA1[1] (RE) ← createIf(is_metocs), PARTN constant.
  - Kept as chains: E1EDK01 BSART/FKART_RL/FKTYP (is_380: the segment also carries CURCY), E1EDK04 MWSBT, E1EDP26 BETRG, E1EDP19 IDTNR and the item Quantity values (qualified values inside an item / tax line), header values (currency, date, PO number).

- **2026-11-24 E1EDK04 / E1EDP26 (v1.0.4, L2, user Q2 a+b).** Segment-level filter instead of a filtered value per field: E1EDK04 ← createIf(Tax/MonetaryAmount/@Type [context Invoice] = 176), E1EDP26 ← createIf(Item/MonetaryAmount/@Type [context Item] = 38); the amount fields 1:1. Impact: no segment when the amount type is missing.
- **2026-11-24 E1EDK01 BSART/FKART_RL/FKTYP (L2, user Q4).** Keep the field-level `DocumentType = 380` checks for now (CURCY in the same segment is always sent). To explain to the user later.

- **2026-11-24 v1.0.5 (L2, user's test of the Metocs INVOIC: "overkill… this check has been done already"; applied to all mappings, user: "Yes, all mappings").** EDI_DC40, E1EDKA1 (LF) and E1EDKA1[1] (RE) ← empty constant; the mill check `startsWith(SourceSystem, 'METOCS')` is removed, because the parent iFlow already routes by mill. `E1EDK04/MWSKZ ← Tax/@Type` 1:1: `removeContexts` → `SplitByValue` removed (the attribute already has one context per Tax).
