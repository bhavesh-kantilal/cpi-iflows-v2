# Hämeenlinna Tilkku hub OrdrspInterchange → Tibnor ORDRSP / ORDERS01

- **Mapping name:** `Map_HammelinnaTilkkuHub_TibnorS4_OrderConfirmation_ORDRSP` (user, 2026-11-16)
- **Interface:** 1002257 · IN-14530 – Tibnor SSABEuropeHameenlinnaTilkku [86245] EDI ORDRSP in. No iFlow known (mapping only).
- **Spec source:** `1002257_ORDRSP_Tilkku-to-Tibnor_MappingSpec_v0.1.xlsx` (the shared spec lives in this folder)
- **Design:** identical to the Raahe Tilkku mapping, `mappings/7_ORDRSP_RaaheTilkku-to-Tibnor/spec.md`. The logic is `build(mill)` in `mappings/7_ORDRSP_RaaheTilkku-to-Tibnor/build_mapping.py`; this folder's `build_mapping.py` passes the values of this mill. Schemas and scripts are the same files.
- **Samples:** 2 sets (0046540444 KGM/TNE, 0046540768 colour-coated, MTK); `_sim.xml` copies without `xsi:` attributes.

## What differs from Raahe Tilkku
- VM-01: InterchangeSender `00372389445751` → SNDPRT/SNDPFC/SNDPRN `LI`/`LF`/`0000086245`.

## Sample check
By hand: E1EDKA1 AG 8387920, LF 0003003, E1EDK02 002 45725J / 45811J, DATUM = end of the 718 range (20261122, 20270117).

## Open questions
See the Raahe spec (same questions, same build logic).

## Decisions
| Date | Question | Answer | Impact |
|---|---|---|---|
| 2026-11-16 | Spec missing in the Raahe zip | User added the 1002257 zips; the shared spec is copied into this folder | Rows refer to the 1002257 sheet |
| 2026-11-16 | Folder and name | `11_ORDRSP_HameenlinnaTilkku-to-Tibnor`; `Map_HammelinnaTilkkuHub_TibnorS4_OrderConfirmation_ORDRSP` (user chose the spelling 'Hammelinna', as the Metocs mappings) | `.mmap` / zip name |
| 2026-11-16 | The spec covers both Tilkku mills: one mapping for both? | **One mapping per mill** (user: "Raahe only" for the Raahe mapping; the 4 Hämeenlinna Tilkku zips get their own mappings) | VM-01 = Hämeenlinna Tilkku GLN only |
| 2026-11-16 | Control record | As Metocs ORDRSP (my default, stated to the user): `getProperty` SNDPOR / RCVPOR / RCVPRN, STD constants, STDVRS `93A` from the sample | iFlow sets the properties |
| 2026-11-16 | iFlow steps | None: mapping only (user) | One OrderResponseMessage per message assumed, as Metocs |
| 2026-11-16 | Price fields | `context = Item` instead of the PO filter pattern (no qualifier to filter on) | An Item without Price stays aligned |
