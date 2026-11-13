# CHANGELOG — Map_HammelinnaMetocsHub_TibnorS4_OrderConfirmation_ORDRSP

## 1.0.0 — 2026-11-13
- First build from `25207_ORDRSP_HameenlinnaMetocs-to-Tibnor_MappingSpec_v0.1.xlsx`: rows 1–21, as 58 target mappings.
- Source `Ordrsp_1_0_0.xsd` (OrdrspInterchange, namespace eruukki). Target `ORDRSP.ORDERS02.xsd` (ORDERS01 IDoc).
- Standard functions only, no UDFs.
- Built as **two test variants**, which differ only in the source path prefixes (spec.md, Q2):
  - `…_ORDRSP_NsAllSteps.zip`: `ns0:` on every source element step
  - `…_ORDRSP_NsRootOnly.zip`: `ns0:` on the source root only
- Checks passed for both:
  - every source and target path exists in the XSDs
  - all mandatory IDoc fields are mapped
  - all XML is well-formed
  - the zip layout matches the standalone references
  - no forbidden strings
- The self-test passes.
- Not yet tested in CPI. Open for the import test: which namespace variant works, and the item filter for skipped items (no sample has one).
