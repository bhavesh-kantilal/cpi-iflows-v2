# Raahe Tilkku hub DeliveryBatch → Tibnor DESADV / DELVRY01

- **Mapping name:** `Map_RaaheTilkkuHub_TibnorS4_DeliveryNotice_DESADV` (user, 2026-11-16)
- **Interface:** 1000761 · IN-14533 – Tibnor SSABEuropeRaaheTilkku [80067] EDI DESADV in. No iFlow known (mapping only).
- **Spec source:** `1000761_DESADV_RaaheTilkku-to-Tibnor_MappingSpec_v0.1.xlsx` (shared with Hämeenlinna Tilkku 1002242)
- **Source:** `schemas/DeliveryBatch_0_8_1.xsd` (copied from the Metocs DESADV), root `DeliveryBatch`, qualified namespace `…/rucomef/otc`. The samples are version 0.8.4, which only adds `SinglePart/SlabManufacturerParty` (not used). Validation of the samples against 0_8_1 fails only on that element.
- **Target:** `schemas/DESADV.DELVRY01.xsd`, root `DELVRY01`
- **Shared logic:** `build(mill)` in `build_mapping.py`; the Hämeenlinna Tilkku mapping (folder 12) calls it with heat grouping.
- **Reference:** `reference/PO-Mapping_DeliveryBatch_to_DESADV93A_TIBNOR.txt`, `reference/PO-UDF_…_getBuyerOrderId.txt`
- **Samples:** 4 sets; simulator copies without `xsi:` attributes `Input_*_sim.xml`.

## Design (target ← source, how)
| # | Target | Built with |
|---|---|---|
| 1, 7 | IDOCTYP/MESTYP, STD/STDVRS/STDMES | `DELVRY01`/`DESADV`; `E`/`93A`/`DESADV` (today's IDoc); REFMES not mapped (OP-05) |
| 2 | SNDPRT/SNDPFC/SNDPRN | `ifWithoutElse(InterchangeSender = '00372389445741', LI / LF / 0000080067)` (VM-01) |
| 3–4 | SNDPOR, RCVPOR, RCVPRT, RCVPRN | `getProperty` / `LS` (as Metocs) |
| 5–6 | SNDLAD / RCVLAD | InterchangeSender / InterchangeRecipient |
| 8 | E1EDL20-VBELN | UDF `getBuyerOrderId(Reference[BuyersOrderId]/ReferenceId)`: part before the first '-' |
| 9 | E1ADRM1 LF / PARTNER_ID | constant segment; `80067` for this mill |
| 10 | E1EDT13 007 / NTANF | `TransformDate(DespatchDate, yyyy-MM-dd → yyyyMMdd)` |
| 11 | E1EDL24 (one per group) | `collapseContexts(groups)` |
| 12, 22, 27 | POSNR, E1EDL43-POSNR, E1EDL41-POSEX | line id per group, `formatNumber '#'` |
| 13–14 | MATNR, KDMAT | CustomersArticleId per group |
| 15, 21, 25 | ARKTX, E1EDL43-BELNR, E1EDL41-BSTNR | `formatNumber(order no, '0000000000')`, `CopyValue(…, 0)` |
| 16 | LFIMG | `formatNumber(SplitByValue[each](sum(formatByExample(Pieces, groups))), '#')` |
| 17 | VRKME | `PCE` |
| 18, 23, 26 | ABRDT, E1EDL43-DATUM, E1EDL41-BSTDT | DespatchDate, `CopyValue(…, 0)` |
| 19 | E1EDL11-SERNR | Raahe: one E1EDL11 per item with the group key |
| 20, 24 | E1EDL43 V, E1EDL41 001 | constant segments |

### Grouping (#11, VM-02), standard functions only
- Part values are flattened in document order, one per SinglePart: line id and article via `useOneAsMany(line value, SinglePart, SinglePart)`, key `substring(SinglePartId, 0, 8)`, Pieces via the PO filter on `SinglePart/DespatchedQuantity[ValueName='Pieces']`.
- `groups = SplitByValue[value change](concat(line id, key, ':'))`. Line + key, so equal keys of two lines never merge.
- **Value change groups consecutive equal keys only** (CLAUDE.md R1). The user chose no sort step (2026-11-16): the parts of one group must arrive next to each other, as in all samples.

### Sample check (rules emulated in Python)
All 7 Tilkku sets (4 Raahe, 3 Hämeenlinna Tilkku): E1EDL24 count, POSNR, LFIMG and E1EDL11 equal the expected IDocs (20938-02: 6 plates → 3 items with 2 pieces each).

## UDF call-outs (R2)
- **Bhavesh, I built `getBuyerOrderId`** (`scripts/getBuyerOrderId.groovy`) **because** VBELN / ARKTX / BELNR / BSTNR need the BuyersOrderId part before the first '-' (#8). It is the PO UDF of the same name, rewritten in Groovy with the same logic. **Standard alternative:** `substring`. **Why not:** its start and count are fixed, the position of '-' is not. (All samples have no '-'.)

## Open questions
- **Q1 Pieces format.** `/DELVRY01/IDOC/E1EDL20/E1EDL24/LFIMG` = `formatNumber(SplitByValue[each](sum(formatByExample(removeContexts(ifWithoutElse(ValueName = 'Pieces', Value)), groups))), '#')`. `sum` of `00005.00` values: **UNVERIFIED** what text `sum` returns before `formatNumber`; expected `28`.
- Spec open points: OP-01 (several lines), OP-02 (despatch number), OP-03 (pieces only), OP-04 (grouping per mill or part type), OP-06 (part without pieces), OP-07 (changes).

## Decisions
| Date | Question | Answer | Impact |
|---|---|---|---|
| 2026-11-16 | Folder and name | `8_DESADV_RaaheTilkku-to-Tibnor`; `Map_RaaheTilkkuHub_TibnorS4_DeliveryNotice_DESADV` | `.mmap` / zip name |
| 2026-11-16 | Both mills in one mapping? | **Raahe only**; Hämeenlinna Tilkku in folder 12 | VM-02 = first 8 characters of SinglePartId |
| 2026-11-16 | Grouping: standard or UDF; sort first? | **Standard, no sort** (SplitByValue value change) | Parts of a group must be consecutive |
| 2026-11-16 | Source XSD 0.8.4 not available | **Use 0_8_1 now**, swap when 0_8_4 arrives | Link and `xsd/` use DeliveryBatch_0_8_1.xsd |
| 2026-11-16 | Control record | As Metocs (my default, stated to the user): `getProperty` SNDPOR/RCVPOR/RCVPRN, STD constants `93A` | iFlow sets the properties |
| 2026-11-16 | "Before the first '-'" | UDF `getBuyerOrderId` (port of the PO UDF), call-out above | One UDF |
| 2026-11-16 | iFlow steps | None: mapping only (user) | No sort step |
