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
            source=Link("xsd", ["Ordrsp_1_0_0.xsd", "src/main/resources/xsd", "OrdrspInterchange"]),
            target=Link("xsd", ["ORDRSP.ORDERS02.xsd", "src/main/resources/xsd", "ORDERS01"]),
            namespaces=[(NS, NS_URI)])
C, F = b.const, b.fn


def S(path: str):
    """Source field; ns0: on every element step, attributes unprefixed (CONFIRMED by import test)."""
    return b.src("/" + "/".join(s if s.startswith("@") else f"{NS}:{s}" for s in path.strip("/").split("/")))


def eq(a, value):
    return F("stringEquals", a, C(value))


def each(v):
    """PO pattern: one value per context -> removeContexts -> SplitByValue (Each Value)."""
    return F("SplitByValue", F("removeContexts", v), type="0")


def by_type(node, value, field=None):
    """Value of node (or node/field) where node/@Type = value. PO D_7140 pattern: mapWithDefault on both inputs."""
    val = S(f"{node}/{field}") if field else S(node)
    return F("ifWithoutElse", eq(F("mapWithDefault", S(f"{node}/@Type"), default_value=""), value),
             F("mapWithDefault", val, default_value=""), keepss="false")


M = "/OrdrspInterchange/OrderResponseMessage"
IT = f"{M}/Item"
T = "/ORDERS01/IDOC"

# ---- header values --------------------------------------------------------------------
po_no = F("removeContexts", F("ifWithoutElse", eq(S(f"{M}/Reference/@Type"), "CO"),
                              S(f"{M}/Reference/RefNo"), keepss="false"))                     # #8, #10, #16
is_doc_date = eq(S(f"{M}/DocumentId/Date/@Type"), "137")
is_metocs = F("startWith2", S(f"{M}/Header/ApplicationId"), C("METOCS"))                      # VM-01

# ---- control record EDI_DC40 (#1-7) -----------------------------------------------------
b.map("/ORDERS01", C(""))
b.map(T, C(""))
b.map(f"{T}/@BEGIN", C("1"))
D = f"{T}/EDI_DC40"
b.map(D, C(""))
b.map(f"{D}/@SEGMENT", C("1"))
b.map(f"{D}/TABNAM", C("EDI_DC40"))                       # mandatory, as reference CLFMAS02
b.map(f"{D}/DIRECT", C("2"))                              # mandatory, inbound, as reference CLFMAS02
b.map(f"{D}/IDOCTYP", C("ORDERS01"))
b.map(f"{D}/MESTYP", C("ORDRSP"))
b.map(f"{D}/STD", C("E"))                                 # OP-06 (Q4)
b.map(f"{D}/STDVRS", C("96A"))
b.map(f"{D}/STDMES", C("ORDRSP"))
b.map(f"{D}/SNDPOR", F("getProperty", C("SNDPOR")))       # Q3, as reference CLFMAS02
b.map(f"{D}/SNDPRT", F("ifWithoutElse", is_metocs, C("LI"), keepss="false"))
b.map(f"{D}/SNDPFC", F("ifWithoutElse", is_metocs, C("LF"), keepss="false"))
b.map(f"{D}/SNDPRN", F("ifWithoutElse", is_metocs, C("0000080008"), keepss="false"))
b.map(f"{D}/SNDLAD", S(f"{M}/Header/InterchangeSender"))
b.map(f"{D}/RCVPOR", F("getProperty", C("RCVPOR")))
b.map(f"{D}/RCVPRT", C("LS"))
b.map(f"{D}/RCVPRN", F("getProperty", C("RCVPRN")))       # OP-07
b.map(f"{D}/RCVLAD", S(f"{M}/Header/InterchangeRecipient"))

# ---- header segments (#8-11) ------------------------------------------------------------
b.map(f"{T}/E1EDK01", C(""))
b.map(f"{T}/E1EDK01/@SEGMENT", C("1"))
b.map(f"{T}/E1EDK01/BELNR", po_no)
b.map(f"{T}/E1EDK03", F("createIf", is_doc_date))         # optional container: createIf
b.map(f"{T}/E1EDK03/@SEGMENT", C("1"))
b.map(f"{T}/E1EDK03/IDDAT", C("012"))
b.map(f"{T}/E1EDK03/DATUM", F("ifWithoutElse", is_doc_date, S(f"{M}/DocumentId/Date"), keepss="false"))
b.map(f"{T}/E1EDK02", F("createIf", eq(S(f"{M}/Reference/@Type"), "CO")))   # QUALF 001
b.map(f"{T}/E1EDK02/@SEGMENT", C("1"))
b.map(f"{T}/E1EDK02/QUALF", C("001"))
b.map(f"{T}/E1EDK02/BELNR", po_no)
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
is_718 = F("and", eq(S(f"{IT}/Date/@Type"), "55"), eq(S(f"{IT}/Date/@Format"), "718"))
conf_date = each(F("ifWithoutElse", is_718, F("substring", S(f"{IT}/Date"), start="9", count="8"),
                   keepss="false"))                    # PO D_2380: end of 'YYYYMMDD-YYYYMMDD'
art_in = each(by_type(f"{IT}/AddArticleNo", "IN"))    # PO D_7140

P = f"{T}/E1EDP01"
b.map(P, F("removeContexts", F("ifWithoutElse", keep_item, C(""), keepss="false")))
b.map(f"{P}/@SEGMENT", C("1"))
b.map(f"{P}/POSEX", line_no)
b.map(f"{P}/MENGE", qty)
b.map(f"{P}/MENEE", F("iF", C("MTR"), eq(unit, "M"), unit))   # #15; iF pins: then, condition, else
b.map(f"{P}/E1EDP02", C(""))
b.map(f"{P}/E1EDP02/@SEGMENT", C("1"))
b.map(f"{P}/E1EDP02/QUALF", C("001"))
# header PO number once per Item: useOneAsMany(value, all LineNo in one context, LineNo per Item)
b.map(f"{P}/E1EDP02/BELNR", F("useOneAsMany", po_no, F("removeContexts", S(f"{IT}/LineNo")), S(f"{IT}/LineNo")))
b.map(f"{P}/E1EDP02/ZEILE", line_no)
b.map(f"{P}/E1EDP03", F("createIf", is_718))              # #18: only items with a format-718 date
b.map(f"{P}/E1EDP03/@SEGMENT", C("1"))
b.map(f"{P}/E1EDP03/IDDAT", C("001"))
b.map(f"{P}/E1EDP03/DATUM", conf_date)
b.map(f"{P}/E1EDP20", C(""))                              # one schedule line per item
b.map(f"{P}/E1EDP20/@SEGMENT", C("1"))
b.map(f"{P}/E1EDP20/WMENG", qty)
b.map(f"{P}/E1EDP20/EDATU", conf_date)
b.map(f"{P}/E1EDP19", F("createIf", eq(S(f"{IT}/AddArticleNo/@Type"), "IN")))
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
