# CHANGELOG — Map_HammelinnaMetocsHub_TibnorS4_Invoice_INVOIC

## 1.0.0 — 2026-11-13
- First build from `25224_INVOIC_HameenlinnaMetocs-to-Tibnor_MappingSpec_v0.1.xlsx`: rows 1–29, as 77 target mappings.
- Source `Harmonized_Mill_Invoice_0_0_4_AoC.xsd` (Invoice, no namespace). Target `INVOIC.INVOIC01.xsd` (INVOIC01).
- Standard functions only, using the user's PO filter pattern and the ORDRSP conventions. No UDF.
- Simulator copies `samples/*/Input_*_sim.xml` added.
- Checks passed: paths, well-formed XML, zip layout, no forbidden strings. The self-test passes.
- The rules were checked in Python against the 5 expected IDocs. Everything matches except ZEILE for METOCSTO (assumption A1).
- Not yet tested in CPI. Assumptions A1–A7 are in spec.md.
