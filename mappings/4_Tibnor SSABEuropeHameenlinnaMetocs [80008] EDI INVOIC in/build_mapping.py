"""Build Map_HammelinnaMetocsHub_TibnorS4_Invoice_INVOIC.

Run:  py -I "mappings/4_Tibnor SSABEuropeHameenlinnaMetocs [80008] EDI INVOIC in/build_mapping.py"
Rows (#) refer to sheet 'Mapping' of 25224_INVOIC_HameenlinnaMetocs-to-Tibnor_MappingSpec_v0.1.xlsx.
Design, assumptions and decisions: spec.md.

Conventions taken over from ORDRSP v1.0.2 (FORMAT_NOTES §2.2, §3.6, CLAUDE.md):
  * qualifier filters on repeating children follow the user's PO pattern, no source contexts, no UDF
  * EDI_DC40 as ORDRSP (getProperty SNDPOR/RCVPOR/RCVPRN, STD constants)
The source XSD has no targetNamespace, so paths carry no prefix and the link has 3 elems.
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

NAME = "Map_HammelinnaMetocsHub_TibnorS4_Invoice_INVOIC"

b = Builder(NAME,
            source=Link("xsd", ["Harmonized_Mill_Invoice_0_0_4_AoC.xsd", "src/main/resources/xsd", "Invoice"]),
            target=Link("xsd", ["INVOIC.INVOIC01.xsd", "src/main/resources/xsd", "INVOIC01"]))
S, C, F = b.src, b.const, b.fn


def eq(a, value):
    return F("stringEquals", a, C(value))


def by_attr(node, attr, value, field=None, attr_context=None):
    """Value of node (or node/field) where node/@attr = value. PO D_7140 pattern: mapWithDefault on both inputs.
    attr_context: when the value is the node itself (attribute vs its own element's value), the attribute's
    context must be the parent (FORMAT_NOTES 3.6, ORDRSP v1.0.4)."""
    val = S(f"{node}/{field}") if field else S(node)
    attr = S(f"{node}/@{attr}", context=attr_context)
    # R4 (CLAUDE.md): no mapWithDefault after a context change when the new context can hold several occurrences
    key = attr if attr_context else F("mapWithDefault", attr, default_value="")
    return F("ifWithoutElse", eq(key, value),
             F("mapWithDefault", val, default_value=""), keepss="false")


def header(v):
    """Header-level filtered value: one value in one context."""
    return F("removeContexts", v)


def each(v):
    """PO pattern for item values: removeContexts -> SplitByValue (Each Value)."""
    return F("SplitByValue", F("removeContexts", v), type="0")


def per_item(v):
    """Header value on every Item: CopyValue index 0 (CLAUDE.md rule, ORDRSP v1.0.3)."""
    return F("CopyValue", v, nnumber="0")


H = "/Invoice"
IT = f"{H}/Item"
T = "/INVOIC01/IDOC"

# ---- header values ------------------------------------------------------------------------
is_metocs = F("startWith2", S(f"{H}/Header/SourceSystem"), C("METOCS"))                    # VM-01
is_380 = eq(S(f"{H}/Header/DocumentType"), "380")                                          # VM-03
currency = header(by_attr(f"{H}/Currency", "Type", "1", "CurrencyCode"))
inv_date = header(by_attr(f"{H}/DocumentId/Date", "Type", "149", attr_context=f"{H}/DocumentId"))
po_no = F("formatNumber", header(by_attr(f"{H}/Reference", "Type", "ON", "ReferenceIdentification")),
          nformat="0000000000", separator=".")                                             # #23: 10 digits
line_no = F("formatNumber", S(f"{IT}/LineNo"), nformat="#", separator=".")                 # '000010' -> '10'
vendor = C("80008")                    # E1EDKA1 segments carry the Metocs check (segment-level filter)

# ---- control record EDI_DC40 (#1-7) --------------------------------------------------------
b.map("/INVOIC01", C(""))
b.map(T, C(""))
b.map(f"{T}/@BEGIN", C("1"))
D = f"{T}/EDI_DC40"
# segment-level filter (CLAUDE.md, user 2026-11-24): the Metocs check sits on the segment, the sender
# fields are constants. A non-Metocs message gets no control record (it could not be posted anyway).
b.map(D, F("createIf", is_metocs))
b.map(f"{D}/@SEGMENT", C("1"))
b.map(f"{D}/TABNAM", C("EDI_DC40"))
b.map(f"{D}/DIRECT", C("2"))
b.map(f"{D}/IDOCTYP", C("INVOIC01"))
b.map(f"{D}/MESTYP", C("INVOIC"))
b.map(f"{D}/MESCOD", C("MM"))
b.map(f"{D}/STD", C("E"))
b.map(f"{D}/STDVRS", C("96A"))
b.map(f"{D}/STDMES", C("INVOIC"))
b.map(f"{D}/SNDPOR", F("getProperty", C("SNDPOR")))
b.map(f"{D}/SNDPRT", C("LI"))
b.map(f"{D}/SNDPFC", C("LF"))
b.map(f"{D}/SNDPRN", C("0000080008"))
b.map(f"{D}/SNDLAD", S(f"{H}/Header/InterchangeSender"))
b.map(f"{D}/RCVPOR", F("getProperty", C("RCVPOR")))
b.map(f"{D}/RCVPRT", C("LS"))
b.map(f"{D}/RCVPRN", F("getProperty", C("RCVPRN")))
b.map(f"{D}/RCVLAD", S(f"{H}/Header/RecipientIdentification"))

# ---- header segments (#8-19) ----------------------------------------------------------------
b.map(f"{T}/E1EDK01", C(""))
b.map(f"{T}/E1EDK01/@SEGMENT", C("1"))
b.map(f"{T}/E1EDK01/CURCY", currency)
b.map(f"{T}/E1EDK01/BSART", F("ifWithoutElse", is_380, C("INVO"), keepss="false"))
b.map(f"{T}/E1EDK01/FKART_RL", F("ifWithoutElse", is_380, C("LR"), keepss="false"))
b.map(f"{T}/E1EDK01/FKTYP", F("ifWithoutElse", is_380, C("L"), keepss="false"))

b.map(f"{T}/E1EDKA1", F("createIf", is_metocs))          # LF = vendor
b.map(f"{T}/E1EDKA1/@SEGMENT", C("1"))
b.map(f"{T}/E1EDKA1/PARVW", C("LF"))
b.map(f"{T}/E1EDKA1/PARTN", vendor)
b.map(f"{T}/E1EDKA1[1]", F("createIf", is_metocs))       # RE = invoicing party, same vendor
b.map(f"{T}/E1EDKA1[1]/@SEGMENT", C("1"))
b.map(f"{T}/E1EDKA1[1]/PARVW", C("RE"))
b.map(f"{T}/E1EDKA1[1]/PARTN", vendor)
b.map(f"{T}/E1EDKA1[1]/NAME1", F("concat", header(by_attr(f"{H}/Party", "Role", "SE", "PartyName1")),
                                 header(by_attr(f"{H}/Party", "Role", "BY", "CountryCode")), delimeter="/"))

b.map(f"{T}/E1EDK02", C(""))
b.map(f"{T}/E1EDK02/@SEGMENT", C("1"))
b.map(f"{T}/E1EDK02/QUALF", C("009"))
b.map(f"{T}/E1EDK02/BELNR", S(f"{H}/DocumentId/DocumentNo"))
b.map(f"{T}/E1EDK03", C(""))
b.map(f"{T}/E1EDK03/@SEGMENT", C("1"))
b.map(f"{T}/E1EDK03/IDDAT", C("012"))
b.map(f"{T}/E1EDK03/DATUM", inv_date)

tax_rate = S(f"{H}/Tax/TaxRate")
b.map(f"{T}/E1EDK04", S(f"{H}/Tax"))                      # one E1EDK04 per Tax
b.map(f"{T}/E1EDK04/@SEGMENT", C("1"))
b.map(f"{T}/E1EDK04/MWSKZ", each(S(f"{H}/Tax/@Type")))   # attribute sits in the Invoice context: split per Tax
b.map(f"{T}/E1EDK04/MSATZ", F("iF", C("0"), eq(tax_rate, "0.00"), tax_rate))       # #18: '0.00' -> '0'
b.map(f"{T}/E1EDK04/MWSBT", each(by_attr(f"{H}/Tax/MonetaryAmount", "Type", "176", "MonetaryValue")))

# ---- items (#20-27) ---------------------------------------------------------------------------
P = f"{T}/E1EDP01"
b.map(P, S(IT))
b.map(f"{P}/@SEGMENT", C("1"))
b.map(f"{P}/POSEX", line_no)
b.map(f"{P}/MENGE", F("formatNumber", each(by_attr(f"{IT}/Quantity", "Type", "21", "QuantityValue")),
                      nformat="0.###", separator="."))                                   # '29120.000' -> '29120'
b.map(f"{P}/MENEE", each(by_attr(f"{IT}/Quantity", "Type", "21", "MeasureUnit")))
b.map(f"{P}/E1EDP02", C(""))
b.map(f"{P}/E1EDP02/@SEGMENT", C("1"))
b.map(f"{P}/E1EDP02/QUALF", C("001"))
b.map(f"{P}/E1EDP02/BELNR", per_item(po_no))
b.map(f"{P}/E1EDP02/ZEILE", line_no)                      # OP-02 open (METOCSTO '000001' -> 10?)
b.map(f"{P}/E1EDP03", C(""))
b.map(f"{P}/E1EDP03/@SEGMENT", C("1"))
b.map(f"{P}/E1EDP03/IDDAT", C("012"))
b.map(f"{P}/E1EDP03/DATUM", per_item(inv_date))
b.map(f"{P}/E1EDP19", C(""))                              # #26: created even without a UA article (as today)
b.map(f"{P}/E1EDP19/@SEGMENT", C("1"))
b.map(f"{P}/E1EDP19/QUALF", C("001"))
b.map(f"{P}/E1EDP19/IDTNR", each(by_attr(f"{IT}/AddArticleNo", "Type", "UA", attr_context=IT)))
b.map(f"{P}/E1EDP26", C(""))
b.map(f"{P}/E1EDP26/@SEGMENT", C("1"))
b.map(f"{P}/E1EDP26/QUALF", C("003"))
b.map(f"{P}/E1EDP26/BETRG", each(by_attr(f"{IT}/MonetaryAmount", "Type", "38", "MonetaryValue")))

# ---- totals (#28-29) ---------------------------------------------------------------------------
b.map(f"{T}/E1EDS01", C(""))
b.map(f"{T}/E1EDS01/@SEGMENT", C("1"))
b.map(f"{T}/E1EDS01/SUMID", C("011"))
b.map(f"{T}/E1EDS01/SUMME", header(by_attr(f"{H}/MonetaryAmount", "Type", "39", "MonetaryValue")))
b.map(f"{T}/E1EDS01/WAERQ", currency)

m = b.finish()

if __name__ == "__main__":
    z = package(m, HERE, HERE / "build")
    errs = check_build(z, NAME) + check_paths(m, HERE / "build" / NAME)
    print(z.name, f"{len(m.targets)} targets")
    print("\n".join(errs) if errs else "ALL CHECKS PASSED")
    sys.exit(1 if [e for e in errs if not e.startswith("NOTE")] else 0)
