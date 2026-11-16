"""Build Map_RaaheTilkkuHub_TibnorS4_OrderConfirmation_ORDRSP.

Run:  py -I mappings/7_ORDRSP_RaaheTilkku-to-Tibnor/build_mapping.py
Rows (#) refer to sheet 'Mapping' of 1002257_ORDRSP_Tilkku-to-Tibnor_MappingSpec_v0.1.xlsx (shared spec for the
Raahe and Hämeenlinna Tilkku mills). Design and decisions: spec.md.

One mapping per mill (user 2026-11-16, "Raahe only"). The logic lives in build(mill); the Hämeenlinna Tilkku
mapping (mappings/11_ORDRSP_HameenlinnaTilkku-to-Tibnor/build_mapping.py) calls it with its own MILL values.

Patterns taken over from the user-tested Metocs ORDRSP (same source XSD Ordrsp_1_0_0, v1.0.6):
  * ns0: on every source element step, 4th link elem = targetNamespace
  * item values: ifWithoutElse(@Type filter, value) -> removeContexts -> SplitByValue(Each Value)
  * attribute compared with its own element's value gets context = parent (Date/@Type, ArticleNo/@Type)
  * header value on every item: CopyValue(value, 0)
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

# VM-01 for this mill (spec sheet 'Value Mappings')
MILL = dict(
    name="Map_RaaheTilkkuHub_TibnorS4_OrderConfirmation_ORDRSP",
    gln="00372389445741",            # Header/InterchangeSender of Raahe Tilkku
    sndprn="0000080067",             # Tibnor vendor 80067
)
NS_URI, NS = "http://www.ruukki.com/schemas/eai/internal/production/eruukki", "ns0"


def build(mill: dict):
    b = Builder(mill["name"],
                source=Link("xsd", ["Ordrsp_1_0_0.xsd", "src/main/resources/xsd", "OrdrspInterchange", NS_URI]),
                target=Link("xsd", ["ORDRSP.ORDERS02.xsd", "src/main/resources/xsd", "ORDERS01"]),
                namespaces=[(NS, NS_URI)])
    C, F = b.const, b.fn

    def _ns(path: str) -> str:
        return "/" + "/".join(s if s.startswith("@") else f"{NS}:{s}" for s in path.strip("/").split("/"))

    def S(path: str, context: str | None = None):
        """Source field; ns0: on every element step (FORMAT_NOTES §2.2, qualified XSD)."""
        return b.src(_ns(path), context=_ns(context) if context else None)

    def eq(a, value):
        return F("stringEquals", a, C(value))

    def each(v):
        """PO pattern: removeContexts -> SplitByValue (Each Value), one context per found value."""
        return F("SplitByValue", F("removeContexts", v), type="0")

    def by_type(node, value, field=None, attr_context=None):
        """Value of node (or node/field) where node/@Type = value (PO D_7140 pattern, R4 as Metocs v1.0.6)."""
        val = S(f"{node}/{field}") if field else S(node)
        attr = S(f"{node}/@Type", attr_context)
        key = attr if attr_context else F("mapWithDefault", attr, default_value="")
        return F("ifWithoutElse", eq(key, value), F("mapWithDefault", val, default_value=""), keepss="false")

    def party_zti(role):
        """Party[@Role=role]/PartyId[@Type='ZTI'] (#9, #11). A Party has several PartyIds:
        PartyId sits in the Party context (default); PartyId/@Type is compared with its own element's value,
        so its context is Party; @Role (one per Party) is repeated per PartyId with useOneAsMany."""
        pid = S(f"{M}/Party/PartyId")
        role_per_id = F("useOneAsMany", S(f"{M}/Party/@Role"), pid, pid)
        cond = F("and", eq(role_per_id, role), eq(S(f"{M}/Party/PartyId/@Type", f"{M}/Party"), "ZTI"))
        return F("removeContexts", F("ifWithoutElse", cond, S(f"{M}/Party/PartyId"), keepss="false"))

    M = "/OrdrspInterchange/OrderResponseMessage"
    IT = f"{M}/Item"
    T = "/ORDERS01/IDOC"

    # ---- header values ------------------------------------------------------------------------
    co_ref = F("ifWithoutElse", eq(S(f"{M}/Reference/@Type"), "CO"), S(f"{M}/Reference/RefNo"), keepss="false")
    po_no = F("removeContexts", co_ref)                                   # #7, #20 (Tibnor order number)
    po_chain = each(co_ref)                                               # #12: one E1EDK02 per CO reference
    # #8: Date/@Type compared with its own element's value -> context DocumentId (FORMAT_NOTES §3.6)
    doc_date = each(F("ifWithoutElse", eq(S(f"{M}/DocumentId/Date/@Type", f"{M}/DocumentId"), "137"),
                      S(f"{M}/DocumentId/Date"), keepss="false"))
    is_mill = eq(S(f"{M}/Header/InterchangeSender"), mill["gln"])        # VM-01

    # ---- control record EDI_DC40 (#1-6) ---------------------------------------------------------
    b.map("/ORDERS01", C(""))
    b.map(T, C(""))
    b.map(f"{T}/@BEGIN", C("1"))
    D = f"{T}/EDI_DC40"
    b.map(D, C(""))
    b.map(f"{D}/@SEGMENT", C("1"))
    b.map(f"{D}/TABNAM", C("EDI_DC40"))                       # mandatory, as reference CLFMAS02
    b.map(f"{D}/DIRECT", C("2"))                              # inbound, as reference CLFMAS02
    b.map(f"{D}/IDOCTYP", C("ORDERS01"))
    b.map(f"{D}/MESTYP", C("ORDRSP"))
    b.map(f"{D}/STD", C("E"))                                 # #6 OP-05: as today's IDoc
    b.map(f"{D}/STDVRS", C("93A"))
    b.map(f"{D}/STDMES", C("ORDRSP"))
    b.map(f"{D}/SNDPOR", F("getProperty", C("SNDPOR")))       # as Metocs ORDRSP Q3
    b.map(f"{D}/SNDPRT", F("ifWithoutElse", is_mill, C("LI"), keepss="false"))
    b.map(f"{D}/SNDPFC", F("ifWithoutElse", is_mill, C("LF"), keepss="false"))
    b.map(f"{D}/SNDPRN", F("ifWithoutElse", is_mill, C(mill["sndprn"]), keepss="false"))
    b.map(f"{D}/SNDLAD", S(f"{M}/Header/InterchangeSender"))
    b.map(f"{D}/RCVPOR", F("getProperty", C("RCVPOR")))
    b.map(f"{D}/RCVPRT", C("LS"))
    b.map(f"{D}/RCVPRN", F("getProperty", C("RCVPRN")))       # #3 OP-05
    b.map(f"{D}/RCVLAD", S(f"{M}/Header/InterchangeRecipient"))

    # ---- header segments (#7-13) -----------------------------------------------------------------
    b.map(f"{T}/E1EDK01", C(""))
    b.map(f"{T}/E1EDK01/@SEGMENT", C("1"))
    b.map(f"{T}/E1EDK01/BELNR", po_chain)
    b.map(f"{T}/E1EDK03", doc_date)                           # segment and field from one filtered chain
    b.map(f"{T}/E1EDK03/@SEGMENT", C("1"))
    b.map(f"{T}/E1EDK03/IDDAT", C("012"))
    b.map(f"{T}/E1EDK03/DATUM", doc_date)
    b.map(f"{T}/E1EDKA1", C(""))                              # #9 AG = buyer
    b.map(f"{T}/E1EDKA1/@SEGMENT", C("1"))
    b.map(f"{T}/E1EDKA1/PARVW", C("AG"))
    b.map(f"{T}/E1EDKA1/PARTN", party_zti("BY"))
    b.map(f"{T}/E1EDKA1[1]", C(""))                           # #10 WE, no other fields (OP-03)
    b.map(f"{T}/E1EDKA1[1]/@SEGMENT", C("1"))
    b.map(f"{T}/E1EDKA1[1]/PARVW", C("WE"))
    b.map(f"{T}/E1EDKA1[2]", C(""))                           # #11 LF = mill (SSAB party number)
    b.map(f"{T}/E1EDKA1[2]/@SEGMENT", C("1"))
    b.map(f"{T}/E1EDKA1[2]/PARVW", C("LF"))
    b.map(f"{T}/E1EDKA1[2]/PARTN", party_zti("SE"))
    b.map(f"{T}/E1EDK02", po_chain)                           # #12 QUALF 001, one per CO reference
    b.map(f"{T}/E1EDK02/@SEGMENT", C("1"))
    b.map(f"{T}/E1EDK02/QUALF", C("001"))
    b.map(f"{T}/E1EDK02/BELNR", po_chain)
    b.map(f"{T}/E1EDK02[1]", C(""))                           # #13 QUALF 002: DocumentNo is mandatory
    b.map(f"{T}/E1EDK02[1]/@SEGMENT", C("1"))
    b.map(f"{T}/E1EDK02[1]/QUALF", C("002"))
    b.map(f"{T}/E1EDK02[1]/BELNR", S(f"{M}/DocumentId/DocumentNo"))

    # ---- items (#14-25) ---------------------------------------------------------------------------
    line_no = F("formatNumber", S(f"{IT}/LineNo"), nformat="#", separator=".")          # '010' -> '10'
    qty = each(by_type(f"{IT}/Quantity", "21", "QuantityValue"))
    is_718 = F("and", eq(S(f"{IT}/Date/@Type", IT), "55"), eq(S(f"{IT}/Date/@Format", IT), "718"))
    date_718 = each(F("ifWithoutElse", is_718, S(f"{IT}/Date"), keepss="false"))
    conf_date = b.udf("substringSafe", "substringSafe", date_718, C("9"), C("17"))   # end of the range
    art_in = each(by_type(f"{IT}/ArticleNo", "IN", attr_context=IT))

    P = f"{T}/E1EDP01"
    b.map(P, S(IT))                                           # #14 one E1EDP01 per Item (OP-01)
    b.map(f"{P}/@SEGMENT", C("1"))
    b.map(f"{P}/POSEX", line_no)
    b.map(f"{P}/MENGE", qty)
    b.map(f"{P}/MENEE", each(by_type(f"{IT}/Quantity", "21", "MeasureUnit")))     # #17 copy (OP-02)
    # #18-19: Price occurs at most once per Item; context Item keeps an Item without Price aligned
    b.map(f"{P}/PMENE", S(f"{IT}/Price/MeasureUnit", IT))
    b.map(f"{P}/VPREI", S(f"{IT}/Price/PriceValue", IT))
    b.map(f"{P}/E1EDP02", C(""))
    b.map(f"{P}/E1EDP02/@SEGMENT", C("1"))
    b.map(f"{P}/E1EDP02/QUALF", C("001"))
    b.map(f"{P}/E1EDP02/BELNR", F("CopyValue", po_no, nnumber="0"))
    b.map(f"{P}/E1EDP02/ZEILE", line_no)
    b.map(f"{P}/E1EDP03", date_718)                           # #22 same chain as DATUM / EDATU
    b.map(f"{P}/E1EDP03/@SEGMENT", C("1"))
    b.map(f"{P}/E1EDP03/IDDAT", C("001"))
    b.map(f"{P}/E1EDP03/DATUM", conf_date)
    b.map(f"{P}/E1EDP20", C(""))                              # #23-24 one schedule line per item
    b.map(f"{P}/E1EDP20/@SEGMENT", C("1"))
    b.map(f"{P}/E1EDP20/WMENG", qty)
    b.map(f"{P}/E1EDP20/EDATU", conf_date)
    b.map(f"{P}/E1EDP19", art_in)                             # #25 segment and IDTNR from one chain
    b.map(f"{P}/E1EDP19/@SEGMENT", C("1"))
    b.map(f"{P}/E1EDP19/QUALF", C("001"))
    b.map(f"{P}/E1EDP19/IDTNR", art_in)
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
