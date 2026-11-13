"""Build Map_HammelinnaMetocsHub_TibnorS4_OrderConfirmation_ORDRSP.

Run:  py -I mappings/2_ORDRSP_HameenlinnaMetocs-to-Tibnor/build_mapping.py
Rows (#) refer to sheet 'Mapping' of 25207_ORDRSP_HameenlinnaMetocs-to-Tibnor_MappingSpec_v0.1.xlsx.
Design and decisions: spec.md.

The source XSD is namespace-qualified (targetNamespace eruukki, elementFormDefault qualified).
No reference shows such a source, so v1.0.0 is built as two TEST VARIANTS that differ only in how
the source paths are prefixed (spec.md, Decisions 2026-11-13 Q2):
  NsAllSteps : /ns0:OrdrspInterchange/ns0:OrderResponseMessage/ns0:Item/ns0:LineNo
  NsRootOnly : /ns0:OrdrspInterchange/OrderResponseMessage/Item/LineNo   (pattern of the references)
After the import test only the variant that works is kept, under the plain mapping name.
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
SRC_XSD, TGT_XSD = "Ordrsp_1_0_0.xsd", "ORDRSP.ORDERS02.xsd"
NS_URI, NS = "http://www.ruukki.com/schemas/eai/internal/production/eruukki", "ns0"
VARIANTS = {"NsAllSteps": "all", "NsRootOnly": "root"}


def build(variant: str, prefix_mode: str):
    b = Builder(f"{NAME}_{variant}",
                source=Link("xsd", [SRC_XSD, "src/main/resources/xsd", "OrdrspInterchange"]),
                target=Link("xsd", [TGT_XSD, "src/main/resources/xsd", "ORDERS01"]),
                namespaces=[(NS, NS_URI)])
    C, F = b.const, b.fn

    def sp(path: str) -> str:
        """Source path with namespace prefixes. Attributes (@x) never get a prefix."""
        steps = path.strip("/").split("/")
        out = []
        for i, s in enumerate(steps):
            if s.startswith("@") or (prefix_mode == "root" and i > 0):
                out.append(s)
            else:
                out.append(f"{NS}:{s}")
        return "/" + "/".join(out)

    def S(path, context=None):
        return b.src(sp(path), context=sp(context) if context else None)

    M = "/OrdrspInterchange/OrderResponseMessage"
    IT = f"{M}/Item"
    T = "/ORDERS01/IDOC"

    def qualified(node, attr, value, field=None, ctx=None):
        """Values of node (or node/field) whose @attr = value, e.g. Reference[@Type='CO']/RefNo.
        @attr and the value are on the same queue level when field is None (Date, AddArticleNo).
        For a child field the field gets context ctx so it lines up with node/@attr."""
        val = S(f"{node}/{field}", context=ctx) if field else S(node)
        if field:
            val = F("mapWithDefault", val, default_value="")
        return F("ifWithoutElse", F("stringEquals", S(f"{node}/@{attr}"), C(value)), val, keepss="false")

    def present(v):
        """createIf condition: one value per context; empty context -> default '' -> false."""
        return F("createIf", F("not", F("stringEquals", F("mapWithDefault", v, default_value=""), C(""))))

    # ---- header values ------------------------------------------------------------------
    po_no = F("removeContexts", qualified(f"{M}/Reference", "Type", "CO", "RefNo", ctx=M))   # #8, #10, #16
    doc_date = F("removeContexts", qualified(f"{M}/DocumentId/Date", "Type", "137"))         # #9
    app_id = S(f"{M}/Header/ApplicationId")
    is_metocs = F("startWith2", app_id, C("METOCS"))                                          # VM-01

    # ---- control record EDI_DC40 (#1-7) ---------------------------------------------------
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
    b.map(f"{D}/STD", C("E"))                                 # OP-06, like Implema today (Q4)
    b.map(f"{D}/STDVRS", C("96A"))
    b.map(f"{D}/STDMES", C("ORDRSP"))
    b.map(f"{D}/SNDPOR", F("getProperty", C("SNDPOR")))       # Q3: exchange properties, as CLFMAS02
    b.map(f"{D}/SNDPRT", F("ifWithoutElse", is_metocs, C("LI"), keepss="false"))
    b.map(f"{D}/SNDPFC", F("ifWithoutElse", is_metocs, C("LF"), keepss="false"))
    b.map(f"{D}/SNDPRN", F("ifWithoutElse", is_metocs, C("0000080008"), keepss="false"))
    b.map(f"{D}/SNDLAD", S(f"{M}/Header/InterchangeSender"))
    b.map(f"{D}/RCVPOR", F("getProperty", C("RCVPOR")))
    b.map(f"{D}/RCVPRT", C("LS"))
    b.map(f"{D}/RCVPRN", F("getProperty", C("RCVPRN")))       # OP-07: PRDCLNT100 in production
    b.map(f"{D}/RCVLAD", S(f"{M}/Header/InterchangeRecipient"))

    # ---- header segments (#8-11) ----------------------------------------------------------
    b.map(f"{T}/E1EDK01", C(""))
    b.map(f"{T}/E1EDK01/@SEGMENT", C("1"))
    b.map(f"{T}/E1EDK01/BELNR", po_no)
    b.map(f"{T}/E1EDK03", present(doc_date))
    b.map(f"{T}/E1EDK03/@SEGMENT", C("1"))
    b.map(f"{T}/E1EDK03/IDDAT", C("012"))
    b.map(f"{T}/E1EDK03/DATUM", doc_date)
    b.map(f"{T}/E1EDK02", present(po_no))                     # QUALF 001: Tibnor PO number
    b.map(f"{T}/E1EDK02/@SEGMENT", C("1"))
    b.map(f"{T}/E1EDK02/QUALF", C("001"))
    b.map(f"{T}/E1EDK02/BELNR", po_no)
    b.map(f"{T}/E1EDK02[1]", C(""))                           # QUALF 002: DocumentNo is mandatory
    b.map(f"{T}/E1EDK02[1]/@SEGMENT", C("1"))
    b.map(f"{T}/E1EDK02[1]/QUALF", C("002"))
    b.map(f"{T}/E1EDK02[1]/BELNR", S(f"{M}/DocumentId/DocumentNo"))

    # ---- items (#12-21) -------------------------------------------------------------------
    # #12: keep an Item only if it has a Property type 12 whose text is not 'ITEM CANCELLED'.
    # Type-12 text per Item; no type-12 property -> empty context -> default 'ITEM CANCELLED' -> skipped.
    prod_name = F("mapWithDefault", qualified(f"{IT}/Property", "Type", "12", "PropertyText", ctx=IT),
                  default_value="ITEM CANCELLED")
    line_no = F("formatNumber", S(f"{IT}/LineNo"), nformat="#", separator=".")              # '010' -> '10'
    qty = qualified(f"{IT}/Quantity", "Type", "21", "QuantityValue", ctx=IT)
    unit = qualified(f"{IT}/Quantity", "Type", "21", "MeasureUnit", ctx=IT)
    date718 = F("ifWithoutElse", F("and", F("stringEquals", S(f"{IT}/Date/@Type"), C("55")),
                                   F("stringEquals", S(f"{IT}/Date/@Format"), C("718"))),
                S(f"{IT}/Date"), keepss="false")
    conf_date = F("substring", date718, start="9", count="8")   # 'YYYYMMDD-YYYYMMDD' -> end date
    art_in = qualified(f"{IT}/AddArticleNo", "Type", "IN")

    P = f"{T}/E1EDP01"
    b.map(P, F("createIf", F("not", F("stringEquals", prod_name, C("ITEM CANCELLED")))))
    b.map(f"{P}/@SEGMENT", C("1"))
    b.map(f"{P}/POSEX", line_no)
    b.map(f"{P}/MENGE", qty)
    # #15: 'M' -> 'MTR', other units unchanged. iF pins: then, condition, else.
    b.map(f"{P}/MENEE", F("iF", C("MTR"), F("stringEquals", unit, C("M")), unit))
    b.map(f"{P}/E1EDP02", C(""))
    b.map(f"{P}/E1EDP02/@SEGMENT", C("1"))
    b.map(f"{P}/E1EDP02/QUALF", C("001"))
    # header PO number repeated once per Item: useOneAsMany(value, repeat per Item, Item contexts)
    b.map(f"{P}/E1EDP02/BELNR", F("useOneAsMany", po_no, S(f"{IT}/LineNo", context=M), S(f"{IT}/LineNo")))
    b.map(f"{P}/E1EDP02/ZEILE", line_no)
    b.map(f"{P}/E1EDP03", present(date718))                   # #18: no format-718 date -> no E1EDP03
    b.map(f"{P}/E1EDP03/@SEGMENT", C("1"))
    b.map(f"{P}/E1EDP03/IDDAT", C("001"))
    b.map(f"{P}/E1EDP03/DATUM", conf_date)
    b.map(f"{P}/E1EDP20", C(""))                              # one schedule line per item
    b.map(f"{P}/E1EDP20/@SEGMENT", C("1"))
    b.map(f"{P}/E1EDP20/WMENG", qty)
    b.map(f"{P}/E1EDP20/EDATU", conf_date)                    # #20: left out without a format-718 date
    b.map(f"{P}/E1EDP19", present(art_in))
    b.map(f"{P}/E1EDP19/@SEGMENT", C("1"))
    b.map(f"{P}/E1EDP19/QUALF", C("001"))
    b.map(f"{P}/E1EDP19/IDTNR", art_in)
    return b.finish()


if __name__ == "__main__":
    out = HERE / "build"
    bad = 0
    for variant, mode in VARIANTS.items():
        m = build(variant, mode)
        z = package(m, HERE, out)
        errs = check_build(z, m.name) + check_paths(m, out / m.name)
        print(f"{z.name}: {len(m.targets)} targets")
        print("   " + ("\n   ".join(errs) if errs else "ALL CHECKS PASSED"))
        bad += len([e for e in errs if not e.startswith("NOTE")])
    sys.exit(1 if bad else 0)
