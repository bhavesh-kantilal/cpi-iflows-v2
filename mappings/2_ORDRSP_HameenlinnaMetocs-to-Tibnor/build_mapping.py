"""Build Map_HammelinnaMetocsHub_TibnorS4_OrderConfirmation_ORDRSP.

Run:  py -I mappings/2_ORDRSP_HameenlinnaMetocs-to-Tibnor/build_mapping.py
Rows (#) refer to sheet 'Mapping' of 25207_ORDRSP_HameenlinnaMetocs-to-Tibnor_MappingSpec_v0.1.xlsx.
Design and decisions: spec.md.

v1.0.1 follows the user's existing PO mapping of the same hub source (towards EDI), see spec.md:
  * no context settings on source fields, no UDF
  * item node:   removeContexts(ifWithoutElse(condition, const ""))
  * item values: ifWithoutElse(@Type filter, value) -> removeContexts -> SplitByValue(Each Value)
Source paths carry ns0: on every element step (import test of v1.0.0, variant NsAllSteps).
"""
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE.parent.parent / "tools"))
sys.stdout.reconfigure(encoding="utf-8")

from cpimm.build import Builder                       # noqa: E402
from cpimm.check import check_build, check_paths      # noqa: E402
from cpimm.model import Link                          # noqa: E402
from cpimm.package import package                     # noqa: E402

NAME = "Map_HammelinnaMetocsHub_TibnorS4_OrderConfirmation_ORDRSP"
NS_URI, NS = "http://www.ruukki.com/schemas/eai/internal/production/eruukki", "ns0"

b = Builder(NAME,
            # namespaced XSD: 4th elem = targetNamespace, as CPI writes it (feedback v1.0.1)
            source=Link("xsd", ["Ordrsp_1_0_0.xsd", "src/main/resources/xsd", "OrdrspInterchange", NS_URI]),
            target=Link("xsd", ["ORDRSP.ORDERS02.xsd", "src/main/resources/xsd", "ORDERS01"]),
            namespaces=[(NS, NS_URI)])
C, F = b.const, b.fn


def _ns(path: str) -> str:
    return "/" + "/".join(s if s.startswith("@") else f"{NS}:{s}" for s in path.strip("/").split("/"))


def S(path: str, context: str | None = None):
    """Source field; ns0: on every element step, attributes unprefixed (CONFIRMED by import test).
    context: needed for an attribute compared with the value of its OWN element (Date/@Type vs Date):
    an attribute's default context is its element, the element's value sits in the parent's context
    (user's CPI fix, feedback v2 2026-11-15)."""
    return b.src(_ns(path), context=_ns(context) if context else None)


def eq(a, value):
    return F("stringEquals", a, C(value))


def each(v):
    """PO pattern: one value per context -> removeContexts -> SplitByValue (Each Value)."""
    return F("SplitByValue", F("removeContexts", v), type="0")


def by_type(node, value, field=None, attr_context=None):
    """Value of node (or node/field) where node/@Type = value. PO D_7140 pattern: mapWithDefault on both inputs.
    attr_context: set when the value is the node itself (AddArticleNo), see S()."""
    val = S(f"{node}/{field}") if field else S(node)
    attr = S(f"{node}/@Type", attr_context)
    # R4 (CLAUDE.md): no mapWithDefault after a context change when the new context can hold several occurrences
    key = attr if attr_context else F("mapWithDefault", attr, default_value="")
    return F("ifWithoutElse", eq(key, value),
             F("mapWithDefault", val, default_value=""), keepss="false")


M = "/OrdrspInterchange/OrderResponseMessage"
IT = f"{M}/Item"
T = "/ORDERS01/IDOC"

# ---- header values --------------------------------------------------------------------
co_ref = F("ifWithoutElse", eq(S(f"{M}/Reference/@Type"), "CO"), S(f"{M}/Reference/RefNo"), keepss="false")
po_no = F("removeContexts", co_ref)                                                          # #16 (CopyValue)
# #8, #10: one value per CO reference; feeds E1EDK01/BELNR, E1EDK02 and E1EDK02/BELNR (user's CPI fix v2:
# createIf(@Type = CO) without removeContexts only saw the first Reference, so E1EDK02 001 was missing)
po_chain = each(co_ref)
is_doc_date = eq(S(f"{M}/DocumentId/Date/@Type"), "137")
is_metocs = F("startWith2", S(f"{M}/Header/ApplicationId"), C("METOCS"))                      # VM-01

# ---- control record EDI_DC40 (#1-7) -----------------------------------------------------
b.map("/ORDERS01", C(""))
b.map(T, C(""))
b.map(f"{T}/@BEGIN", C("1"))
D = f"{T}/EDI_DC40"
# segment-level filter (CLAUDE.md, user 2026-11-24): the Metocs check sits on the segment, the sender
# fields are constants. A non-Metocs message gets no control record (it could not be posted anyway).
b.map(D, F("createIf", is_metocs))
b.map(f"{D}/@SEGMENT", C("1"))
b.map(f"{D}/TABNAM", C("EDI_DC40"))                       # mandatory, as reference CLFMAS02
b.map(f"{D}/DIRECT", C("2"))                              # mandatory, inbound, as reference CLFMAS02
b.map(f"{D}/IDOCTYP", C("ORDERS01"))
b.map(f"{D}/MESTYP", C("ORDRSP"))
b.map(f"{D}/STD", C("E"))                                 # OP-06 (Q4)
b.map(f"{D}/STDVRS", C("96A"))
b.map(f"{D}/STDMES", C("ORDRSP"))
b.map(f"{D}/SNDPOR", F("getProperty", C("SNDPOR")))       # Q3, as reference CLFMAS02
b.map(f"{D}/SNDPRT", C("LI"))
b.map(f"{D}/SNDPFC", C("LF"))
b.map(f"{D}/SNDPRN", C("0000080008"))
b.map(f"{D}/SNDLAD", S(f"{M}/Header/InterchangeSender"))
b.map(f"{D}/RCVPOR", F("getProperty", C("RCVPOR")))
b.map(f"{D}/RCVPRT", C("LS"))
b.map(f"{D}/RCVPRN", F("getProperty", C("RCVPRN")))       # OP-07
b.map(f"{D}/RCVLAD", S(f"{M}/Header/InterchangeRecipient"))

# ---- header segments (#8-11) ------------------------------------------------------------
b.map(f"{T}/E1EDK01", C(""))
b.map(f"{T}/E1EDK01/@SEGMENT", C("1"))
b.map(f"{T}/E1EDK01/BELNR", po_chain)
b.map(f"{T}/E1EDK03", F("createIf", is_doc_date))         # optional container: createIf
b.map(f"{T}/E1EDK03/@SEGMENT", C("1"))
b.map(f"{T}/E1EDK03/IDDAT", C("012"))
b.map(f"{T}/E1EDK03/DATUM", F("ifWithoutElse", is_doc_date, S(f"{M}/DocumentId/Date"), keepss="false"))
# QUALF 001, one per CO reference: segment-level filter, @Type lifted to the message context; BELNR 1:1
b.map(f"{T}/E1EDK02", F("createIf", eq(S(f"{M}/Reference/@Type", M), "CO")))
b.map(f"{T}/E1EDK02/@SEGMENT", C("1"))
b.map(f"{T}/E1EDK02/QUALF", C("001"))
b.map(f"{T}/E1EDK02/BELNR", S(f"{M}/Reference/RefNo"))
b.map(f"{T}/E1EDK02[1]", C(""))                           # QUALF 002: DocumentNo is mandatory
b.map(f"{T}/E1EDK02[1]/@SEGMENT", C("1"))
b.map(f"{T}/E1EDK02[1]/QUALF", C("002"))
b.map(f"{T}/E1EDK02[1]/BELNR", S(f"{M}/DocumentId/DocumentNo"))

# ---- items (#12-21) ------------------------------------------------------------------------
# #12 as the PO item node G_SG26: Property type 12 and text not 'ITEM CANCELLED'.
keep_item = F("and", eq(S(f"{IT}/Property/@Type"), "12"),
              F("not", eq(S(f"{IT}/Property/PropertyText"), "ITEM CANCELLED")))
line_no = F("formatNumber", S(f"{IT}/LineNo"), nformat="#", separator=".")                  # '010' -> '10'
qty = each(by_type(f"{IT}/Quantity", "21", "QuantityValue"))
unit = each(by_type(f"{IT}/Quantity", "21", "MeasureUnit"))
is_718 = F("and", eq(S(f"{IT}/Date/@Type", IT), "55"), eq(S(f"{IT}/Date/@Format", IT), "718"))   # context Item (v2)
# User feedback 2026-11-15 (Feedback.docx, CPI screenshot): E1EDP03, DATUM and EDATU all come from the
# filtered format-718 Date chain; the segment is NOT built with createIf (SUPPRESS hid other items' segments).
date_718 = each(F("ifWithoutElse", is_718, S(f"{IT}/Date"), keepss="false"))
# End of the range 'YYYYMMDD-YYYYMMDD', after the filter (only 718 values reach it): library UDF substringSafe
conf_date = b.udf("substringSafe", "substringSafe", date_718, C("9"), C("17"))
art_in = each(by_type(f"{IT}/AddArticleNo", "IN", attr_context=IT))    # PO D_7140; @Type context Item (v2)

P = f"{T}/E1EDP01"
b.map(P, F("removeContexts", F("ifWithoutElse", keep_item, C(""), keepss="false")))
b.map(f"{P}/@SEGMENT", C("1"))
b.map(f"{P}/POSEX", line_no)
b.map(f"{P}/MENGE", qty)
# #15: FixValues 'Use Key' (user feedback 2026-11-15): M -> MTR, any other unit passes unchanged.
# Use Key = vmstrategy 2 with empty default (FORMAT_NOTES §5 Q1, MAT Status/Description = "Use Key").
b.map(f"{P}/MENEE", b.table("FixValues", unit, [("M", "MTR")], default="", strategy="2"))
b.map(f"{P}/E1EDP02", C(""))
b.map(f"{P}/E1EDP02/@SEGMENT", C("1"))
b.map(f"{P}/E1EDP02/QUALF", C("001"))
# header PO number on every item: CopyValue index 0 (user feedback 2026-11-15, instead of useOneAsMany)
b.map(f"{P}/E1EDP02/BELNR", F("CopyValue", po_no, nnumber="0"))
b.map(f"{P}/E1EDP02/ZEILE", line_no)
# #18: one per format-718 date, the same Item-context chain as DATUM/EDATU (user 2026-11-15: keep segment and
# fields consistent; without the context the segment count is right by luck, the values are not)
b.map(f"{P}/E1EDP03", date_718)
b.map(f"{P}/E1EDP03/@SEGMENT", C("1"))
b.map(f"{P}/E1EDP03/IDDAT", C("001"))
b.map(f"{P}/E1EDP03/DATUM", conf_date)
b.map(f"{P}/E1EDP20", C(""))                              # one schedule line per item
b.map(f"{P}/E1EDP20/@SEGMENT", C("1"))
b.map(f"{P}/E1EDP20/WMENG", qty)
b.map(f"{P}/E1EDP20/EDATU", conf_date)
b.map(f"{P}/E1EDP19", art_in)                             # same chain as IDTNR, no createIf (user feedback)
b.map(f"{P}/E1EDP19/@SEGMENT", C("1"))
b.map(f"{P}/E1EDP19/QUALF", C("001"))
b.map(f"{P}/E1EDP19/IDTNR", art_in)

m = b.finish()

if __name__ == "__main__":
    z = package(m, HERE, HERE / "build")
    errs = check_build(z, NAME) + check_paths(m, HERE / "build" / NAME)
    print(z.name, f"{len(m.targets)} targets")
    print("\n".join(errs) if errs else "ALL CHECKS PASSED")
    sys.exit(1 if [e for e in errs if not e.startswith("NOTE")] else 0)
