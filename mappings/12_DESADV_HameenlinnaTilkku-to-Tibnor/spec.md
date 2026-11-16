# Hämeenlinna Tilkku hub DeliveryBatch → Tibnor DESADV / DELVRY01

- **Mapping name:** `Map_HammelinnaTilkkuHub_TibnorS4_DeliveryNotice_DESADV` (user, 2026-11-16)
- **Interface:** 1002242 · IN-14529 – Tibnor SSABEuropeHameenlinnaTilkku [86245] EDI DESADV in. No iFlow known (mapping only).
- **Spec source:** `1000761_DESADV_RaaheTilkku-to-Tibnor_MappingSpec_v0.1.xlsx` (shared spec, copied here; see `Spec is in 1000761.txt`)
- **Design:** identical to the Raahe Tilkku mapping, `mappings/8_DESADV_RaaheTilkku-to-Tibnor/spec.md`. The logic is `build(mill)` in `mappings/8_DESADV_RaaheTilkku-to-Tibnor/build_mapping.py`; this folder's `build_mapping.py` passes the values of this mill. Schemas and scripts are the same files.
- **Samples:** 3 sets (coils, status 51 today – Q59 in the spec); `_sim.xml` copies.

## What differs from Raahe Tilkku
- VM-01: InterchangeSender `00372389445751` → `LI`/`LF`/`0000086245`, E1ADRM1 PARTNER_ID `86245`. **VM-02: groups by heat number** (`SinglePart/MaterialBatch[MaterialBatchType='HEAT']/MaterialBatchId`), and **one E1EDL11 per SinglePart** of the group with the first 8 characters of its SinglePartId: `E1EDL11` and `SERNR` ← `formatByExample(substring(SinglePartId, 0, 8), groups)`.
- UDF `getBuyerOrderId` (same file as Raahe): see the call-out in the Raahe spec.

## Sample check
Rules emulated in Python: E1EDL24, POSNR, LFIMG and the E1EDL11 list equal all 3 expected IDocs (44779J-01: 2 bundles of heat 25472 → 1 item, SERNR BJ506001 + BJ506002).

## Open questions
See the Raahe spec (same questions, same build logic).

## Decisions
| Date | Question | Answer | Impact |
|---|---|---|---|
| 2026-11-16 | Folder and name | `12_DESADV_HameenlinnaTilkku-to-Tibnor`; `Map_HammelinnaTilkkuHub_TibnorS4_DeliveryNotice_DESADV` (user chose the spelling 'Hammelinna', as the Metocs mappings) | `.mmap` / zip name |
| 2026-11-16 | The spec covers both Tilkku mills: one mapping for both? | **One mapping per mill** (user: "Raahe only" for the Raahe mapping; the 4 Hämeenlinna Tilkku zips get their own mappings) | VM-02 = heat number, one E1EDL11 per SinglePart |
| 2026-11-16 | Grouping: standard or UDF; sort first? | **Standard, no sort** (SplitByValue value change) | Parts of a group must be consecutive |
| 2026-11-16 | Source XSD 0.8.4 not available | **Use 0_8_1 now**, swap when 0_8_4 arrives | Link and `xsd/` use DeliveryBatch_0_8_1.xsd |
| 2026-11-16 | Control record | As Metocs (my default, stated to the user): `getProperty` SNDPOR/RCVPOR/RCVPRN, STD constants `93A` | iFlow sets the properties |
| 2026-11-16 | "Before the first '-'" | UDF `getBuyerOrderId` (port of the PO UDF), call-out in the Raahe spec | One UDF |
| 2026-11-16 | iFlow steps | None: mapping only (user) | No sort step |
