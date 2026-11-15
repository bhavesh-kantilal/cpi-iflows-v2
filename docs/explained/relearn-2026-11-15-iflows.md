# Re-learn 2026-11-15 (2): with the iFlows

**New material:** 14 iFlow exports added by the user (`_reference/iflows/`, imported with `tools/iflow_import.py`). The reference set is now **31 distinct mappings**: 26 originals (L1, 16 of them new; some are other versions of existing ones, e.g. the FSAP variant of I0115) plus 5 generated (L3). **Every one of your mappings now has its iFlow**, so each pattern is read together with the steps before and after it (`_reference/CATALOG.md` §4). All numbers are counted by `tools/catalog.py`. **No rule was changed;** proposals and questions are at the end.

## 1. Rules checked again (old L1 → with the new L1)
| Rule | Evidence in the 26 originals | Verdict |
|---|---|---|
| **R1** SplitByValue "value change" needs sorted input → XSLT sort before the mapping | Value change appears in only 2 mappings (ACC and INV, each in GSAP and FSAP I0115). **Every time, the iFlow runs XSLT `SortByTaxLines` (sorts by `taxCode`, `number(percentage)`) directly before it.** The unused OTM copy has no step | **Fully supported (L1 + L2)** |
| **R3** lift with `context=`, `removeContexts` only when all contexts must go | Both styles are used: `context=` 132× (INV 45, SUP 13, JE 5, MAT/Equipment/FunctionalLocation/DIR 4–5 each), `removeContexts` 121× (mostly ACC 28 per copy, INV 11, SUP 7). The newer SmarTeam mappings (Equipment, FunctionalLocation) mix both | **Supported as a preference (L2)**; L1 shows both in use |
| **R4** `mapWithDefault` after a context change only with ≤ 1 occurrence | 12 uses, all on header fields (ACC `customField_Numeric1`, SUP BankAccountID) | **Supported** |
| **R5** `counter` for missing line numbers | 35 uses, all item numbers in ACC / JE / INV (`ini=2, inc=2` where line 1 is the vendor line) | **Supported** |
| CopyValue for header → item | 112 uses; `useOneAsMany` only 7× (repeating per child value) | **Supported** |
| FixValues Use Key (2) | 36× `2`/empty, 3× `1` | **Supported** |
| Clean layout, no overlaps | 0 overlaps in all 26 SAP layouts | **Supported** |
| Attribute context | 4 uses (MAT and its I2018 copy, DIR in I2051_P and I2052_P): attribute paired with its own element | **Supported** |

## 2. New patterns: what your iFlows do around the mappings
1. **Monitoring before every mapping:** `Set Monitoring Identifiers` → `Log Payload` → `logCustomHeaders.groovy` precede every mapping in the new iFlows. **Not our concern in the mapping,** but the standard frame of every iFlow.
2. **Filter / route before the mapping, not inside it:** an `ExclusiveGateway` ("Allowed?", "Allowed Companies") decides before the mapping runs (I0541, I0544 JDBC, I0161).
3. **Split before the mapping:** `Splitter` "Internal Order Splitter" (I0541) and "Splitter Account Information" (I0544 BP), so the mapping handles one object per message. This matches what we noted for ORDRSP OP-08 and the NShift house waybills.
4. **XSLT preprocessing for logic that spans segments:** I0161 XSLT `LowestLevel` runs before `MapProjectToMedius` and derives an `ACTIVE` flag (project status `I0046` / `INACTIVE`), the owner from `E1BPPAREX` (`ZZOWNER`), and the maximum WBS level. The mapping then only maps.
5. **XSLT filter driven by an exchange property:** I0544 BP XSLT `AccountingInformationAllowed` removes every `AccountingInformation` whose `CompanyID` ≠ property `CH_CompanyCode`.
6. **Cleaning before the mapping:** `removeXSINil` (XSLT) before `MapBPToDDSJDBC`, and `CleanNamespace.groovy` before `SupplierMastertoMedius`.
7. **Post-processing after the mapping:** `ReplaceWithVirtualCompany.groovy` (I0541, I0544 BP); a second mapping chained after the first (I0161: `MapProjectToMedius` → `MapToUserResponsible`); XSLT aggregation after INV (`SubsequentCreditDebit`, `XSL_Group_ToMakeUniqueItems`).
8. **New function `exists`:** I0541 › `InternalOrdertoMediusMap` (see Q7). It's the only function not yet in FORMAT_NOTES.

## 3. Questions to you
- **Q7 — `exists`.** iFlow `I0541_InternalOrder_FSAP_Medius_JMSToREST` › `InternalOrdertoMediusMap` › target `/__$$RoOt_ArRaY$$__/isActive` ← `iF('true', or(exists(…/InternalOrder/Status/StatusCreatedIndicator), exists(…/InternalOrder/Status/StatusReleasedIndicator)), 'false')`. Is `exists` your standard for "is this node present" (instead of `mapWithDefault` + `stringEquals`, or `not(isNil)` as in SUP)?
- **Q8 — Clean Namespace.** iFlow `I0544_BusinessPartner_FSAP_Medius_JMSToREST` › script `CleanNamespace.groovy` runs before `SupplierMastertoMedius`. Which namespace problem does it solve? Is it an alternative to the `ns0:`-on-every-step approach we used for ORDRSP/DESADV?
- **Q9 — XSLT vs UDF vs graphical.** iFlow `I0161_Project_…` › XSLT `LowestLevel` derives `ACTIVE`, the owner and the lowest WBS level before `MapProjectToMedius`. Is your rule "logic across segments or levels → XSLT preprocessing, the message mapping stays field-to-field"? When do you pick an XSLT step and when a UDF?
- **Q10 — Split before mapping.** iFlows `I0541_…` (Internal Order Splitter) and `I0544_BusinessPartner_FSAP_Medius_JMSToREST` (Splitter Account Information): is "one business object per message, split in the iFlow" your default? That would answer ORDRSP OP-08 (several confirmations per interchange) and NShift OP-01 (one booking per house waybill).
- **Q11 — removeXSINil.** iFlow `I0544_BusinessPartner_FSAP_StreamServeDDS_JMSToJDBC` › XSLT `removeXSINil` before `MapBPToDDSJDBC`: what goes wrong with `xsi:nil` (the mapping, or the JDBC adapter)?

## 4. Proposals (need your OK; collected in REVIEW.md)
- **R1–R5** (unchanged, now with more evidence).
- **R6 (after Q9/Q10):** "Before building a mapping, decide what belongs in the iFlow: sorting (R1), splitting into one object per message, filtering by exchange property, logic across segments (XSLT). The mapping stays field-to-field." Every such iFlow step is named in the mapping's `spec.md`, and the user is told: "Bhavesh, this needs an iFlow step …".
- **FORMAT_NOTES:** add `exists` (1 input, a boolean "node present"), once Q7 is answered.
