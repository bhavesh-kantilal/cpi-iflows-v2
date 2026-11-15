# CHANGELOG — Map_TibnorS4_NShift_TransportOrder_Book

## 1.0.2 — 2026-11-15 11:43 CET
- Applies the rules accepted in the review of 2026-11-15:
  - `Communication` (phone, e-mail) and `Tod/location` are straight maps under their `createIf` segments.
  - New editor layout (no overlaps).
- The output should be unchanged. Re-test in CPI recommended.

## 1.0.1 — 2026-11-13 14:55 CET
- Fix: the target WSDL `NShift_ConsignmentWS.wsdl` lost the inlined XSDs' `xmlns:tns` declarations, so CPI could not resolve any NShift type (Consignment, Part, GoodsItem, …). It is regenerated with the fixed `tools/wsdl_inline.py`; the schema set now compiles.
- New build check: XSD/WSDL type and element references must resolve (`check.py: schema_ref_errors`). The v1.0.0 zip fails it with 151 errors; v1.0.1 and all other mappings pass.
- The mapping logic is unchanged. The self-test passes.

## 1.0.0 — 2026-11-13 13:57 CET
- First build. There is no source spec: the rules are a best guess, written up as `S4TM-NShift_TransportOrder_Book_MappingSpec_v0.1.xlsx` and `spec.md` (assumptions A1–A14, open points OP-01–OP-12).
- Source: S/4 TM `TransportationOrderRequest` (WSDL). Target: nShift ConsignmentWS `book` (self-contained WSDL with the two downloaded nShift XSDs inlined by the new `tools/wsdl_inline.py`).
- 73 target mappings. UDFs `goodsItemFlags.groovy` (goods rows + SSCC) and `toLocalDate.groovy` (UTC → local date).
- Checks passed:
  - paths
  - target namespace prefixes checked against the XSD
  - well-formed XML
  - zip layout
  - no forbidden strings
- The self-test passes. The expected result for `Input.XML` is in spec.md (Python model).
- Not yet tested in CPI. The Groovy UDFs have not run anywhere yet.
