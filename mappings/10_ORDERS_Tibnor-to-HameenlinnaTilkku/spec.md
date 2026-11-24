# Tibnor ORDERS02 → Hämeenlinna Tilkku hub OrdersMessage

- **Mapping name:** `Map_TibnorS4_HammelinnaTilkkuHub_PurchaseOrder_ORDERS02` (user, 2026-11-16)
- **Interface:** 1002249 – Tibnor SSABEuropeHameenlinnaTilkku [86245] EDI ORDERS out. No iFlow known (mapping only).
- **Spec source:** `1002249_ORDERS_Tibnor-to-HameenlinnaTilkku_MappingSpec_v0.1.xlsx` (same rules as Raahe 1002129, except Property ZMA)
- **Design:** identical to the Raahe Tilkku mapping, `mappings/6_ORDERS_Tibnor-to-RaaheTilkku/spec.md`. The logic is `build(mill)` in `mappings/6_ORDERS_Tibnor-to-RaaheTilkku/build_mapping.py`; this folder's `build_mapping.py` passes the values of this mill. Schemas and scripts are the same files.
- **Samples:** 5 sets (all Tibnor OY, ship-to 1683422 Järvenpää); Windows-1252 IDocs with `_utf8.xml` simulator copies (all well-formed).

## What differs from Raahe Tilkku
- VM-01: vendor `0000086245` → InterchangeRecipient `00372389445751`, MessageRoutingOutbound `HAMF.M.TILKKU` + suffix; Party MF `86245`. **Property ZMA is not sent** (OP-02: only the Raahe Implema mapping adds it), so an item has up to 14 Property occurrences instead of 15.

## Sample check
Rules emulated in Python: Properties, Package, Quantity LL equal the 5 expected outputs. One order difference: PO 46540444 item 10 has Measurements LN, TH, WD today; the mapping writes LN, WD, TH (Q1 in the Raahe spec).

## Open questions
See the Raahe spec (same questions, same build logic).

## Decisions
| Date | Question | Answer | Impact |
|---|---|---|---|
| 2026-11-16 | Folder and name | `10_ORDERS_Tibnor-to-HameenlinnaTilkku`; `Map_TibnorS4_HammelinnaTilkkuHub_PurchaseOrder_ORDERS02` (user chose the spelling 'Hammelinna', as the Metocs mappings) | `.mmap` / zip name |
| 2026-11-16 | The spec covers both Tilkku mills: one mapping for both? | **One mapping per mill** (user: "Raahe only" for the Raahe mapping; the 4 Hämeenlinna Tilkku zips get their own mappings) | VM-01 = Hämeenlinna Tilkku vendor only; ZMA not sent |
| 2026-11-16 | Characteristics sit beside the items, linked by POSEX | User: "try to solve it with the graphical mapping in a UDF and call it out" | UDF `itemCharacteristic` + standard per-item chains; call-out in the Raahe spec |
| 2026-11-16 | OP-14 city upper case | **Standard `toUpperCase`** ('Sölvesborg' → 'SÖLVESBORG', today 'SöLVESBORG') | No UDF; differs from today for ä/ö/å |
| 2026-11-16 | iFlow steps | None: mapping only (user) | No sort/XSLT step; all logic in the mapping |
| 2026-11-16 | Environment suffix PRD/TST (#7–8) | Same as Metocs ORDERS Q3: exchange property `HubEnvironment` (my default, stated to the user) | iFlow / simulator must set the property |
| 2026-11-16 | Values as sent | Today's output keeps leading spaces of VALUE_TXT; the UDF does not trim | like-for-like |
| 2026-11-16 | Not well-formed sample originals | Escaped only in the `_utf8` copies | Originals unchanged |

- **2026-11-24 Segment-level filters (v1.0.1, rule from the user's ORDERS v1.2.0 feedback, L2).** Party BY/MF/CN ← createIf(E1EDKA1/PARVW [context IDOC] = AG/LF/WE), fields 1:1 from that E1EDKA1; TermsOfDelivery ← createIf(E1EDK17/QUALF [context IDOC] = 001), LKOND/LKTEXT 1:1. Change: a Party is now created only when its partner segment exists (before: always); TermsOfDelivery for every QUALF 001 segment (before: only when LKOND had a value). (logic shared with ORDERS_Tibnor-to-RaaheTilkku)
  - Kept as chains: Header InterchangeSender/Recipient/MessageRoutingOutbound (header fields from the AG/LF partner), the ship-to copied onto every item (CopyValue of header values), DocumentId/Date (E1EDK03 IDDAT 012), the item characteristics (itemCharacteristic UDF) and ArticleNo.
