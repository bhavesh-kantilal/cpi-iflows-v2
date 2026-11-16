"""Build Map_RaaheTilkkuHub_TibnorS4_DeliveryNotice_DESADV.

Run:  py -I mappings/8_DESADV_RaaheTilkku-to-Tibnor/build_mapping.py
Rows (#) refer to sheet 'Mapping' of 1000761_DESADV_RaaheTilkku-to-Tibnor_MappingSpec_v0.1.xlsx (shared spec for the
Raahe and Hämeenlinna Tilkku mills). Design and decisions: spec.md.

One mapping per mill (user 2026-11-16). The logic lives in build(mill); the Hämeenlinna Tilkku mapping
(mappings/12_DESADV_HameenlinnaTilkku-to-Tibnor/build_mapping.py) calls it with its own MILL values.
The mills differ in the item grouping (VM-02):
  * Raahe:       key = first 8 characters of SinglePartId, one E1EDL11 per item with the key
  * Hämeenlinna: key = heat number (MaterialBatch HEAT), one E1EDL11 per SinglePart (first 8 characters of its id)

Grouping with standard functions only (user 2026-11-16, CLAUDE.md R1 pattern, no sort step):
  part values are flattened (one value per SinglePart, document order), the group key is line + key, and
  groups = SplitByValue[value change](key). It groups CONSECUTIVE equal keys only: the parts of one group must
  arrive next to each other (true in all samples).
  * one E1EDL24 per group:   collapseContexts(groups)
  * a part value per group:  SplitByValue[each](collapseContexts(formatByExample(value, groups)))
  * pieces per group:        SplitByValue[each](sum(formatByExample(pieces, groups)))   (L1 ACC, R1)
UDF: getBuyerOrderId (same logic as the PO UDF) for "order number = BuyersOrderId before the first '-'".
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
    name="Map_RaaheTilkkuHub_TibnorS4_DeliveryNotice_DESADV",
    gln="00372389445741",            # VM-01: Header/InterchangeSender of Raahe Tilkku
    sndprn="0000080067",
    vendor="80067",                  # E1ADRM1 PARTNER_ID (vendor without leading zeros)
    group_by="part_id",              # VM-02: first 8 characters of SinglePartId
)
NS_URI, NS = "http://www.ruukki.com/schemas/eai/rucomef/otc", "ns0"
CALEND = {"calend": [("fd", "1"), ("md", "1"), ("le", "true")]}       # as reference INV TransformDate


def build(mill: dict):
    b = Builder(mill["name"],
                # DeliveryBatch_0_8_1.xsd: the samples are 0.8.4, which only adds SinglePart/SlabManufacturerParty
                # (not used). User decision 2026-11-16: build with 0_8_1 until 0_8_4 is available.
                source=Link("xsd", ["DeliveryBatch_0_8_1.xsd", "src/main/resources/xsd", "DeliveryBatch", NS_URI]),
                target=Link("xsd", ["DESADV.DELVRY01.xsd", "src/main/resources/xsd", "DELVRY01"]),
                namespaces=[(NS, NS_URI)])
    C, F = b.const, b.fn

    def S(path: str, context: str | None = None):
        def ns(p):
            return "/" + "/".join(s if s.startswith("@") else f"{NS}:{s}" for s in p.strip("/").split("/"))
        return b.src(ns(path), context=ns(context) if context else None)

    def eq(a, value):
        return F("stringEquals", a, C(value))

    def by_key(node, key, value, field):
        """node/field where node/key = value (key is a child element). PO D_7140 pattern."""
        return F("ifWithoutElse", eq(F("mapWithDefault", S(f"{node}/{key}"), default_value=""), value),
                 F("mapWithDefault", S(f"{node}/{field}"), default_value=""), keepss="false")

    H = "/DeliveryBatch"
    LN = f"{H}/DeliveryBatchLine"
    SP = f"{LN}/SinglePart"
    T = "/DELVRY01/IDOC"

    # ---- header values ------------------------------------------------------------------------
    is_mill = eq(S(f"{H}/Header/InterchangeSender"), mill["gln"])                       # VM-01
    order_no = b.udf("getBuyerOrderId", "getBuyerOrderId", F("removeContexts", by_key(
        f"{H}/Reference", "ReferenceType", "BuyersOrderId", "ReferenceId")))           # #8
    order_10 = F("formatNumber", order_no, nformat="0000000000", separator=".")       # #15, #21, #25
    desp_date = F("TransformDate", S(f"{H}/DespatchDate"), iform="yyyy-MM-dd", oform="yyyyMMdd", calend=CALEND)

    # ---- part values: one per SinglePart, flattened (document order) -----------------------------
    def per_part(line_field):
        """Line value repeated once per SinglePart of that line (SinglePart node: one context per line)."""
        sp = S(SP)
        return F("removeContexts", F("useOneAsMany", F("mapWithDefault", S(f"{LN}/{line_field}"), default_value=""),
                                     sp, sp))

    def part_id8():
        return F("substring", F("removeContexts", S(f"{SP}/SinglePartId")), start="0", count="8")

    if mill["group_by"] == "part_id":
        part_key = part_id8()
    else:                                                     # heat number of the SinglePart
        part_key = F("removeContexts", by_key(f"{SP}/MaterialBatch", "MaterialBatchType", "HEAT", "MaterialBatchId"))
    # line + key, so that equal keys of two lines never fall into one group
    groups = F("SplitByValue", F("concat", per_part("DeliveryBatchLineId"), part_key, delimeter=":"), type="2")

    def per_group(flat):
        """One value per group (first part of the group), one context per group."""
        return F("SplitByValue", F("collapseContexts", F("formatByExample", flat, groups)), type="0")

    def on_each_group(v):
        """Header value on every E1EDL24: CopyValue index 0 (CLAUDE.md rule)."""
        return F("CopyValue", v, nnumber="0")

    pieces = F("removeContexts", by_key(f"{SP}/DespatchedQuantity", "ValueName", "Pieces", "Value"))
    posnr = F("formatNumber", per_group(per_part("DeliveryBatchLineId")), nformat="#", separator=".")   # #12
    article = per_group(per_part("CustomersArticleId"))                                                # #13-14

    # ---- control record EDI_DC40 (#1-7) ---------------------------------------------------------
    b.map("/DELVRY01", C(""))
    b.map(T, C(""))
    b.map(f"{T}/@BEGIN", C("1"))
    D = f"{T}/EDI_DC40"
    b.map(D, C(""))
    b.map(f"{D}/@SEGMENT", C("1"))
    b.map(f"{D}/TABNAM", C("EDI_DC40"))
    b.map(f"{D}/DIRECT", C("2"))
    b.map(f"{D}/IDOCTYP", C("DELVRY01"))
    b.map(f"{D}/MESTYP", C("DESADV"))
    b.map(f"{D}/STD", C("E"))                                 # #7 OP-05: as today's IDoc
    b.map(f"{D}/STDVRS", C("93A"))
    b.map(f"{D}/STDMES", C("DESADV"))
    b.map(f"{D}/SNDPOR", F("getProperty", C("SNDPOR")))      # #3 OP-05 ('INOBIZ' today)
    b.map(f"{D}/SNDPRT", F("ifWithoutElse", is_mill, C("LI"), keepss="false"))
    b.map(f"{D}/SNDPFC", F("ifWithoutElse", is_mill, C("LF"), keepss="false"))
    b.map(f"{D}/SNDPRN", F("ifWithoutElse", is_mill, C(mill["sndprn"]), keepss="false"))
    b.map(f"{D}/SNDLAD", S(f"{H}/Header/InterchangeSender"))
    b.map(f"{D}/RCVPOR", F("getProperty", C("RCVPOR")))
    b.map(f"{D}/RCVPRT", C("LS"))
    b.map(f"{D}/RCVPRN", F("getProperty", C("RCVPRN")))      # #4 OP-05
    b.map(f"{D}/RCVLAD", S(f"{H}/Header/InterchangeRecipient"))

    # ---- delivery header E1EDL20 (#8-10) -----------------------------------------------------------
    L20 = f"{T}/E1EDL20"
    b.map(L20, C(""))
    b.map(f"{L20}/@SEGMENT", C("1"))
    b.map(f"{L20}/VBELN", order_no)
    b.map(f"{L20}/E1ADRM1", C(""))
    b.map(f"{L20}/E1ADRM1/@SEGMENT", C("1"))
    b.map(f"{L20}/E1ADRM1/PARTNER_Q", C("LF"))
    b.map(f"{L20}/E1ADRM1/PARTNER_ID", F("ifWithoutElse", is_mill, C(mill["vendor"]), keepss="false"))
    b.map(f"{L20}/E1EDT13", C(""))
    b.map(f"{L20}/E1EDT13/@SEGMENT", C("1"))
    b.map(f"{L20}/E1EDT13/QUALF", C("007"))
    b.map(f"{L20}/E1EDT13/NTANF", desp_date)

    # ---- delivery items E1EDL24, one per line + group (#11-27) ------------------------------------
    P = f"{L20}/E1EDL24"
    b.map(P, F("collapseContexts", groups))                   # #11
    b.map(f"{P}/@SEGMENT", C("1"))
    b.map(f"{P}/POSNR", posnr)
    b.map(f"{P}/MATNR", article)
    b.map(f"{P}/ARKTX", on_each_group(order_10))
    b.map(f"{P}/KDMAT", article)
    b.map(f"{P}/LFIMG", F("formatNumber", F("SplitByValue", F("sum", F("formatByExample", pieces, groups)), type="0"),
                          nformat="#", separator="."))        # #16 sum of pieces, whole number
    b.map(f"{P}/VRKME", C("PCE"))                             # #17
    b.map(f"{P}/ABRDT", on_each_group(desp_date))
    if mill["group_by"] == "part_id":                         # #19 Raahe: one E1EDL11 with the group key
        b.map(f"{P}/E1EDL11", C(""))
        b.map(f"{P}/E1EDL11/@SEGMENT", C("1"))
        b.map(f"{P}/E1EDL11/SERNR", per_group(part_id8()))
    else:                                                     # #19 Hämeenlinna: one E1EDL11 per SinglePart
        sernr = F("formatByExample", part_id8(), groups)
        b.map(f"{P}/E1EDL11", sernr)
        b.map(f"{P}/E1EDL11/@SEGMENT", C("1"))
        b.map(f"{P}/E1EDL11/SERNR", sernr)
    b.map(f"{P}/E1EDL43", C(""))                              # #20-23
    b.map(f"{P}/E1EDL43/@SEGMENT", C("1"))
    b.map(f"{P}/E1EDL43/QUALF", C("V"))
    b.map(f"{P}/E1EDL43/BELNR", on_each_group(order_10))
    b.map(f"{P}/E1EDL43/POSNR", posnr)
    b.map(f"{P}/E1EDL43/DATUM", on_each_group(desp_date))
    b.map(f"{P}/E1EDL41", C(""))                              # #24-27
    b.map(f"{P}/E1EDL41/@SEGMENT", C("1"))
    b.map(f"{P}/E1EDL41/QUALI", C("001"))
    b.map(f"{P}/E1EDL41/BSTNR", on_each_group(order_10))
    b.map(f"{P}/E1EDL41/BSTDT", on_each_group(desp_date))
    b.map(f"{P}/E1EDL41/POSEX", posnr)
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
