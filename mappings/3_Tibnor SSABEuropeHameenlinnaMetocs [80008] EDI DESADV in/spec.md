# Hämeenlinna Metocs hub DeliveryBatch → Tibnor DESADV / DELVRY01

- **Mapping name:** `Map_HammelinnaMetocsHub_TibnorS4_DeliveryNotice_DESADV`
- **Spec source:** `25208_DESADV_HameenlinnaMetocs-to-Tibnor_MappingSpec_v0.1.xlsx` (draft v0.1, 12 Nov 2026), integration ID 25208 / IN-14525
- **Source:** `schemas/DeliveryBatch_0_8_1.xsd`, root `DeliveryBatch`, targetNamespace `http://www.ruukki.com/schemas/eai/rucomef/otc`, qualified. As ORDRSP: `ns0:` on every element step, and the namespace URI as the 4th link elem (FORMAT_NOTES §2.2, CONFIRMED on ORDRSP).
- **Target:** `schemas/DESADV.DELVRY01.xsd`, IDoc root `DELVRY01`
- **Old PO mapping:** `Reference/PO-Mapping_FIN_DeliveryBatch_to_DESADV96A_TIBNOR.txt`. It writes EDIFACT per bundle (SinglePart). The grouping per heat was done afterwards by Implema, so the PO mapping has no logic to reuse for it.
- **Samples:** 5 sets in `Samples/<date>_<cargo id>/`: input, Implema EDIFACT intermediate, expected IDoc.
  - `Input_*_sim.xml` are simulator copies without `xmlns:xsi` / `xsi:schemaLocation` (`tools/sim_copy.py`).
  - The folder is still `Samples` (capital S): renaming it was refused because the folder was in use. Rename it to `samples` when convenient.

## How I read the sheet
- Sheet "Mapping": `#`, `Target field`, `Occ.`, `Source`, `Target rule`, `Sample value`, `Status`, `Notes`.
  - `Reference[ReferenceType='CargoId']` = the Reference whose child element ReferenceType = CargoId.
  - Rows 11–27 are per **group** (line + heat), not per hub line.

## Design (target ← source, how)

| # | Target | Built with |
|---|---|---|
| — | `DELVRY01`, `IDOC`, `EDI_DC40`, `E1EDL20`, `E1ADRM1`, `E1EDT13`, `E1EDL11`, `E1EDL43`, `E1EDL41` | empty constant; `@BEGIN`/`@SEGMENT` = `1`; `TABNAM`/`DIRECT` = `EDI_DC40`/`2` |
| 1 | IDOCTYP / MESTYP | `DELVRY01` / `DESADV` |
| 2 | SNDPRT / SNDPFC / SNDPRN | `ifWithoutElse(startWith2(SourceSystem, 'METOCS'), const)` → LI / LF / 0000080008 |
| 3–4, 7 | SNDPOR, RCVPOR, RCVPRN / RCVPRT / STD… | as ORDRSP: `getProperty` / `LS` / `E`, `96A`, `DESADV`; REFMES not mapped |
| 5–6 | SNDLAD / RCVLAD | Header/InterchangeSender / InterchangeRecipient |
| 8 | E1EDL20-VBELN | Reference[ReferenceType='CargoId']/ReferenceId |
| 9 | E1ADRM1 LF / PARTNER_ID | `ifWithoutElse(METOCS, '80008')` |
| 10, 18, 24, 26 | NTANF, ABRDT, E1EDL43-DATUM, BSTDT | `TransformDate(DespatchDate, yyyy-MM-dd → yyyyMMdd)` (as reference INV). Item fields repeated per group with `useOneAsMany` |
| 11 | E1EDL24 | **UDF `groupByHeat`** output 0, one value per group (line + heat, in order of first appearance) |
| 12, 23, 27 | POSNR, E1EDL43-POSNR, E1EDL41-POSEX | UDF output 0 (line id) → `SplitByValue(Each Value)` |
| 13–14 | MATNR, KDMAT | UDF output 1 (CustomersArticleId) |
| 15, 22, 25 | ARKTX, E1EDL43-BELNR, E1EDL41-BSTNR | Reference[ReferenceType='BuyersOrderId']/ReferenceId, once per group (`useOneAsMany`) |
| 16 | LFIMG | UDF output 3: Meters, one bundle → as sent, several → sum without trailing decimals |
| 17 | VRKME | UDF output 6: the Meters unit (`MTR`) |
| 19 | USR01 | UDF output 4: number of bundles |
| 20 | USR03 | UDF output 5: `<Weight>;KGM;<Pieces>;PCE;<Meters>;MTR;`, same number rule |
| 21 | E1EDL11-SERNR | UDF output 2: heat number |

### UDF `scripts/groupByHeat.groovy` (user decision: one grouping UDF)
- **Inputs:** one value per SinglePart, flattened with standard functions only, no context settings:
  - line id and article: `removeContexts(useOneAsMany(line field, SinglePart, SinglePart))`
  - heat: the PO filter pattern on MaterialBatch with MaterialBatchType = Heat
  - Weight / Pieces / Meters / Meters unit: the PO filter pattern on DespatchedQuantity/ValueName
- **Outputs:** 7, one value per group (multi-output UDF as ACC `splitStringOTV`). Children take `SplitByValue(Each Value)` of an output; output 0 is a plain arg.
- The UDF stops with a clear error if the inputs are not one value per bundle. That happens if a bundle lacks a Heat batch or a quantity, instead of mis-pairing.
- **Number rule:** `BigDecimal` sum with `stripTrailingZeros` (`9590.000`+… → `9590`). If a sum had real decimals, they are kept (`216.5`) and not rounded.

### Sample check
A Python model of exactly these rules reproduces all **11 E1EDL24 of the 5 expected IDocs**: POSNR, MATNR, LFIMG, USR01, USR03, SERNR. Example: 51762 has 3 lines → 4 items, and line 20 has 2 heats. Header and control-record values match too.
- The Groovy UDF itself has not run yet (no Groovy runtime here). The CPI simulator is the first real test.

## Assumptions for later (user, 2026-11-13: "keep them as assumptions for later")
- **A1 Grouping key (OP-04, OP-15):** line + MaterialBatch of type `Heat`, exactly one Heat batch per bundle, SinglePartLevel 1 only (all samples). PO's `concatMaterialBatchId` is unknown.
- **A2 Number format (OP-06):** the "as sent / sum without decimals" rule copies Implema. Whether Tibnor needs it is open.
- **A3 Dates (OP-09):** ABRDT, E1EDL43-DATUM and BSTDT use DespatchDate (equal to the DespatchAdvice date in all samples).
- **A4 One PO per delivery (OP-13):** BuyersOrderId from the header for all groups.
- **A5 VBELN = cargo id (OP-07), ARKTX = PO number (OP-08):** as today.
- **A6 Control record** as ORDRSP (OP-10): SNDPOR from a property, today `INOBIZ`.
- **A7 Non-METOCS SourceSystem:** sender partner fields stay empty, so the mapping fails.
- **A8 One delivery per message:** one E1EDL20 (the hub root is one DeliveryBatch).

## Decisions
- **2026-11-13 Name** `Map_HammelinnaMetocsHub_TibnorS4_DeliveryNotice_DESADV` (user).
- **2026-11-13 Grouping with one Groovy UDF** (user). Everything else uses standard functions.
- **2026-11-13 Control record** as ORDRSP (user).
- **2026-11-13 Files moved:** XSDs → `schemas/`. The empty `Test/` folder is left as it is.
