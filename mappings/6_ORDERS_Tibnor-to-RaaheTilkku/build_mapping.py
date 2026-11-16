"""Build Map_TibnorS4_RaaheTilkkuHub_PurchaseOrder_ORDERS02.

Run:  py -I mappings/6_ORDERS_Tibnor-to-RaaheTilkku/build_mapping.py
Rows (#) refer to sheet 'Mapping' of 1002129_ORDERS_Tibnor-to-RaaheTilkku_MappingSpec_v0.1.xlsx. The Hämeenlinna
Tilkku spec (1002249) has the same rules except Property ZMA. Design and decisions: spec.md.

One mapping per mill (user 2026-11-16). The logic lives in build(mill); the Hämeenlinna Tilkku mapping
(mappings/10_ORDERS_Tibnor-to-HameenlinnaTilkku/build_mapping.py) calls it with its own MILL values.

Item characteristics (#33-54, #59-60): the E1CUCFG / E1CUVAL segments sit beside the items and point to them by
POSEX, with 1-3 E1CUCFG per item. No standard function joins two queues by a key, so one UDF does the lookup:
itemCharacteristic (scripts/itemCharacteristic.groovy): one VALUE / VALUE_TXT per item, empty when missing.
Each target then takes SplitByValue[each] (one context per item) and is created only for a non-empty value,
with the node and its fields fed from the same per-item chain (createIf rule, CLAUDE.md).
Other UDFs are reused unchanged: removezeros (IDTNR), hasBestText (Metocs ORDERS), substringSafe (udf_library).
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
    name="Map_TibnorS4_RaaheTilkkuHub_PurchaseOrder_ORDERS02",
    vendor="0000080067",                 # E1EDKA1[LF]-PARTN of this mill (VM-01 key)
    gln="00372389445741",                # VM-01 -> Header/InterchangeRecipient
    routing_out="RAMF.M.TILKKU",         # VM-01 -> Header/MessageRoutingOutbound (+ environment suffix)
    send_zma=True,                       # #44 Property ZMA: Raahe Tilkku only (OP-02 answered)
)
ENV_PROPERTY = "HubEnvironment"          # exchange property with PRD / TST (as Metocs ORDERS Q3)
VM04_SENDER = [("0010", "7340195700006"), ("0310", "7080003309006"), ("0500", "003723894430")]
VM04_BUYER = [("0010", "0100"), ("0310", "0300"), ("0500", "0500")]


def build(mill: dict):
    b = Builder(mill["name"],
                source=Link("xsd", ["ORDERS.ORDERS02.xsd", "src/main/resources/xsd", "ORDERS02"]),
                target=Link("xsd", ["Harmonized_Purchase_Order_0_0_7.xsd", "src/main/resources/xsd", "OrdersMessage"]))
    S, C, F = b.src, b.const, b.fn
    I = "/ORDERS02/IDOC"
    E = f"{I}/E1EDP01"
    CFG = f"{I}/E1CUCFG"
    T = "/OrdersMessage"

    # ---- patterns (functions from FORMAT_NOTES) ------------------------------------------------
    def eq(a, value):
        return F("stringEquals", a, C(value))

    def has(v):
        return F("not", eq(v, ""))

    def nonempty(v):
        """Pass v on only when it is not empty, so no empty target element is created."""
        return F("ifWithoutElse", has(v), v, keepss="false")

    def partner(parvw, field, default=""):
        """Field of the E1EDKA1 with PARVW = parvw (as Metocs ORDERS)."""
        return F("removeContexts",
                 F("ifWithoutElse", eq(S(f"{I}/E1EDKA1/PARVW"), parvw),
                   F("mapWithDefault", S(f"{I}/E1EDKA1/{field}"), default_value=default), keepss="false"))

    def header_qualified(seg, qkey, qval, field):
        return F("removeContexts",
                 F("ifWithoutElse", eq(S(f"{I}/{seg}/{qkey}"), qval),
                   F("mapWithDefault", S(f"{I}/{seg}/{field}"), default_value=""), keepss="false"))

    def table(inp, rows):
        return b.table("FixValues", inp, rows, default="", strategy="1")      # Use Default Value, empty

    def no_zeros(v):
        return F("formatNumber", v, nformat="#", separator=".")              # numeric source: leading zeros off

    def per_item(v):
        return F("CopyValue", v, nnumber="0")

    def characteristic(name):
        """UDF itemCharacteristic for CHARC = name: (VALUE, VALUE_TXT), each one value per item, one context per
        item. New bricks per call, so every target group keeps its own small canvas."""
        cfg_val = S(f"{CFG}/E1CUVAL")
        call = b.udf("itemCharacteristic", "itemCharacteristic",
                     S(f"{E}/POSEX", context=I),
                     F("removeContexts", F("useOneAsMany", S(f"{CFG}/POSEX"), cfg_val, cfg_val)),
                     F("removeContexts", S(f"{CFG}/E1CUVAL/CHARC")),
                     F("removeContexts", F("mapWithDefault", S(f"{CFG}/E1CUVAL/VALUE"), default_value="")),
                     F("removeContexts", F("mapWithDefault", S(f"{CFG}/E1CUVAL/VALUE_TXT"), default_value="")),
                     C(name), context_param=True)
        return (F("SplitByValue", b.out(call, 0), type="0"),
                F("SplitByValue", b.out(call, 1), type="0"))

    def when(cond, v):
        return F("ifWithoutElse", cond, v, keepss="false")

    # ---- header values -----------------------------------------------------------------------------
    ag_partn = partner("AG", "PARTN")
    lf_partn = partner("LF", "PARTN")
    belnr = no_zeros(S(f"{I}/E1EDK01/BELNR"))                                            # #9, #11
    date012 = header_qualified("E1EDK03", "IDDAT", "012", "DATUM")                       # #10, #12 (OP-07)
    env = F("getProperty", C(ENV_PROPERTY))

    # ---- Header (#1-8) ---------------------------------------------------------------------------
    b.map(T, C(""))
    b.map(f"{T}/Header", C(""))
    b.map(f"{T}/Header/SchemaId", C("EDI.ORDER"))
    b.map(f"{T}/Header/SchemaVersion", C("Harmonized_Purchase_Order_0_0_7.xsd"))
    b.map(f"{T}/Header/MessageFunction", C("9"))                                          # #3
    b.map(f"{T}/Header/OrderType", when(eq(S(f"{I}/E1EDK01/BSART"), "NB"), C("105")))    # #4 NB only (OP-03)
    b.map(f"{T}/Header/InterchangeSender", table(ag_partn, VM04_SENDER))                 # #5 VM-04
    b.map(f"{T}/Header/InterchangeRecipient", table(lf_partn, [(mill["vendor"], mill["gln"])]))   # #6 VM-01
    b.map(f"{T}/Header/MessageRoutingInbound", F("concat", C("SSCO.M.EDI"), env, delimeter=""))   # #7
    b.map(f"{T}/Header/MessageRoutingOutbound", F("concat", table(lf_partn, [(mill["vendor"], mill["routing_out"])]),
                                                  env, delimeter=""))                     # #8

    # ---- Document references and dates (#9-12) -------------------------------------------------
    b.map(f"{T}/DocumentId", C(""))
    b.map(f"{T}/DocumentId/DocumentNo", belnr)
    b.map(f"{T}/DocumentId/Date", date012)
    b.map(f"{T}/DocumentId/Date/@Type", C("4"))
    b.map(f"{T}/DocumentId/Date/@Format", C("102"))
    b.map(f"{T}/Reference", belnr)
    b.map(f"{T}/Reference/@Type", C("CR"))
    b.map(f"{T}/Date", date012)
    b.map(f"{T}/Date/@Type", C("137"))
    b.map(f"{T}/Date/@Format", C("102"))

    # ---- Party BY = Party (#13-17) ---------------------------------------------------------------
    P = f"{T}/Party"
    bname = partner("AG", "BNAME")
    b.map(P, C(""))
    b.map(f"{P}/@Role", C("BY"))
    b.map(f"{P}/PartyId", table(ag_partn, VM04_BUYER))
    b.map(f"{P}/PartyId/@Type", C("ZZZ"))
    b.map(f"{P}/PartyName1", partner("AG", "NAME1"))
    b.map(f"{P}/Contact", F("createIf", has(bname)))         # container only when there is a contact
    b.map(f"{P}/Contact/@Type", C("EB"))
    b.map(f"{P}/Contact/ContactName", F("trim", bname))        # straight under createIf
    b.map(f"{P}/Contact/CommId", nonempty(partner("AG", "TELF1")))    # #17 copy as it is
    b.map(f"{P}/Contact/CommId/@Type", C("TE"))

    # ---- Party MF = Party[1] (#18-19) ------------------------------------------------------------
    P = f"{T}/Party[1]"
    b.map(P, C(""))
    b.map(f"{P}/@Role", C("MF"))
    b.map(f"{P}/PartyId", no_zeros(lf_partn))
    b.map(f"{P}/PartyId/@Type", C("ZZZ"))

    # ---- Party CN = Party[2] (#20-25) ------------------------------------------------------------
    cn_id = no_zeros(partner("WE", "PARNR", default="0"))                                # #21 '0' without PARNR
    cn_name = partner("WE", "NAME1")
    cn_street = partner("WE", "STRAS")
    # #25 postal code filled with spaces to 8 characters + city in upper case (OP-13, OP-14: standard toUpperCase)
    cn_city = F("concat",
                F("substring", F("concat", partner("WE", "PSTLZ"), C("        "), delimeter=""), start="0", count="8"),
                F("toUpperCase", partner("WE", "ORT01")), delimeter="")
    P = f"{T}/Party[2]"
    b.map(P, C(""))
    b.map(f"{P}/@Role", C("CN"))
    b.map(f"{P}/PartyId", cn_id)
    b.map(f"{P}/PartyId/@Type", C("ZZZ"))
    b.map(f"{P}/PartyName1", cn_name)
    b.map(f"{P}/AddressLine1", cn_street)
    b.map(f"{P}/AddressLine2", nonempty(partner("WE", "PFACH")))                          # #24 left out when empty
    b.map(f"{P}/AddressLine3", cn_city)

    # ---- Commercial terms (#26-28) ---------------------------------------------------------------
    b.map(f"{T}/Currency", S(f"{I}/E1EDK01/CURCY"))
    b.map(f"{T}/Currency/@Type", C("5"))
    lkond = header_qualified("E1EDK17", "QUALF", "001", "LKOND")
    lktext = header_qualified("E1EDK17", "QUALF", "001", "LKTEXT")
    b.map(f"{T}/TermsOfDelivery", F("createIf", has(lkond)))
    b.map(f"{T}/TermsOfDelivery/@Type", C("6"))
    b.map(f"{T}/TermsOfDelivery/TermsOfDeliveryCode", lkond)
    b.map(f"{T}/TermsOfDelivery/TermsOfDeliveryCode/@CodeSet", C("Z2K"))
    b.map(f"{T}/TermsOfDelivery/Location", F("createIf", has(lktext)))
    b.map(f"{T}/TermsOfDelivery/Location/@Type", C("1"))
    b.map(f"{T}/TermsOfDelivery/Location/LocationText", lktext)

    # ---- Items (#29-64) -----------------------------------------------------------------------------
    IT = f"{T}/Item"
    idtnr001 = b.udf("removezeros", "removezeros",
                     when(eq(S(f"{E}/E1EDP19/QUALF", context=E), "001"), S(f"{E}/E1EDP19/IDTNR", context=E)))
    b.map(IT, S(E))                                                                       # #29
    b.map(f"{IT}/LineNo", no_zeros(S(f"{E}/POSEX")))                                     # #30
    b.map(f"{IT}/ArticleNo", idtnr001)                                                    # #31
    b.map(f"{IT}/ArticleNo/@Type", C("IN"))

    # #32 Property 44: first 35 characters of KTEXT (trailing spaces off), only for items with a BEST text
    has_best = b.udf("TibnorOrdersHelpers", "hasBestText", S(f"{E}/E1EDPT1/TDID", context=E), context_param=True)
    ktext001 = when(eq(S(f"{E}/E1EDP19/QUALF", context=E), "001"), S(f"{E}/E1EDP19/KTEXT", context=E))
    p44 = when(has_best, F("trim", b.udf("substringSafe", "substringSafe", ktext001, C("0"), C("35"))))
    props = [("44", p44, p44, None)]

    def prop(ptype, charc, code_from="value", text_from="txt", side=None):
        v, t = characteristic(charc)
        pick = {"value": v, "txt": t}
        props.append((ptype, pick[code_from], pick[text_from], side))

    prop("ZPF", "FORM")                                                                   # #33
    prop("ZTY", "FORM2")                                                                  # #34
    asla, _ = characteristic("ASLACODE")                                                  # #35
    _, kval = characteristic("KVALITET")
    props.append(("12", asla, kval, None))
    _, cert = characteristic("CERTIFICATE")                                              # #36 '3.1 CE' -> '31 CE'
    cert_code = F("replaceString", F("replaceString", cert, C("EN 10204-"), C("")), C("."), C(""))
    props.append(("1", cert_code, cert, None))
    pc_v, pc_t = characteristic("SSAB_PC")                                                # #37 (also Package)
    props.append(("53", pc_v, pc_t, None))
    prop("8", "TIKKU_GROUP", "value", "value")                                            # #38
    prop("35", "COLOUR_COATING_COLOUR_BACK", "value", "value", "BT")                      # #39
    prop("35", "COLOUR_COATING_COLOUR_FRONT", "value", "value", "TP")
    prop("17", "COLOUR_COATING_TYPE_BACK", side="BT")                                     # #40
    prop("17", "COLOUR_COATING_TYPE_FRONT", side="TP")
    prop("59", "PROTECTION")                                                              # #41
    prop("ZPI", "SURFACE_FINISH")                                                         # #42
    prop("ZED", "EDGE_CONDITION")                                                         # #43
    if mill["send_zma"]:
        prop("ZMA", "MARKING")                                                            # #44

    for n, (ptype, code, text, side) in enumerate(props):
        PP = f"{IT}/Property" + (f"[{n}]" if n else "")
        # #35: Property 12 exists when ASLACODE or KVALITET exists; the others when their value exists
        cond = F("or", has(code), has(text)) if ptype == "12" else has(code)
        b.map(PP, when(cond, C("")))
        b.map(f"{PP}/@Type", C(ptype))
        b.map(f"{PP}/PropertyCode", when(has(code), code))
        b.map(f"{PP}/PropertyCode/@CodeSet", C("91"))
        b.map(f"{PP}/PropertyText", when(has(text), text))
        if side:
            b.map(f"{PP}/PropertySide", C(side))

    # #45-48 Measurements: at most 2 decimals, no trailing zeros (format 0.##), unit MMT
    for n, (mtype, charc) in enumerate([("LN", "DIM_1"), ("WD", "DIM_2"), ("TH", "TJOCKLEK"),
                                        ("ID", "COIL_INNER_DIAMETER")]):
        v, _ = characteristic(charc)
        MP = f"{IT}/Measurement" + (f"[{n}]" if n else "")
        b.map(MP, when(has(v), C("")))
        b.map(f"{MP}/@Type", C(mtype))
        b.map(f"{MP}/MeasureValue", F("formatNumber", when(has(v), v), nformat="0.##", separator="."))
        b.map(f"{MP}/MeasureUnit", C("MMT"))

    # #49-50 Quantity 21 (every PO item has a quantity: container constant)
    b.map(f"{IT}/Quantity", C(""))
    b.map(f"{IT}/Quantity/@Type", C("21"))
    b.map(f"{IT}/Quantity/QuantityValue", F("formatNumber", S(f"{E}/MENGE"), nformat="0.###", separator="."))
    b.map(f"{IT}/Quantity/MeasureUnit", S(f"{E}/MENEE"))
    # #51-54 Quantity LL only when MAX_COILWEIGHT exists (OP-06)
    max_coil, _ = characteristic("MAX_COILWEIGHT")
    max_pack, _ = characteristic("MAX_PACK_WEIGHT")
    min_coil, _ = characteristic("MIN_COILWEIGHT")
    is_ll = has(max_coil)
    b.map(f"{IT}/Quantity[1]", when(is_ll, C("")))
    b.map(f"{IT}/Quantity[1]/@Type", C("LL"))
    b.map(f"{IT}/Quantity[1]/QuantityValue", when(is_ll, max_pack))
    b.map(f"{IT}/Quantity[1]/MeasureUnit", C("KGM"))
    b.map(f"{IT}/Quantity[1]/LowerTolerance", when(is_ll, min_coil))
    b.map(f"{IT}/Quantity[1]/UpperTolerance", when(is_ll, max_coil))

    # #55 Date: EDATU (one E1EDP20 per item in all samples, OP-08)
    b.map(f"{IT}/Date", S(f"{E}/E1EDP20/EDATU"))
    b.map(f"{IT}/Date/@Type", C("2"))
    b.map(f"{IT}/Date/@Format", C("102"))
    # #56-57 Price (every PO item has a price: container constant); VM-05 price basis
    pmene = S(f"{E}/PMENE")
    is_pt = F("or", eq(pmene, "TNE"),
              F("and", eq(pmene, "KGM"), eq(F("mapWithDefault", S(f"{E}/PEINH"), default_value=""), "1000")))
    b.map(f"{IT}/Price", C(""))
    b.map(f"{IT}/Price/@Type", C("AAA"))
    b.map(f"{IT}/Price/PriceValue", S(f"{E}/VPREI"))
    b.map(f"{IT}/Price/UnitPriceBasisCode", F("iF", C("PT"), is_pt, pmene))             # iF: then, cond, else
    # #58 Reference CR: order number + ' ' + article number
    b.map(f"{IT}/Reference", F("concat", per_item(belnr), idtnr001, delimeter=" "))
    b.map(f"{IT}/Reference/@Type", C("CR"))
    # #59-60 Package only when SSAB_PC exists (same characteristic as Property 53)
    b.map(f"{IT}/Package", when(has(pc_v), C("")))
    b.map(f"{IT}/Package/PackageTypeCode", when(has(pc_v), pc_v))
    b.map(f"{IT}/Package/PackageTypeCode/@CodeSet", C("92"))
    b.map(f"{IT}/Package/PackageTypeText", when(has(pc_v), pc_t))
    # #61-64 ship-to on every item (header values: CopyValue 0)
    b.map(f"{IT}/Party", C(""))
    b.map(f"{IT}/Party/@Role", C("CN"))
    b.map(f"{IT}/Party/PartyId", per_item(cn_id))
    b.map(f"{IT}/Party/PartyId/@Type", C("ZZZ"))
    b.map(f"{IT}/Party/PartyName1", per_item(cn_name))
    b.map(f"{IT}/Party/AddressLine1", per_item(cn_street))
    b.map(f"{IT}/Party/City", per_item(cn_city))

    # ---- Trailer (#65) ------------------------------------------------------------------------------
    b.map(f"{T}/NumberOfLineItems", F("count", S(f"{E}/POSEX", context=I)))
    return b.finish()


def run(mill: dict, here: Path) -> int:
    m = build(mill)
    z = package(m, here, here / "build")
    errs = check_build(z, mill["name"]) + check_paths(m, here / "build" / mill["name"])
    print(z.name, f"{len(m.targets)} targets, scripts {m.udfs}")
    print("\n".join(errs) if errs else "ALL CHECKS PASSED")
    return 1 if [e for e in errs if not e.startswith("NOTE")] else 0


if __name__ == "__main__":
    sys.exit(run(MILL, HERE))
