"""Build Map_TibnorS4_HammelinnaMetocsHub_PurchaseOrder_ORDERS02.

Run:  py -I mappings/1_ORDERS_Tibnor-to-HameenlinnaMetocs/build_mapping.py
Rows (#) refer to sheet 'Mapping' of 25200_ORDERS_Tibnor-to-HameenlinnaMetocs_MappingSpec_v0.1.xlsx.
Design and decisions: spec.md.
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

NAME = "Map_TibnorS4_HammelinnaMetocsHub_PurchaseOrder_ORDERS02"
ENV_PROPERTY = "HubEnvironment"        # placeholder exchange property holding PRD / TST (Q3, to be fixed later)

b = Builder(NAME,
            source=Link("xsd", ["ORDERS.ORDERS02.xsd", "src/main/resources/xsd", "ORDERS02"]),
            target=Link("xsd", ["Harmonized_Purchase_Order_0_0_7.xsd", "src/main/resources/xsd", "OrdersMessage"]))
S, C, F = b.src, b.const, b.fn
I = "/ORDERS02/IDOC"
T = "/OrdersMessage"


# ---- reusable patterns (all functions from FORMAT_NOTES) -------------------------------
def partner(parvw, field):
    """Field of the E1EDKA1 with PARVW = parvw (one value): removeContexts(ifWithoutElse(PARVW=x, mapWithDefault(field)))."""
    return F("removeContexts",
             F("ifWithoutElse", F("stringEquals", S(f"{I}/E1EDKA1/PARVW"), C(parvw)),
               F("mapWithDefault", S(f"{I}/E1EDKA1/{field}"), default_value=""), keepss="false"))


def header_qualified(seg, qualf, field):
    """Field of header segment seg with QUALF = qualf (e.g. E1EDK17 QUALF 001)."""
    return F("removeContexts",
             F("ifWithoutElse", F("stringEquals", S(f"{I}/{seg}/QUALF"), C(qualf)),
               F("mapWithDefault", S(f"{I}/{seg}/{field}"), default_value=""), keepss="false"))


def nonempty(v):
    """Pass v on only when it is not empty, so no empty target element is created."""
    return F("ifWithoutElse", F("not", F("stringEquals", v, C(""))), v, keepss="false")


def exists(v):
    """Condition for createIf: v has a non-empty value (user feedback 1.1.0: conditional containers use createIf)."""
    return F("createIf", F("not", F("stringEquals", v, C(""))))


def table(inp, rows, default=""):
    # FixValues with "use default value" (vmstrategy 1 + default, as ACC's FixValues with default VST).
    # UNVERIFIED for FixValues (FORMAT_NOTES §5 Q1): check in the CPI editor after import.
    return b.table("FixValues", inp, rows, default=default, strategy="1")


ag_partn = partner("AG", "PARTN")            # ordering Tibnor company 0010 / 0310 / 0500
is_oy = F("stringEquals", ag_partn, C("0500"))

# ---- Header (#1-8) ----------------------------------------------------------------------
b.map(T, C(""))
b.map(f"{T}/Header", C(""))
b.map(f"{T}/Header/SchemaId", C("EDI.ORDER"))
b.map(f"{T}/Header/SchemaVersion", C("Harmonized_Purchase_Order_0_0_7.xsd"))
b.map(f"{T}/Header/MessageFunction", C("105"))                       # OP-15: keep 105
b.map(f"{T}/Header/OrderType", C("105"))                             # NB only (OP-03)
b.map(f"{T}/Header/InterchangeSender", table(ag_partn, [             # VM-04
    ("0010", "7340195700006"), ("0310", "7080003309006"), ("0500", "003723894430")]))
b.map(f"{T}/Header/InterchangeRecipient", C("00372389445756"))       # VM-01
b.map(f"{T}/Header/MessageRoutingInbound", F("concat", C("SSCO.M.EDI"), F("getProperty", C(ENV_PROPERTY)), delimeter=""))
b.map(f"{T}/Header/MessageRoutingOutbound", F("concat", C("HAPU.M.METOCS"), F("getProperty", C(ENV_PROPERTY)), delimeter=""))

# ---- Document references (#9-12) --------------------------------------------------------
belnr = S(f"{I}/E1EDK01/BELNR")
b.map(f"{T}/DocumentId", C(""))
b.map(f"{T}/DocumentId/DocumentNo", belnr)
b.map(f"{T}/Reference", belnr)                       # duplicate subtree: Reference, Reference[1], Reference[2]
b.map(f"{T}/Reference/@Type", C("CR"))
b.map(f"{T}/Reference[1]", C("S"))                   # OP-04
b.map(f"{T}/Reference[1]/@Type", C("ZZ"))
b.map(f"{T}/Reference[2]", C("TPO"))
b.map(f"{T}/Reference[2]/@Type", C("ZOT"))

# ---- Party SE = Party (#24-31) -----------------------------------------------------------
lf_partn = partner("LF", "PARTN")
se_gln = table(lf_partn, [("0000080008", "00370113276957")])                      # VM-01
se_zti = table(se_gln, [("00370113276957", "0003092")], default="0003092")       # VM-02, fallback Metocs
P = f"{T}/Party"
b.map(P, C(""))
b.map(f"{P}/@Role", C("SE"))
b.map(f"{P}/PartyId", se_zti)
b.map(f"{P}/PartyId/@Type", C("ZTI"))
b.map(f"{P}/PartyId[1]", se_gln)
b.map(f"{P}/PartyId[1]/@Type", C("100"))
b.map(f"{P}/PartyName1", table(lf_partn, [("0000080008", "METFORM")]))
b.map(f"{P}/PartyName2", table(lf_partn, [("0000080008", "METFORM HÄMEENLINNA")]))
b.map(f"{P}/AddressLine1", nonempty(partner("BA", "STRAS")))
b.map(f"{P}/AddressLine3", nonempty(partner("BA", "ORT01")))                      # OP-16
b.map(f"{P}/PostalCode", nonempty(partner("BA", "PSTLZ")))
b.map(f"{P}/CountryCode", nonempty(partner("BA", "LAND1")))

# ---- Party BY = Party[1] (#13-23) -------------------------------------------------------
by_gln = table(ag_partn, [("0010", "094200005561351270"), ("0310", "0942000055613512703000"),
                          ("0500", "003723894430")])                               # VM-04
by_zti = table(by_gln, [("094200005561351270", "8380390"), ("0942000055613512703000", "0142700"),
                        ("003723894430", "8387920")])                              # VM-02
we_stras, we_ort01, we_pstlz = partner("WE", "STRAS"), partner("WE", "ORT01"), partner("WE", "PSTLZ")
P = f"{T}/Party[1]"
b.map(P, C(""))
b.map(f"{P}/@Role", C("BY"))
b.map(f"{P}/PartyId", nonempty(by_zti))
b.map(f"{P}/PartyId/@Type", C("ZTI"))
b.map(f"{P}/PartyId[1]", by_gln)
b.map(f"{P}/PartyId[1]/@Type", C("100"))
b.map(f"{P}/PartyName1", table(ag_partn, [("0010", "TIBNOR AB"), ("0310", "TIBNOR AS"), ("0500", "TIBNOR OY")]))
# iF pins: then, condition, else (CONFIRMED). Tibnor OY uses the ship-to address (OP-05).
b.map(f"{P}/AddressLine1", F("iF", we_stras, is_oy,
                             table(ag_partn, [("0010", "Sjöhagsvägen 2"), ("0310", "Professor Birkelandsvei 21")])))
b.map(f"{P}/AddressLine2", nonempty(table(ag_partn, [("0010", "909"), ("0310", "140")])))   # OY: left out
b.map(f"{P}/AddressLine3", F("iF", we_ort01, is_oy, table(ag_partn, [("0010", "Köping"), ("0310", "OSLO")])))
b.map(f"{P}/PostalCode", F("iF", we_pstlz, is_oy, table(ag_partn, [("0010", "73129"), ("0310", "1081")])))
b.map(f"{P}/CountryCode", partner("AG", "LAND1"))
bname_raw = partner("AG", "BNAME")
bname = nonempty(bname_raw)
b.map(f"{P}/Contact", exists(bname_raw))              # container: createIf (user feedback 1.1.0)
b.map(f"{P}/Contact/@Type", C("PD"))
b.map(f"{P}/Contact/ContactName", bname)
telf1 = nonempty(F("replaceString", F("replaceString", partner("AG", "TELF1"), C("-"), C("")), C(" "), C("")))
b.map(f"{P}/Contact/CommId", telf1)
b.map(f"{P}/Contact/CommId/@Type", C("TE"))

# ---- Party CN = Party[2] (#32-39) -------------------------------------------------------
cn_gln = F("ifWithoutElse", F("not", is_oy),
           F("concat", C("094200005561351270"), partner("WE", "LIFNR"), delimeter=""), keepss="false")   # none for OY
cn_zti = nonempty(table(cn_gln, [("0942000055613512700050", "8430748"),
                                 ("0942000055613512703020", "8426340")]))         # VM-02, no hit -> left out
P = f"{T}/Party[2]"
b.map(P, C(""))
b.map(f"{P}/@Role", C("CN"))
b.map(f"{P}/PartyId", cn_zti)
b.map(f"{P}/PartyId/@Type", C("ZTI"))
b.map(f"{P}/PartyId[1]", cn_gln)
b.map(f"{P}/PartyId[1]/@Type", C("100"))
b.map(f"{P}/PartyName1", nonempty(partner("WE", "NAME1")))
b.map(f"{P}/AddressLine1", nonempty(we_stras))
b.map(f"{P}/AddressLine2", nonempty(partner("WE", "PFACH")))
b.map(f"{P}/AddressLine3", nonempty(we_ort01))
b.map(f"{P}/PostalCode", nonempty(F("replaceString", we_pstlz, C(" "), C(""))))
b.map(f"{P}/CountryCode", nonempty(partner("WE", "LAND1")))

# ---- Commercial terms (#40-42) ----------------------------------------------------------
b.map(f"{T}/Currency", C("EUR"))                                                   # OP-20
b.map(f"{T}/Currency/@Type", C("5"))
lkond_raw = header_qualified("E1EDK17", "001", "LKOND")
lktext_raw = header_qualified("E1EDK17", "001", "LKTEXT")
lkond, lktext = nonempty(lkond_raw), nonempty(lktext_raw)
b.map(f"{T}/TermsOfDelivery", exists(lkond_raw))      # container: createIf (user feedback 1.1.0)
b.map(f"{T}/TermsOfDelivery/@Type", C("6"))
b.map(f"{T}/TermsOfDelivery/TermsOfDeliveryCode", lkond)
b.map(f"{T}/TermsOfDelivery/TermsOfDeliveryCode/@CodeSet", C("Z2K"))
b.map(f"{T}/TermsOfDelivery/Location", exists(lktext_raw))
b.map(f"{T}/TermsOfDelivery/Location/@Type", C("1"))
b.map(f"{T}/TermsOfDelivery/Location/LocationText", lktext)

# ---- Items (#43-51) -----------------------------------------------------------------------
E = f"{I}/E1EDP01"
item_ctx = E                      # E1EDP19/E1EDPT1 values grouped per item (context = E1EDP01)
idtnr001 = F("ifWithoutElse", F("stringEquals", S(f"{E}/E1EDP19/QUALF", context=item_ctx), C("001")),
             S(f"{E}/E1EDP19/IDTNR", context=item_ctx), keepss="false")
ktext001 = F("ifWithoutElse", F("stringEquals", S(f"{E}/E1EDP19/QUALF", context=item_ctx), C("001")),
             F("mapWithDefault", S(f"{E}/E1EDP19/KTEXT"), default_value=""), keepss="false")
has_best = b.udf("TibnorOrdersHelpers", "hasBestText", S(f"{E}/E1EDPT1/TDID", context=item_ctx), context_param=True)
prop_text = F("ifWithoutElse", has_best,
              b.udf("TibnorOrdersHelpers", "cropText", ktext001, C("35")), keepss="false")
b.map(f"{T}/Item", S(E))
# user feedback 1.1.0: numeric source -> formatNumber '#' removes leading zeros; removezeros only for non-numeric (IDTNR)
b.map(f"{T}/Item/LineNo", F("formatNumber", S(f"{E}/POSEX"), nformat="#", separator="."))
b.map(f"{T}/Item/AddArticleNo", b.udf("removezeros", "removezeros", idtnr001))
b.map(f"{T}/Item/AddArticleNo/@Type", C("UA"))
b.map(f"{T}/Item/Property", F("createIf", has_best))  # container: only items with a BEST text
b.map(f"{T}/Item/Property/@Type", C("44"))
b.map(f"{T}/Item/Property/PropertyText", prop_text)
b.map(f"{T}/Item/Quantity", C(""))                    # container: every PO item has a quantity (user)
b.map(f"{T}/Item/Quantity/@Type", C("21"))
b.map(f"{T}/Item/Quantity/QuantityValue", F("formatNumber", S(f"{E}/MENGE"), nformat="0.###", separator="."))
b.map(f"{T}/Item/Quantity/MeasureUnit", S(f"{E}/MENEE"))
b.map(f"{T}/Item/Date", S(f"{E}/E1EDP20/EDATU"))     # assumes one E1EDP20 per item (OP-10)
b.map(f"{T}/Item/Date/@Type", C("2"))
b.map(f"{T}/Item/Date/@Format", C("102"))
b.map(f"{T}/Item/Price", C(""))                       # container: every PO item has a price (user)
b.map(f"{T}/Item/Price/@Type", C("AAA"))
b.map(f"{T}/Item/Price/PriceValue", S(f"{E}/VPREI"))
b.map(f"{T}/Item/Price/UnitPriceBasisCode", S(f"{E}/PMENE"))

# ---- Trailer (#52) --------------------------------------------------------------------------
b.map(f"{T}/NumberOfLineItems", F("count", S(f"{E}/POSEX", context=I)))   # standard count (user feedback 1.1.0)

m = b.finish()

if __name__ == "__main__":
    missing = [s for s in ("ORDERS.ORDERS02.xsd", "Harmonized_Purchase_Order_0_0_7.xsd")
               if not (HERE / "schemas" / s).exists()]
    if missing:
        print("BLOCKED: schemas missing in schemas/:", ", ".join(missing))
        print(f"model OK: {len(m.targets)} targets, UDF scripts: {m.udfs}")
        sys.exit(1)
    z = package(m, HERE, HERE / "build")
    errs = check_build(z, NAME) + [e for e in check_paths(m, HERE / "build" / NAME)]
    print(z)
    print("\n".join(errs) if errs else "ALL CHECKS PASSED")
    sys.exit(1 if [e for e in errs if not e.startswith("NOTE")] else 0)
