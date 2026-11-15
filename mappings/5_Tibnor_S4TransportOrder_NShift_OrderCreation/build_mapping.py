"""Build Map_TibnorS4_NShift_TransportOrder_Book.

Run:  py -I mappings/5_Tibnor_S4TransportOrder_NShift_OrderCreation/build_mapping.py
There is no mapping sheet for this interface: spec.md IS the spec (best guess, with assumptions A1..).

Source: S/4 TM TransportationOrderRequest (freight order), schemas/S4_TransportationOrderRequest_Out.wsdl
        (= the user's Source.wsdl, unqualified elements: only the root carries ns0:, as MAT).
Target: NShift ConsignmentWS method 'book' (user: use book, not save), schemas/NShift_ConsignmentWS.wsdl
        (= the user's Target.wsdl with the two imported NShift XSDs inlined, tools/wsdl_inline.py).
        book and its local children are unqualified; the leaf fields (id, name, weight, date ...) are global
        elements of namespace .../consignment/types/v1_0 and get their own prefix mid-path (as JE, FORMAT_NOTES §2.2).
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

NAME = "Map_TibnorS4_NShift_TransportOrder_Book"
NS_SRC = "http://sap.com/xi/SAPGlobal20/Global"
NS_BOOK = "http://www.spedpoint.com/consignment/types"
NS_V1 = "http://www.spedpoint.com/consignment/types/v1_0"

b = Builder(NAME,
            source=Link("wsdl", ["S4_TransportationOrderRequest_Out.wsdl", "src/main/resources/wsdl",
                                 "TransportationOrderRequest", NS_SRC]),
            # elem 3 = the message *element* 'book' (WSDL message is 'ConsignmentEndpoint_book'): UNVERIFIED,
            # in all references message and element share one name.
            target=Link("wsdl", ["NShift_ConsignmentWS.wsdl", "src/main/resources/wsdl", "book", NS_BOOK]),
            namespaces=[("ns0", NS_SRC), ("ns1", NS_BOOK), ("ns2", NS_V1)])
C, F = b.const, b.fn

TD = "/ns0:TransportationOrderRequest/TransportationDocument"
IT = f"{TD}/Item"
K = "/ns1:book"
CO = f"{K}/Consignment"


def S(rel):
    return b.src(f"{TD}/{rel}")


def eq(a, value):
    return F("stringEquals", a, C(value))


def has(v):
    """true when v (header level, may be missing) is not empty."""
    return F("not", eq(F("mapWithDefault", v, default_value=""), ""))


def nonempty(v):
    return F("ifWithoutElse", has(v), v, keepss="false")


def local_date(dt, tz):
    """S/4 UTC date-time -> NShift local calendar day 'yyyy-MM-dd' (UDF, see scripts/toLocalDate.groovy)."""
    return b.udf("toLocalDate", "toLocalDate", dt, F("mapWithDefault", tz, default_value=""))


# ---- header values ----------------------------------------------------------------------------
fo_no = S("BaseBusinessTransactionDocumentReference/ID")            # A2: freight order number (TypeCode 1122)

# ---- goods rows (UDF goodsItemFlags): one flag + SSCC per Item, flattened ----------------------
item_id = S("Item/ID")
hier = S("Item/HierarchyRelationship")
pkg = S("Item/Package")
goods = b.udf("goodsItemFlags", "goodsItemFlags",
              F("removeContexts", item_id),
              F("removeContexts", F("mapWithDefault", S("Item/CategoryCode"), default_value="")),
              F("removeContexts", F("useOneAsMany", item_id, hier, hier)),
              F("removeContexts", S("Item/HierarchyRelationship/ParentItemID")),
              F("removeContexts", F("useOneAsMany", item_id, pkg, pkg)),
              F("removeContexts", S("Item/Package/ID")),
              context_param=True)
is_goods = eq(goods, "true")                                       # output 0, one value per Item


def per_item(field, default=""):
    """Item field, one value per Item, flattened (mapWithDefault in the Item's own context fills gaps)."""
    return F("removeContexts", F("mapWithDefault", S(f"Item/{field}"), default_value=default))


def g(v):
    """Per-Item value -> goods rows only, one context per goods row (PO pattern)."""
    return F("SplitByValue", F("removeContexts", F("ifWithoutElse", is_goods, v, keepss="false")), type="0")


def num(field, nformat, divisor=None):
    """Numeric Item field, formatted; missing -> '0' -> element left out (no arithmetic on empty values)."""
    raw = per_item(field, "0")
    val = F("div", raw, C(divisor)) if divisor else raw
    return F("ifWithoutElse", F("not", eq(raw, "0")), F("formatNumber", val, nformat=nformat, separator="."),
             keepss="false")


# ---- AuthenticationToken + transactionId -----------------------------------------------------
b.map(K, C(""))
b.map(f"{K}/AuthenticationToken", C(""))
b.map(f"{K}/AuthenticationToken/userName", F("getProperty", C("NShift_UserName")))       # A6
b.map(f"{K}/AuthenticationToken/groupName", F("getProperty", C("NShift_GroupName")))
b.map(f"{K}/AuthenticationToken/password", F("getProperty", C("NShift_Password")))
b.map(f"{K}/transactionId", fo_no)                                                     # A7: idempotent per FO

# ---- Consignment ---------------------------------------------------------------------------------
b.map(CO, C(""))
b.map(f"{CO}/@orderNo", fo_no)
b.map(f"{CO}/@templateName", F("getProperty", C("NShift_TemplateName")))               # A5


def part(idx, role, src):
    """Part[idx] with role, from S/4 party/location src (InternalID + Address)."""
    P = f"{CO}/Part" + (f"[{idx}]" if idx else "")
    A = f"{src}/Address"
    PA = f"{A}/PhysicalAddress"
    b.map(P, C(""))
    b.map(f"{P}/@role", C(role))
    b.map(f"{P}/Address", C(""))
    b.map(f"{P}/Address/ns2:id", S(f"{src}/InternalID"))
    b.map(f"{P}/Address/ns2:name", S(f"{A}/OrganisationFormattedName"))
    street = F("trim", F("concat", F("mapWithDefault", S(f"{PA}/StreetName"), default_value=""),
                         F("mapWithDefault", S(f"{PA}/HouseID"), default_value=""), delimeter=" "))
    b.map(f"{P}/Address/ns2:address", street)
    b.map(f"{P}/Address/ns2:postcode", S(f"{PA}/StreetPostalCode"))
    b.map(f"{P}/Address/ns2:city", S(f"{PA}/CityName"))
    b.map(f"{P}/Address/ns2:countrycode", S(f"{PA}/CountryCode"))
    phone = S(f"{A}/Communication/Telephone/Number/SubscriberID")
    email = S(f"{A}/Communication/Email/URI")
    b.map(f"{P}/Communication", F("createIf", F("or", has(phone), has(email))))        # A10
    # createIf on the segment -> straight maps for its fields (CLAUDE.md createIf rule)
    b.map(f"{P}/Communication/ns2:phone", phone)
    b.map(f"{P}/Communication/email", email)


part(0, "consignor", "ShipperParty")                                                    # A3
part(1, "consignee", "ConsigneeParty")
part(2, "deliveryAddress", "ShipToLocation")

# ---- GoodsItem: one per top-level package (A4) -------------------------------------------------
GI = f"{CO}/GoodsItem"
sscc = g(b.out(goods, 1))
b.map(GI, F("removeContexts", F("ifWithoutElse", is_goods, C(""), keepss="false")))
b.map(f"{GI}/ns2:noOfPackages", g(F("formatNumber", per_item("PiecesTransportationQuantity", "1"),
                                    nformat="0", separator=".")))
b.map(f"{GI}/ns2:weight", g(num("GrossWeightTransportationQuantity", "0.00")))       # KGM (A8)
b.map(f"{GI}/ns2:volume", g(num("GrossVolumeTransportationQuantity", "0.000", "10")))  # HLT -> m3
b.map(f"{GI}/ns2:length", g(num("LengthMeasure", "0.00", "10")))                       # MMT -> cm
b.map(f"{GI}/ns2:width", g(num("WidthMeasure", "0.00", "10")))
b.map(f"{GI}/ns2:height", g(num("HeightMeasure", "0.00", "10")))
b.map(f"{GI}/ns2:packageType", g(b.table("FixValues", per_item("Description"),
                                         [("Bunt", "BE"), ("Helpall", "PX")], default="PK", strategy="1")))  # A9
b.map(f"{GI}/ns2:tag", F("ifWithoutElse", F("not", eq(sscc, "")), sscc, keepss="false"))
b.map(f"{GI}/ns2:netWeight", g(num("NetWeightTransportationQuantity", "0.00")))
b.map(f"{GI}/ns2:weightUnit", C("kg"))
b.map(f"{GI}/ns2:volumeUnit", C("m3"))
b.map(f"{GI}/ns2:lengthUnit", C("cm"))
b.map(f"{GI}/ns2:notes", g(per_item("Description")))
b.map(f"{GI}/PackageIds", F("createIf", F("not", eq(sscc, ""))))
b.map(f"{GI}/PackageIds/ns2:code", sscc)

# ---- TransportProduct ----------------------------------------------------------------------------
TP = f"{CO}/TransportProduct"
b.map(TP, C(""))
b.map(f"{TP}/PaymentInstruction", C(""))
rpa = S("RevenuePaymentArrangementCode")                                                # A11
b.map(f"{TP}/PaymentInstruction/@value", F("iF", C("C"), eq(rpa, "CC"), C("P")))
inco = S("DeliveryTerms/Incoterms/ClassificationCode")
b.map(f"{TP}/Tod", F("createIf", has(inco)))
b.map(f"{TP}/Tod/ns2:combiterm", inco)
b.map(f"{TP}/Tod/ns2:location", S("DeliveryTerms/Incoterms/TransferLocationName"))   # straight under createIf
pickup = local_date(S("RequestedPickupDateTimePeriod/StartDateTime"), S("ShipFromLocationAddressTimeZoneCode"))
delivery = local_date(S("RequestedDeliveryDateTimePeriod/StartDateTime"), S("ShipToLocationAddressTimeZoneCode"))
b.map(f"{TP}/Pickup", C(""))
b.map(f"{TP}/Pickup/ns2:date", pickup)
b.map(f"{TP}/Delivery", C(""))
b.map(f"{TP}/Delivery/ns2:date", delivery)

# ---- Target (planned delivery date, required) -------------------------------------------------
b.map(f"{CO}/Target", C(""))
b.map(f"{CO}/Target/ns2:date", delivery)

m = b.finish()

def wsdl_import_test():
    """User's test (2026-11-15): does CPI resolve the NShift types when the XSDs are imported into the mapping
    as separate resources, instead of being inlined in the WSDL? Two variants, same mapping logic as the build:
      A  NShift_ConsignmentWS_urlimport.wsdl  = the user's Target.wsdl byte for byte (imports by https URL)
      B  NShift_ConsignmentWS_fileimport.wsdl = Target.wsdl with only the two schemaLocation values changed
                                                 to the plain XSD file names
    Output: build/test_wsdl_import/<Name>_TestA/B.zip (mapping + WSDL + scripts, NO XSDs) and xsd_to_import/."""
    import copy
    import re
    import shutil
    S_ = HERE / "schemas"
    out = HERE / "build" / "test_wsdl_import"
    xsds = {"https://service.web-ta.net/ws/services/ConsignmentWS?xsd=1": "ConsignmentWS_xsd1.xsd",
            "https://service.web-ta.net/ws/services/ConsignmentWS?xsd=2": "ConsignmentWS_xsd2.xsd"}
    src = (S_ / "Target.wsdl").read_bytes()
    (S_ / "NShift_ConsignmentWS_urlimport.wsdl").write_bytes(src)
    rel = src
    for url, f in xsds.items():
        rel, n = re.subn(rb'schemaLocation="' + re.escape(url.encode()) + rb'"', b'schemaLocation="' + f.encode() + b'"', rel)
        assert n == 1, url
    (S_ / "NShift_ConsignmentWS_fileimport.wsdl").write_bytes(rel)
    (out / "xsd_to_import").mkdir(parents=True, exist_ok=True)
    for f in xsds.values():
        shutil.copyfile(S_ / "downloaded" / f, out / "xsd_to_import" / f)
    for tag, wsdl in (("TestA", "NShift_ConsignmentWS_urlimport.wsdl"), ("TestB", "NShift_ConsignmentWS_fileimport.wsdl")):
        v = copy.deepcopy(m)
        v.name = f"{NAME}_{tag}"
        v.target.elems[0] = wsdl
        z = package(v, HERE, out)
        errs = check_build(z, v.name)
        expected = [e for e in errs if "unresolved" in e]          # types live in the XSDs imported in CPI
        other = [e for e in errs if e not in expected]
        print(z.name, f"| {len(expected)} expected unresolved type refs (XSDs not in the zip)",
              "| other checks:", "PASSED" if not other else other)


if __name__ == "__main__" and "--wsdl-import-test" in sys.argv:
    wsdl_import_test()
    sys.exit(0)

if __name__ == "__main__":
    z = package(m, HERE, HERE / "build")
    errs = check_build(z, NAME) + check_paths(m, HERE / "build" / NAME)
    print(z.name, f"{len(m.targets)} targets, UDF scripts {m.udfs}")
    print("\n".join(errs) if errs else "ALL CHECKS PASSED")
    sys.exit(1 if [e for e in errs if not e.startswith("NOTE")] else 0)
