# CHANGELOG — Map_HammelinnaMetocsHub_TibnorS4_DeliveryNotice_DESADV

## 1.0.0 — 2026-11-13
- First build from `25208_DESADV_HameenlinnaMetocs-to-Tibnor_MappingSpec_v0.1.xlsx`: rows 1–27, as 58 target mappings.
- Source `DeliveryBatch_0_8_1.xsd` (namespace otc: `ns0:` on every step, namespace as the 4th link elem). Target `DESADV.DELVRY01.xsd` (DELVRY01).
- E1EDL24 per line + heat via the new multi-output UDF `groupByHeat.groovy`. Everything else uses standard functions and the user's PO filter pattern.
- Simulator copies `Samples/*/Input_*_sim.xml` added.
- Checks passed: paths, well-formed XML, zip layout, UDF script present, no forbidden strings. The self-test passes.
- The rules were checked in Python against the 5 expected IDocs: 11 of 11 items match. The Groovy UDF has not run yet.
- Not yet tested in CPI. Assumptions A1–A8 are in spec.md.
