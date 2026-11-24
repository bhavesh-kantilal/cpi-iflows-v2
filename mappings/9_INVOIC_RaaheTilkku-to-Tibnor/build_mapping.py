"""Build Map_RaaheTilkkuHub_TibnorS4_Invoice_INVOIC.

Run:  py -I mappings/9_INVOIC_RaaheTilkku-to-Tibnor/build_mapping.py
Rows (#) refer to sheet 'Mapping' of 1002663_INVOIC_Tilkku-to-Tibnor_MappingSpec_v0.1.xlsx (shared spec for the
Raahe and Hämeenlinna Tilkku mills). Design and decisions: spec.md.

One mapping per mill (user 2026-11-16). The logic lives in build(mill); the Hämeenlinna Tilkku mapping
(mappings/13_INVOIC_HameenlinnaTilkku-to-Tibnor/build_mapping.py) calls it with its own MILL values.

Patterns taken over from the Metocs INVOIC v1.0.2 (same source XSD, user-tested):
  * qualifier filters on repeating children follow the user's PO pattern (FORMAT_NOTES §3.6)
  * EDI_DC40 with getProperty SNDPOR / RCVPOR / RCVPRN, STD constants
  * header value on every item: CopyValue(value, 0)
The source XSD has no targetNamespace: paths carry no prefix and the link has 3 elems.
No Groovy UDF.
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

MILL = dict(
    name="Map_RaaheTilkkuHub_TibnorS4_Invoice_INVOIC",
    gln="00372389445741",            # VM-01: Header/InterchangeSender of Raahe Tilkku
    sndprn="0000080067",
    vendor="80067",                  # E1EDKA1 LF / RE PARTN (vendor without leading zeros)
)
# VM-04: Tibnor company GLN (Header/RecipientIdentification) -> company code. Only Tibnor OY is confirmed (OP-08).
VM04 = [("003723894430", "0500")]


def build(mill: dict):
    b = Builder(mill["name"],
                source=Link("xsd", ["Harmonized_Mill_Invoice_0_0_4_AoC.xsd", "src/main/resources/xsd", "Invoice"]),
                target=Link("xsd", ["INVOIC.INVOIC01.xsd", "src/main/resources/xsd", "INVOIC01"]))
    S, C, F = b.src, b.const, b.fn

    def eq(a, value):
        return F("stringEquals", a, C(value))

    def by_attr(node, attr, value, field=None, attr_context=None):
        """node (or node/field) where node/@attr = value. PO D_7140 pattern; attr_context when the value is the
        node itself (attribute vs its own element's value, FORMAT_NOTES §3.6)."""
        val = S(f"{node}/{field}") if field else S(node)
        a = S(f"{node}/@{attr}", context=attr_context)
        key = a if attr_context else F("mapWithDefault", a, default_value="")
        return F("ifWithoutElse", eq(key, value), F("mapWithDefault", val, default_value=""), keepss="false")

    def header(v):
        return F("removeContexts", v)

    def each(v):
        return F("SplitByValue", F("removeContexts", v), type="0")

    def per_item(v):
        return F("CopyValue", v, nnumber="0")

    H = "/Invoice"
    IT = f"{H}/Item"
    T = "/INVOIC01/IDOC"

    # ---- header values ------------------------------------------------------------------------
    is_mill = eq(S(f"{H}/Header/InterchangeSender"), mill["gln"])                       # VM-01
    is_380 = eq(S(f"{H}/Header/DocumentType"), "380")                                    # VM-03 (OP-04)
    currency = header(by_attr(f"{H}/Currency", "Type", "1", "CurrencyCode"))
    inv_date = header(by_attr(f"{H}/DocumentId/Date", "Type", "149", attr_context=f"{H}/DocumentId"))
    po_no = F("formatNumber", header(by_attr(f"{H}/Reference", "Type", "ON", "ReferenceIdentification")),
              nformat="0000000000", separator=".")                                      # #24: 10 digits
    vendor = C(mill["vendor"])            # E1EDKA1 segments carry the mill check (segment-level filter)

    # ---- control record EDI_DC40 (#1-7) --------------------------------------------------------
    b.map("/INVOIC01", C(""))
    b.map(T, C(""))
    b.map(f"{T}/@BEGIN", C("1"))
    D = f"{T}/EDI_DC40"
    # segment-level filter (CLAUDE.md, user 2026-11-24): the mill check sits on the segment, the sender
    # fields are constants. A message from another sender gets no control record (it could not be posted anyway).
    b.map(D, F("createIf", is_mill))
    b.map(f"{D}/@SEGMENT", C("1"))
    b.map(f"{D}/TABNAM", C("EDI_DC40"))
    b.map(f"{D}/DIRECT", C("2"))
    b.map(f"{D}/IDOCTYP", C("INVOIC01"))
    b.map(f"{D}/MESTYP", C("INVOIC"))
    b.map(f"{D}/MESCOD", C("MM"))
    b.map(f"{D}/STD", C("E"))                                 # #7 OP-07: as today's IDoc
    b.map(f"{D}/STDVRS", C("96A"))
    b.map(f"{D}/STDMES", C("INVOIC"))
    b.map(f"{D}/SNDPOR", F("getProperty", C("SNDPOR")))       # #3 OP-07 ('INOBIZ' today)
    b.map(f"{D}/SNDPRT", C("LI"))
    b.map(f"{D}/SNDPFC", C("LF"))
    b.map(f"{D}/SNDPRN", C(mill["sndprn"]))
    b.map(f"{D}/SNDLAD", S(f"{H}/Header/InterchangeSender"))
    b.map(f"{D}/RCVPOR", F("getProperty", C("RCVPOR")))       # #4 OP-07
    b.map(f"{D}/RCVPRT", C("LS"))
    b.map(f"{D}/RCVPRN", F("getProperty", C("RCVPRN")))
    b.map(f"{D}/RCVLAD", S(f"{H}/Header/RecipientIdentification"))

    # ---- header segments (#8-20) ----------------------------------------------------------------
    b.map(f"{T}/E1EDK01", C(""))
    b.map(f"{T}/E1EDK01/@SEGMENT", C("1"))
    b.map(f"{T}/E1EDK01/CURCY", currency)
    b.map(f"{T}/E1EDK01/BSART", F("ifWithoutElse", is_380, C("INVO"), keepss="false"))
    b.map(f"{T}/E1EDK01/FKART_RL", F("ifWithoutElse", is_380, C("LR"), keepss="false"))
    b.map(f"{T}/E1EDK01/FKTYP", F("ifWithoutElse", is_380, C("L"), keepss="false"))

    b.map(f"{T}/E1EDKA1", F("createIf", is_mill))            # #12 LF = vendor
    b.map(f"{T}/E1EDKA1/@SEGMENT", C("1"))
    b.map(f"{T}/E1EDKA1/PARVW", C("LF"))
    b.map(f"{T}/E1EDKA1/PARTN", vendor)
    b.map(f"{T}/E1EDKA1[1]", F("createIf", is_mill))         # #13 RE = same vendor
    b.map(f"{T}/E1EDKA1[1]/@SEGMENT", C("1"))
    b.map(f"{T}/E1EDKA1[1]/PARVW", C("RE"))
    b.map(f"{T}/E1EDKA1[1]/PARTN", vendor)
    # #14: 'SSAB EUROPE OY/' + company code (VM-04, FixValues 'Use Default Value', empty default, OP-08)
    b.map(f"{T}/E1EDKA1[1]/NAME1", F("concat", C("SSAB EUROPE OY"),
                                     b.table("FixValues", S(f"{H}/Header/RecipientIdentification"), VM04,
                                             default="", strategy="1"), delimeter="/"))

    b.map(f"{T}/E1EDK02", C(""))                              # #15
    b.map(f"{T}/E1EDK02/@SEGMENT", C("1"))
    b.map(f"{T}/E1EDK02/QUALF", C("009"))
    b.map(f"{T}/E1EDK02/BELNR", S(f"{H}/DocumentId/DocumentNo"))
    b.map(f"{T}/E1EDK03", C(""))                              # #16
    b.map(f"{T}/E1EDK03/@SEGMENT", C("1"))
    b.map(f"{T}/E1EDK03/IDDAT", C("012"))
    b.map(f"{T}/E1EDK03/DATUM", inv_date)

    # #17 (OP-06): one E1EDK05 when the invoice has any MonetaryAmount of type 165 or 260.
    # 'any' = sum of 1/0 flags over all header amounts > 0 (standard functions only; iF pins then/cond/else).
    amt_type = F("removeContexts", S(f"{H}/MonetaryAmount/@Type"))
    flag = F("iF", C("1"), F("or", eq(amt_type, "165"), eq(amt_type, "260")), C("0"))
    b.map(f"{T}/E1EDK05", F("createIf", F("greater", F("sum", flag), C("0"))))
    b.map(f"{T}/E1EDK05/@SEGMENT", C("1"))
    b.map(f"{T}/E1EDK05/ALCKZ", C("-"))                       # straight maps under createIf
    b.map(f"{T}/E1EDK05/BETRG", C("0.00"))
    b.map(f"{T}/E1EDK05/UPRBS", C("SEK"))

    b.map(f"{T}/E1EDK04", S(f"{H}/Tax"))                      # #18-20 one E1EDK04 per Tax
    b.map(f"{T}/E1EDK04/@SEGMENT", C("1"))
    b.map(f"{T}/E1EDK04/MWSKZ", each(S(f"{H}/Tax/@Type")))   # attribute: one context per Tax
    b.map(f"{T}/E1EDK04/MSATZ", S(f"{H}/Tax/TaxRate"))        # #19 copy
    b.map(f"{T}/E1EDK04/MWSBT", each(by_attr(f"{H}/Tax/MonetaryAmount", "Type", "176", "MonetaryValue")))

    # ---- items (#21-28) ---------------------------------------------------------------------------
    art_in = each(by_attr(f"{IT}/ArticleNo", "Type", "IN", attr_context=IT))
    P = f"{T}/E1EDP01"
    b.map(P, S(IT))
    b.map(f"{P}/@SEGMENT", C("1"))
    b.map(f"{P}/POSEX", S(f"{IT}/LineNo"))                    # #21 as it is ('010')
    b.map(f"{P}/MENGE", F("formatNumber", each(by_attr(f"{IT}/Quantity", "Type", "21", "QuantityValue")),
                          nformat="0.00", separator="."))     # #22 exactly 2 decimals (UNVERIFIED pattern)
    b.map(f"{P}/MENEE", each(by_attr(f"{IT}/Quantity", "Type", "21", "MeasureUnit")))
    b.map(f"{P}/E1EDP02", C(""))
    b.map(f"{P}/E1EDP02/@SEGMENT", C("1"))
    b.map(f"{P}/E1EDP02/QUALF", C("001"))
    b.map(f"{P}/E1EDP02/BELNR", per_item(po_no))
    b.map(f"{P}/E1EDP02/ZEILE", F("formatNumber", S(f"{IT}/LineNo"), nformat="#", separator="."))   # #25
    b.map(f"{P}/E1EDP03", C(""))                              # #26
    b.map(f"{P}/E1EDP03/@SEGMENT", C("1"))
    b.map(f"{P}/E1EDP03/IDDAT", C("012"))
    b.map(f"{P}/E1EDP03/DATUM", per_item(inv_date))
    b.map(f"{P}/E1EDP19", art_in)                             # #27 segment and IDTNR from one chain
    b.map(f"{P}/E1EDP19/@SEGMENT", C("1"))
    b.map(f"{P}/E1EDP19/QUALF", C("001"))
    b.map(f"{P}/E1EDP19/IDTNR", art_in)
    b.map(f"{P}/E1EDP26", C(""))                              # #28
    b.map(f"{P}/E1EDP26/@SEGMENT", C("1"))
    b.map(f"{P}/E1EDP26/QUALF", C("003"))
    b.map(f"{P}/E1EDP26/BETRG", each(by_attr(f"{IT}/MonetaryAmount", "Type", "38", "MonetaryValue")))

    # ---- totals (#29-30) ---------------------------------------------------------------------------
    b.map(f"{T}/E1EDS01", C(""))
    b.map(f"{T}/E1EDS01/@SEGMENT", C("1"))
    b.map(f"{T}/E1EDS01/SUMID", C("011"))
    b.map(f"{T}/E1EDS01/SUMME", header(by_attr(f"{H}/MonetaryAmount", "Type", "39", "MonetaryValue")))
    b.map(f"{T}/E1EDS01/WAERQ", currency)
    return b.finish()


def run(mill: dict, here: Path) -> int:
    m = build(mill)
    z = package(m, here, here / "build")
    errs = check_build(z, mill["name"]) + check_paths(m, here / "build" / mill["name"])
    print(z.name, f"{len(m.targets)} targets")
    print("\n".join(errs) if errs else "ALL CHECKS PASSED")
    return 1 if [e for e in errs if not e.startswith("NOTE")] else 0


if __name__ == "__main__":
    sys.exit(run(MILL, HERE))
