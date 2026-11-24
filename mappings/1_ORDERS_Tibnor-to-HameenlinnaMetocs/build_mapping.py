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


def exists(v):
    """Condition for createIf: v has a non-empty value (user feedback 1.1.0: conditional containers use createIf)."""
    return F("createIf", F("not", F("stringEquals", v, C(""))))


def table(inp, rows, default=""):
    # FixValues with "use default value" (vmstrategy 1 + default, as ACC's FixValues with default VST).
    # UNVERIFIED for FixValues (FORMAT_NOTES §5 Q1): check in the CPI editor after import.
    return b.table("FixValues", inp, rows, default=default, strategy="1")


ag_partn = partner("AG", "PARTN")            # ordering Tibnor company 0010 / 0310 / 0500

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

# ---- Parties: filter at segment level, fields 1:1 (user's v1.2.0 feedback, CLAUDE.md) ----------
# Party ← createIf(PARVW [context IDOC] = X): one value per E1EDKA1, SUPPRESS for the others, so each
# created Party reads its own E1EDKA1's fields. The partner rules differ from the v0.1 sheet on purpose
# (user 2026-11-24); see the "Current CPI mapping" column of the v2 sheet.
KA = f"{I}/E1EDKA1"


def party_if(parvw):
    return F("createIf", F("stringEquals", S(f"{KA}/PARVW", context=I), C(parvw)))


def ka(field, default=True):
    """E1EDKA1 field, straight map (mapWithDefault where the user's version has it)."""
    return F("mapWithDefault", S(f"{KA}/{field}"), default_value="") if default else S(f"{KA}/{field}")


def use_key(inp, rows):
    """FixValues 'Use Key' (vmstrategy 2, empty default), as in the user's version."""
    return b.table("FixValues", inp, rows, default="", strategy="2")


# Party SE = Party (#24-31): LF partner; names and address hardcoded (user)
P = f"{T}/Party"
b.map(P, party_if("LF"))
b.map(f"{P}/@Role", C("SE"))
b.map(f"{P}/PartyId", ka("PARTN"))
b.map(f"{P}/PartyId/@Type", C("ZTI"))
b.map(f"{P}/PartyId[1]", ka("PARTN"))
b.map(f"{P}/PartyId[1]/@Type", C("100"))
b.map(f"{P}/PartyName1", C("METFORM"))
b.map(f"{P}/PartyName2", C("METFORM HÄMEENLINNA"))
b.map(f"{P}/AddressLine1", C("HARVIALANTIE 420"))
b.map(f"{P}/AddressLine3", C("HÄMEENLINNA"))
b.map(f"{P}/PostalCode", C("13300"))
b.map(f"{P}/CountryCode", C("FI"))

# Party BY = Party[1] (#13-23): AG partner; address by company code (Use Key)
P = f"{T}/Party[1]"
b.map(P, party_if("AG"))
b.map(f"{P}/@Role", C("BY"))
b.map(f"{P}/PartyId", ka("PARTN"))
b.map(f"{P}/PartyId/@Type", C("ZTI"))
b.map(f"{P}/PartyId[1]", ka("PARTN"))
b.map(f"{P}/PartyId[1]/@Type", C("100"))
b.map(f"{P}/PartyName1", ka("NAME1"))
b.map(f"{P}/AddressLine1", use_key(ka("PARTN"), [("0500", "Niinistönkatu 7"), ("0010", "Norsavägen 38"),
                                                 ("0310", "Professor Birkelandsvei 21")]))
b.map(f"{P}/AddressLine2", use_key(ka("PARTN"), [("0500", ""), ("0010", "909"), ("0310", "140")]))
b.map(f"{P}/AddressLine3", use_key(ka("PARTN"), [("0500", "HYVINKÄÄ"), ("0010", "Köping"), ("0310", "OSLO")]))
b.map(f"{P}/PostalCode", use_key(ka("PARTN"), [("0500", "05800"), ("0010", "73129"), ("0310", "1081")]))
b.map(f"{P}/CountryCode", ka("LAND1"))
b.map(f"{P}/Contact", exists(ka("BNAME")))            # optional inside the AG segment, same E1EDKA1 context
b.map(f"{P}/Contact/@Type", C("PD"))
b.map(f"{P}/Contact/ContactName", ka("BNAME"))
b.map(f"{P}/Contact/CommId", F("replaceString", F("replaceString", ka("TELF1", default=False), C("-"), C("")),
                               C(" "), C("")))
b.map(f"{P}/Contact/CommId/@Type", C("TE"))

# Party CN = Party[2] (#32-39): WE partner, all fields straight
P = f"{T}/Party[2]"
b.map(P, party_if("WE"))
b.map(f"{P}/@Role", C("CN"))
b.map(f"{P}/PartyId", ka("PARTN", default=False))
b.map(f"{P}/PartyId/@Type", C("ZTI"))
b.map(f"{P}/PartyId[1]", ka("LIFNR", default=False))
b.map(f"{P}/PartyId[1]/@Type", C("100"))
b.map(f"{P}/PartyName1", ka("NAME1", default=False))
b.map(f"{P}/AddressLine1", ka("STRAS", default=False))      # user 2026-11-24: keep the street
b.map(f"{P}/AddressLine2", ka("PFACH"))
b.map(f"{P}/AddressLine3", ka("ORT01", default=False))
b.map(f"{P}/PostalCode", F("replaceString", ka("PSTLZ"), C(" "), C("")))
b.map(f"{P}/CountryCode", ka("LAND1"))

# ---- Commercial terms (#40-42) ----------------------------------------------------------
b.map(f"{T}/Currency", C("EUR"))                                                   # OP-20
b.map(f"{T}/Currency/@Type", C("5"))
K17 = f"{I}/E1EDK17"
lkond = F("mapWithDefault", S(f"{K17}/LKOND"), default_value="")
lktext = F("mapWithDefault", S(f"{K17}/LKTEXT"), default_value="")
# segment-level filter: QUALF 001 in the IDOC context, fields 1:1 from the same E1EDK17
b.map(f"{T}/TermsOfDelivery", F("createIf", F("stringEquals", S(f"{K17}/QUALF", context=I), C("001"))))
b.map(f"{T}/TermsOfDelivery/@Type", C("6"))
b.map(f"{T}/TermsOfDelivery/TermsOfDeliveryCode", lkond)
b.map(f"{T}/TermsOfDelivery/TermsOfDeliveryCode/@CodeSet", C("Z2K"))
b.map(f"{T}/TermsOfDelivery/Location", exists(lktext))
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
b.map(f"{T}/Item/Property", prop_text)              # segment from the same chain as PropertyText (createIf rule)
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
