# Hämeenlinna Tilkku hub Invoice → Tibnor INVOIC / INVOIC01

- **Mapping name:** `Map_HammelinnaTilkkuHub_TibnorS4_Invoice_INVOIC` (user, 2026-11-16)
- **Interface:** 1002743 · IN-14531 – Tibnor SSABEuropeHameenlinnaTilkku [86245] EDI INVOIC in. No iFlow known (mapping only).
- **Spec source:** `1002663_INVOIC_Tilkku-to-Tibnor_MappingSpec_v0.1.xlsx` (shared spec, copied here; see `Spec is in 1002663.txt`)
- **Design:** identical to the Raahe Tilkku mapping, `mappings/9_INVOIC_RaaheTilkku-to-Tibnor/spec.md`. The logic is `build(mill)` in `mappings/9_INVOIC_RaaheTilkku-to-Tibnor/build_mapping.py`; this folder's `build_mapping.py` passes the values of this mill. Schemas and scripts are the same files.
- **Samples:** 1 set (122620723, coil); `_sim.xml` copy.

## What differs from Raahe Tilkku
- VM-01: InterchangeSender `00372389445751` → `LI`/`LF`/`0000086245`, E1EDKA1 LF / RE PARTN `86245`. The sample has no MonetaryAmount 165/260, so no E1EDK05.

## Sample check
By hand: no E1EDK05, RE NAME1 `SSAB EUROPE OY/0500`, IDTNR 385081, BETRG 3802.50, SUMME 4772.14 as in the spec sample values.

## Open questions
See the Raahe spec (same questions, same build logic).

## Decisions
| Date | Question | Answer | Impact |
|---|---|---|---|
| 2026-11-16 | Folder and name | `13_INVOIC_HameenlinnaTilkku-to-Tibnor`; `Map_HammelinnaTilkkuHub_TibnorS4_Invoice_INVOIC` (user chose the spelling 'Hammelinna', as the Metocs mappings) | `.mmap` / zip name |
| 2026-11-16 | The spec covers both Tilkku mills: one mapping for both? | **One mapping per mill** (user: "Raahe only" for the Raahe mapping; the 4 Hämeenlinna Tilkku zips get their own mappings) | VM-01 = Hämeenlinna Tilkku GLN only |
| 2026-11-16 | Control record | As Metocs INVOIC (my default, stated to the user) | iFlow sets the properties |
| 2026-11-16 | E1EDK05 (#17) | Built as the spec says (Assumed), for both mills; constants as today | OP-06 stays open |
| 2026-11-16 | VM-04 | Only the confirmed OY row | OP-08 |
| 2026-11-16 | iFlow steps | None: mapping only (user) | — |

- **2026-11-24 Segment-level filters (v1.0.1, rule from the user's ORDERS v1.2.0 feedback, L2).** EDI_DC40 ← createIf(is_mill), sender fields constants; E1EDKA1 (LF) and E1EDKA1[1] (RE) ← createIf(is_mill), PARTN constant. (logic shared with INVOIC_RaaheTilkku-to-Tibnor)
  - Kept as chains: E1EDK01 (is_380 with CURCY), E1EDK05 (sum condition), item qualified values, header values.
