"""Build Map_HammelinnaMetocsHub_TibnorS4_DeliveryNotice_DESADV.

Run:  py -I "mappings/3_Tibnor SSABEuropeHameenlinnaMetocs [80008] EDI DESADV in/build_mapping.py"
Rows (#) refer to sheet 'Mapping' of 25208_DESADV_HameenlinnaMetocs-to-Tibnor_MappingSpec_v0.1.xlsx.
Design, assumptions and decisions: spec.md.

Conventions taken over from ORDRSP v1.0.2 (FORMAT_NOTES §2.2, §3.6, CLAUDE.md):
  * namespaced source XSD: ns0: on every element step, 4th link elem = targetNamespace
  * qualifier filters follow the user's PO pattern, no context settings on source fields
  * EDI_DC40 as ORDRSP (getProperty SNDPOR/RCVPOR/RCVPRN, STD constants)
E1EDL24 grouping (line + heat, spec row 11) is the one Groovy UDF groupByHeat (user decision 2026-11-13).
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

NAME = "Map_HammelinnaMetocsHub_TibnorS4_DeliveryNotice_DESADV"
NS_URI, NS = "http://www.ruukki.com/schemas/eai/rucomef/otc", "ns0"
CALEND = {"calend": [("fd", "1"), ("md", "1"), ("le", "true")]}       # as reference INV TransformDate

b = Builder(NAME,
            source=Link("xsd", ["DeliveryBatch_0_8_1.xsd", "src/main/resources/xsd", "DeliveryBatch", NS_URI]),
            target=Link("xsd", ["DESADV.DELVRY01.xsd", "src/main/resources/xsd", "DELVRY01"]),
            namespaces=[(NS, NS_URI)])
C, F = b.const, b.fn


def S(path: str):
    """Source field; ns0: on every element step (FORMAT_NOTES §2.2, qualified XSD)."""
    return b.src("/" + "/".join(s if s.startswith("@") else f"{NS}:{s}" for s in path.strip("/").split("/")))


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
is_metocs = F("startWith2", S(f"{H}/SourceSystem"), C("METOCS"))                          # VM-01
po_no = F("removeContexts", by_key(f"{H}/Reference", "ReferenceType", "BuyersOrderId", "ReferenceId"))
cargo_id = F("removeContexts", by_key(f"{H}/Reference", "ReferenceType", "CargoId", "ReferenceId"))
desp_date = F("TransformDate", S(f"{H}/DespatchDate"), iform="yyyy-MM-dd", oform="yyyyMMdd", calend=CALEND)

# ---- grouping UDF (#11): inputs = one value per SinglePart, flattened ------------------------
sp_node = S(SP)                                         # SinglePart occurrences, one context per line


def per_bundle(line_field):
    """Line value repeated once per SinglePart of that line, then flattened."""
    return F("removeContexts", F("useOneAsMany", F("mapWithDefault", S(f"{LN}/{line_field}"), default_value=""),
                                 sp_node, sp_node))


def bundle_qty(name, field="Value"):
    return F("removeContexts", by_key(f"{SP}/DespatchedQuantity", "ValueName", name, field))


groups = b.udf("groupByHeat", "groupByHeat",
               per_bundle("DeliveryBatchLineId"),
               per_bundle("CustomersArticleId"),
               F("removeContexts", by_key(f"{SP}/MaterialBatch", "MaterialBatchType", "Heat", "MaterialBatchId")),
               bundle_qty("Weight"), bundle_qty("Pieces"), bundle_qty("Meters"), bundle_qty("Meters", "ValueUnit"),
               context_param=True)
OUT = {k: i for i, k in enumerate(["posnr", "matnr", "sernr", "lfimg", "usr01", "usr03", "vrkme"])}


def g(name):
    """Group value for an E1EDL24 child: UDF output -> SplitByValue (Each Value)."""
    return F("SplitByValue", b.out(groups, OUT[name]), type="0")


def per_group(v):
    """Header value on every group (E1EDL24): CopyValue index 0 (CLAUDE.md rule, ORDRSP v1.0.3)."""
    return F("CopyValue", v, nnumber="0")


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
b.map(f"{D}/STD", C("E"))
b.map(f"{D}/STDVRS", C("96A"))
b.map(f"{D}/STDMES", C("DESADV"))
b.map(f"{D}/SNDPOR", F("getProperty", C("SNDPOR")))      # OP-10: 'INOBIZ' today
b.map(f"{D}/SNDPRT", F("ifWithoutElse", is_metocs, C("LI"), keepss="false"))
b.map(f"{D}/SNDPFC", F("ifWithoutElse", is_metocs, C("LF"), keepss="false"))
b.map(f"{D}/SNDPRN", F("ifWithoutElse", is_metocs, C("0000080008"), keepss="false"))
b.map(f"{D}/SNDLAD", S(f"{H}/Header/InterchangeSender"))
b.map(f"{D}/RCVPOR", F("getProperty", C("RCVPOR")))
b.map(f"{D}/RCVPRT", C("LS"))
b.map(f"{D}/RCVPRN", F("getProperty", C("RCVPRN")))
b.map(f"{D}/RCVLAD", S(f"{H}/Header/InterchangeRecipient"))

# ---- delivery header E1EDL20 (#8-10) -----------------------------------------------------------
L20 = f"{T}/E1EDL20"
b.map(L20, C(""))
b.map(f"{L20}/@SEGMENT", C("1"))
b.map(f"{L20}/VBELN", cargo_id)
b.map(f"{L20}/E1ADRM1", C(""))
b.map(f"{L20}/E1ADRM1/@SEGMENT", C("1"))
b.map(f"{L20}/E1ADRM1/PARTNER_Q", C("LF"))
b.map(f"{L20}/E1ADRM1/PARTNER_ID", F("ifWithoutElse", is_metocs, C("80008"), keepss="false"))
b.map(f"{L20}/E1EDT13", C(""))
b.map(f"{L20}/E1EDT13/@SEGMENT", C("1"))
b.map(f"{L20}/E1EDT13/QUALF", C("007"))
b.map(f"{L20}/E1EDT13/NTANF", desp_date)

# ---- delivery items E1EDL24, one per line + heat (#11-27) -------------------------------------
P = f"{L20}/E1EDL24"
b.map(P, b.out(groups, OUT["posnr"]))
b.map(f"{P}/@SEGMENT", C("1"))
b.map(f"{P}/POSNR", g("posnr"))
b.map(f"{P}/MATNR", g("matnr"))
b.map(f"{P}/ARKTX", per_group(po_no))                    # OP-08: PO number in the description
b.map(f"{P}/KDMAT", g("matnr"))
b.map(f"{P}/LFIMG", g("lfimg"))
b.map(f"{P}/VRKME", g("vrkme"))
b.map(f"{P}/ABRDT", per_group(desp_date))                # OP-09: DespatchDate
b.map(f"{P}/USR01", g("usr01"))
b.map(f"{P}/USR03", g("usr03"))
b.map(f"{P}/E1EDL11", C(""))                             # one heat per group
b.map(f"{P}/E1EDL11/@SEGMENT", C("1"))
b.map(f"{P}/E1EDL11/SERNR", g("sernr"))
b.map(f"{P}/E1EDL43", C(""))
b.map(f"{P}/E1EDL43/@SEGMENT", C("1"))
b.map(f"{P}/E1EDL43/QUALF", C("V"))
b.map(f"{P}/E1EDL43/BELNR", per_group(po_no))
b.map(f"{P}/E1EDL43/POSNR", g("posnr"))
b.map(f"{P}/E1EDL43/DATUM", per_group(desp_date))
b.map(f"{P}/E1EDL41", C(""))
b.map(f"{P}/E1EDL41/@SEGMENT", C("1"))
b.map(f"{P}/E1EDL41/QUALI", C("001"))
b.map(f"{P}/E1EDL41/BSTNR", per_group(po_no))
b.map(f"{P}/E1EDL41/BSTDT", per_group(desp_date))
b.map(f"{P}/E1EDL41/POSEX", g("posnr"))

m = b.finish()

if __name__ == "__main__":
    z = package(m, HERE, HERE / "build")
    errs = check_build(z, NAME) + check_paths(m, HERE / "build" / NAME)
    print(z.name, f"{len(m.targets)} targets")
    print("\n".join(errs) if errs else "ALL CHECKS PASSED")
    sys.exit(1 if [e for e in errs if not e.startswith("NOTE")] else 0)
