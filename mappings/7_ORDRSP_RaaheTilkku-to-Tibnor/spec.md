# Raahe Tilkku hub OrdrspInterchange → Tibnor ORDRSP / ORDERS01

- **Mapping name:** `Map_RaaheTilkkuHub_TibnorS4_OrderConfirmation_ORDRSP` (user, 2026-11-16)
- **Interface:** 1002235 · IN-14536 – Tibnor SSABEuropeRaaheTilkku [80067] EDI ORDRSP in. No iFlow known (mapping only).
- **Spec source:** `1002257_ORDRSP_Tilkku-to-Tibnor_MappingSpec_v0.1.xlsx` (shared with Hämeenlinna Tilkku 1002257; copied here from that folder, see `Spec is in 1002257.txt`)
- **Source:** `schemas/Ordrsp_1_0_0.xsd`, root `OrdrspInterchange`, qualified namespace `…/eruukki` (`ns0:` on every element step, 4th link elem). Copied from the Metocs ORDRSP mapping.
- **Target:** `schemas/ORDRSP.ORDERS02.xsd`, IDoc root `ORDERS01` (file name as delivered for Metocs).
- **Shared logic:** `build(mill)` in `build_mapping.py`; the Hämeenlinna Tilkku mapping (folder 11) calls it with its VM-01 values.
- **Samples:** `samples/20261116_0046540729/` (Tibnor AS, plates). Simulator copy without `xsi:` attributes: `Input_*_sim.xml`.

## Design (target ← source, how)
Same patterns as the user-tested Metocs ORDRSP v1.0.6 (same source XSD).

| # | Target | Built with |
|---|---|---|
| 1 | IDOCTYP / MESTYP | constants `ORDERS01` / `ORDRSP` |
| 2 | SNDPRT / SNDPFC / SNDPRN | `ifWithoutElse(InterchangeSender = '00372389445741', LI / LF / 0000080067)` (VM-01). Another sender leaves them empty, so the IDoc fails instead of going to the wrong partner |
| 3 | RCVPRT / RCVPRN | `LS` / `getProperty("RCVPRN")`; SNDPOR / RCVPOR `getProperty` (as Metocs) |
| 4–5 | SNDLAD / RCVLAD | InterchangeSender / InterchangeRecipient |
| 6 | STD / STDVRS / STDMES | `E` / `93A` / `ORDRSP` (today's IDoc); REFMES not mapped (OP-05) |
| 7, 12 | E1EDK01-BELNR, E1EDK02 001 | Reference[@Type='CO']/RefNo, `ifWithoutElse → removeContexts → SplitByValue` |
| 8 | E1EDK03 012 / DATUM | DocumentId/Date with `@Type [context DocumentId]` = 137; segment and field from one chain |
| 9 | E1EDKA1 (AG) / PARTN | Party[@Role='BY']/PartyId[@Type='ZTI']: `@Role` repeated per PartyId (`useOneAsMany`), `PartyId/@Type [context Party]` |
| 10 | E1EDKA1[1] (WE) | constant segment, PARVW only (OP-03) |
| 11 | E1EDKA1[2] (LF) / PARTN | Party[@Role='SE']/PartyId[@Type='ZTI'], as #9 |
| 13 | E1EDK02[1] 002 / BELNR | DocumentId/DocumentNo |
| 14–15 | E1EDP01, POSEX | ← Item; `formatNumber(LineNo, '#')` |
| 16–17, 23 | MENGE, MENEE, WMENG | Quantity type 21, PO pattern; MENEE copy (no M → MTR, OP-02) |
| 18–19 | PMENE / VPREI | Item/Price/MeasureUnit, PriceValue with `context = Item` (at most one Price per Item) |
| 20–21 | E1EDP02 001 / BELNR, ZEILE | `CopyValue(PO no, 0)`; `formatNumber(LineNo, '#')` |
| 22, 24 | E1EDP03 001 / DATUM, EDATU | Date 55/718 (attributes `context Item`), `substringSafe(…, 9, 17)` = end of the range |
| 25 | E1EDP19 001 / IDTNR | ArticleNo `@Type [context Item]` = IN; segment from the same chain |

### Sample check (by hand)
PO 46540729: BELNR 46540729, E1EDK03 20261113, AG 0142700, WE empty, LF 0003000, E1EDK02 001/46540729 and 002/95849A; item 10, 19200.00 KGM, TNE 1085.00, DATUM = EDATU 20261220, IDTNR 330057. EDI_DC40 LI/LF/0000080067, SNDLAD 00372389445741, RCVLAD 7080003309006. Matches `Output_IDOC_0000000020345014.xml` (MANDT, DOCNUM, STATUS, CREDAT, CRETIM, REFMES are filled by SAP / not mapped).

## UDF call-outs (R2)
- `substringSafe` (udf_library, unchanged): the range end date (positions 9–17) after the 718 filter, as in Metocs ORDRSP. No new UDF.

## Open questions
- Spec open points OP-01 (several items, item filter), OP-03 (empty WE segment), OP-04 (UnitPriceBasis ≠ 1), OP-05 (control record values per environment), OP-06 (changed confirmations) stay open in the spec.

## Decisions
| Date | Question | Answer | Impact |
|---|---|---|---|
| 2026-11-16 | Spec missing in the Raahe zip | User added the 1002257 zips; the shared spec is copied into this folder | Rows refer to the 1002257 sheet |
| 2026-11-16 | Folder and name | `7_ORDRSP_RaaheTilkku-to-Tibnor`; `Map_RaaheTilkkuHub_TibnorS4_OrderConfirmation_ORDRSP` | `.mmap` / zip name |
| 2026-11-16 | Both mills in one mapping? | **Raahe only**; Hämeenlinna Tilkku in folder 11 | VM-01 = Raahe GLN only |
| 2026-11-16 | Control record | As Metocs ORDRSP (my default, stated to the user): `getProperty` SNDPOR / RCVPOR / RCVPRN, STD constants, STDVRS `93A` from the sample | iFlow sets the properties |
| 2026-11-16 | iFlow steps | None: mapping only (user) | One OrderResponseMessage per message assumed, as Metocs |
| 2026-11-16 | Price fields | `context = Item` instead of the PO filter pattern (no qualifier to filter on) | An Item without Price stays aligned |

- **2026-11-24 Segment-level filters (v1.0.1, rule from the user's ORDERS v1.2.0 feedback, L2).** EDI_DC40 ← createIf(is_mill), sender fields constants; E1EDK02 (QUALF 001) ← createIf(Reference/@Type [context OrderResponseMessage] = CO), BELNR 1:1.
  - Kept as chains: E1EDKA1 AG/LF: PARTN is the ZTI PartyId inside the Party (own-value filter), so it stays a chain. Item values as in Metocs ORDRSP.

- **2026-11-24 (v1.0.2, L2, user Q1).** E1EDKA1 (AG) ← createIf(Party/@Role [context OrderResponseMessage] = BY), E1EDKA1[2] (LF) ← createIf(… = SE); PARTN ← ifWithoutElse(PartyId/@Type [context Party] = ZTI, PartyId) within that Party (useOneAsMany removed). No E1EDKA1 AG/LF when the Party is missing (before: always, possibly empty).
