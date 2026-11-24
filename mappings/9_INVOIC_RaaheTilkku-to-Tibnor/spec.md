# Raahe Tilkku hub Invoice → Tibnor INVOIC / INVOIC01

- **Mapping name:** `Map_RaaheTilkkuHub_TibnorS4_Invoice_INVOIC` (user, 2026-11-16)
- **Interface:** 1002663 · IN-14534 – Tibnor SSABEuropeRaaheTilkku [80067] EDI INVOIC in. No iFlow known (mapping only).
- **Spec source:** `1002663_INVOIC_Tilkku-to-Tibnor_MappingSpec_v0.1.xlsx` (shared with Hämeenlinna Tilkku 1002743)
- **Source:** `schemas/Harmonized_Mill_Invoice_0_0_4_AoC.xsd`, root `Invoice`, no namespace (copied from the Metocs INVOIC). Both samples (version 0.0.6) validate against it.
- **Target:** `schemas/INVOIC.INVOIC01.xsd`, root `INVOIC01`
- **Shared logic:** `build(mill)` in `build_mapping.py`; the Hämeenlinna Tilkku mapping (folder 13) calls it.
- **Samples:** 2 sets; simulator copies without `xsi:` attributes `Input_*_sim.xml`.

## Design (target ← source, how)
Standard functions only. Patterns of the user-tested Metocs INVOIC v1.0.2.

| # | Target | Built with |
|---|---|---|
| 1, 7 | IDOCTYP/MESTYP/MESCOD, STD… | `INVOIC01`/`INVOIC`/`MM`; `E`/`96A`/`INVOIC`; REFMES not mapped (OP-07) |
| 2 | SNDPRT/SNDPFC/SNDPRN | `ifWithoutElse(InterchangeSender = '00372389445741', LI / LF / 0000080067)` (VM-01) |
| 3–4 | SNDPOR, RCVPOR, RCVPRT, RCVPRN | `getProperty` / `LS` |
| 5–6 | SNDLAD / RCVLAD | InterchangeSender / RecipientIdentification |
| 8, 30 | CURCY, WAERQ | Currency[@Type='1']/CurrencyCode |
| 9–11 | BSART / FKART_RL / FKTYP | `ifWithoutElse(DocumentType = '380', INVO / LR / L)` (VM-03, OP-04) |
| 12–13 | E1EDKA1 LF, E1EDKA1[1] RE / PARTN | `80067` for this mill |
| 14 | E1EDKA1[1]/NAME1 | `concat('SSAB EUROPE OY', FixValues(RecipientIdentification: 003723894430 → 0500, default ''), '/')` (VM-04) |
| 15 | E1EDK02 009 / BELNR | DocumentId/DocumentNo |
| 16 | E1EDK03 012 / DATUM | DocumentId/Date `@Type [context DocumentId]` = 149 |
| 17 | E1EDK05 | `createIf(greater(sum(iF('1', @Type = 165 or 260, '0')), '0'))` over all header MonetaryAmount types; ALCKZ `-`, BETRG `0.00`, UPRBS `SEK` constants (OP-06) |
| 18–20 | E1EDK04 MWSKZ / MSATZ / MWSBT | per Tax: `@Type`, TaxRate copy, MonetaryAmount 176 |
| 21 | POSEX | LineNo as it is (`010`) |
| 22–23 | MENGE / MENEE | Quantity 21; `formatNumber '0.00'` (exactly 2 decimals) |
| 24–25 | E1EDP02 001 / BELNR, ZEILE | `formatNumber(Reference[ON], '0000000000')` with `CopyValue`; `formatNumber(LineNo, '#')` |
| 26 | E1EDP03 012 / DATUM | invoice date, `CopyValue` |
| 27 | E1EDP19 001 / IDTNR | ArticleNo `@Type [context Item]` = IN; segment from the same chain |
| 28 | E1EDP26 003 / BETRG | Item MonetaryAmount 38 |
| 29 | E1EDS01 011 / SUMME | MonetaryAmount 39 |

### Sample check (by hand)
Invoice 122683168: E1EDK05 created (165 and 260 present, one segment), RE NAME1 `SSAB EUROPE OY/0500`, POSEX `010`, MENGE `21772.00`, BELNR `0046538408`, ZEILE `10`, IDTNR 386943, BETRG 21750.23, SUMME 27296.54. Matches the expected IDoc.

## Open questions
- **Q1 Two decimals.** `/INVOIC01/IDOC/E1EDP01/MENGE` = `formatNumber(Quantity[@Type='21']/QuantityValue, nformat '0.00')`. The `0.00` pattern is **UNVERIFIED** (`#`, `0.###` and `0000000000` are confirmed). Expected `21772.00`.
- **Q2 E1EDK05 condition.** `/INVOIC01/IDOC/E1EDK05` = `createIf(greater(sum(iF(const '1', or(stringEquals(removeContexts(MonetaryAmount/@Type), '165'), stringEquals(…, '260')), const '0')), '0'))`. **UNVERIFIED** in CPI; the expected result is one E1EDK05 for the Raahe samples.
- **Q3 VM-04 for AB / AS / DK (OP-08).** Only Tibnor OY (0500) is in the table; other recipients give `SSAB EUROPE OY/`.
- Spec open points OP-01 … OP-08.

## Decisions
| Date | Question | Answer | Impact |
|---|---|---|---|
| 2026-11-16 | Folder and name | `9_INVOIC_RaaheTilkku-to-Tibnor`; `Map_RaaheTilkkuHub_TibnorS4_Invoice_INVOIC` | `.mmap` / zip name |
| 2026-11-16 | Both mills in one mapping? | **Raahe only**; Hämeenlinna Tilkku in folder 13 | VM-01 = Raahe GLN only |
| 2026-11-16 | Control record | As Metocs INVOIC (my default, stated to the user) | iFlow sets the properties |
| 2026-11-16 | E1EDK05 (#17) | Built as the spec says (Assumed), for both mills; constants as today | OP-06 stays open |
| 2026-11-16 | VM-04 | Only the confirmed OY row | OP-08 |
| 2026-11-16 | iFlow steps | None: mapping only (user) | — |

- **2026-11-24 Segment-level filters (v1.0.1, rule from the user's ORDERS v1.2.0 feedback, L2).** EDI_DC40 ← createIf(is_mill), sender fields constants; E1EDKA1 (LF) and E1EDKA1[1] (RE) ← createIf(is_mill), PARTN constant.
  - Kept as chains: E1EDK01 (is_380 with CURCY), E1EDK05 (sum condition), item qualified values, header values.

- **2026-11-24 (v1.0.2, L2, user Q2 a+b).** E1EDK04 ← createIf(Tax/MonetaryAmount/@Type [context Invoice] = 176), MWSBT 1:1; E1EDP26 ← createIf(Item/MonetaryAmount/@Type [context Item] = 38), BETRG 1:1. No segment when the amount type is missing (before: always).
