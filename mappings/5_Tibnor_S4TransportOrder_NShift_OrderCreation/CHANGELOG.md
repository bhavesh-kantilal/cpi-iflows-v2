# CHANGELOG — Map_TibnorS4_NShift_TransportOrder_Book

## 1.0.0 — 2026-11-13
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
