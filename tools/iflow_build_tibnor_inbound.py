"""
tools/iflow_build_tibnor_inbound.py
Inbound EDI from the Finnish message hub to Tibnor S4 (CPI package Tibnor_SSAB_EDIMigration,
repo folder iflows/Tibnor_SSAB_EDIMigration/). One parent + three mill children per message type:

  ORDRSP  IXXXX_P_OrderResponse_FinMessageHub_MQToJMS    route on Header/ApplicationId
  DESADV  IXXXX_P_DespatchAdvice_FinMessageHub_MQToJMS   route on SourceSystem + InterchangeSender, only for
  INVOIC  IXXXX_P_Invoice_FinMessageHub_MQToJMS          the PO recipient GLNs (user's PO conditions, 2026-11-24)

  parent   IBM MQ sender (+ Manual Retrigger) -> receiver determination -> JMS queue IXXXX_TibnorS4
           (dispatcher, not built here)
  children IXXXX_<Object>_FinMessageHub_<Mill>_TibnorS4_JMSToIDoc, <Mill> =
           HameenlinnaMetocs, HameenlinnaTilkku, RaaheTilkku
           ProcessDirect from the dispatcher -> the mill's mapping -> ProcessDirect to the shared
           IDoc flow T0143_P_IDocReceiver_TibnorS4_PDToIDoc

Templates (no XML structure invented, CLAUDE.md):
  parent  = our ORDERS parent IXXXX_P_PurchaseOrder_..._IDocToJMS (L3 shape from I2023_P)
  child   = our ORDERS child IXXXX_PurchaseOrder_..._JMSToMQ (L3 shape from I2018)
  IBM MQ sender channel + parameters = Bhavesh's I2017_..._IBMMQtoSOAP.jar (L1, source/)
  ProcessDirect receiver channel ("IDoc to SAP") = reference I2052_..._PDToIDoc (L1, _reference/iflows)

Usage:  py -I tools/iflow_build_tibnor_inbound.py --flow ORDRSP|DESADV|INVOIC
                                                  [--only parent|HameenlinnaMetocs|HameenlinnaTilkku|RaaheTilkku]
"""
import copy
import os
import re
import sys
import zipfile

sys.stdout.reconfigure(encoding="utf-8")
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import iflow_lib  # noqa: E402
from iflow_lib import NS, _q  # noqa: E402
import iflow_build_smarteam as st  # noqa: E402
import iflow_build_tibnor as tb  # noqa: E402  (sets st.PKG to the Tibnor package folder)

REPO, PKG, RES = st.REPO, tb.PKG, tb.RES
NUMBER = tb.NUMBER                                    # interface number, not decided yet
QUEUE = f"{NUMBER}_TibnorS4"                          # new dispatcher queue for Tibnor S4 (user, 2026-11-24)
MQ_SYSTEM, IDOC_SYSTEM = "FinMessageHub", "TibnorS4"
IDOC_ENDPOINT = "/T0143_P_IDocReceiver_TibnorS4_PDToIDoc"   # shared IDoc flow (user, 2026-11-24)
APP_ID = "CH_FinMessageHubApplicationId"             # user, 2026-11-24 (not CH_ApplicationId: confusable)
SOURCE_SYSTEM = "CH_FinMessageHubSourceSystem"
MAPPINGS = os.path.join(REPO, "mappings")

# DESADV / INVOIC routing, as the user's PO conditions (2026-11-24):
#   receiver: recipient GLN in this list; interface: SourceSystem METOCS* -> Metocs, else Tilkku.
#   Tilkku is split by the mill GLN (InterchangeSender), the value the Tilkku mappings check (user, 2026-11-24).
RECIPIENTS = "7340195700006,7080003309006,5790002585623,003723894430"
METOCS = 'sourceSystem.startsWith("METOCS")'
RAAHE, HAMEENLINNA = 'sender == "00372389445741"', 'sender == "00372389445751"'

# ns: iFlow Namespace Mapping xmlns:p1=<ns> (Runtime Configuration). Works in CPI (L2, user 2026-11-24).
# Prefix p1 as in the user's PO conditions.
# rows: XPath properties in both parent and child (logged as custom headers); route_rows: parent only.
FLOWS = {
    "ORDRSP": dict(
        object="OrderResponse", ns="http://www.ruukki.com/schemas/eai/internal/production/eruukki",
        root="/p1:OrdrspInterchange/p1:OrderResponseMessage", app_id="/p1:DocumentId/p1:DocumentNo",
        rows=[(APP_ID, "/p1:Header/p1:ApplicationId"),
              ("CH_PurchaseOrder", "/p1:Reference[@Type=&apos;CO&apos;]/p1:RefNo")],
        route_rows=[], guard=False,
        children={   # mill: (mapping folder, mapping name, receiver rule for the Groovy script)
            "HameenlinnaMetocs": ("2_ORDRSP_HameenlinnaMetocs-to-Tibnor",
                                  "Map_HammelinnaMetocsHub_TibnorS4_OrderConfirmation_ORDRSP",
                                  'appId.startsWith("METOCS")'),
            "HameenlinnaTilkku": ("11_ORDRSP_HameenlinnaTilkku-to-Tibnor",
                                  "Map_HammelinnaTilkkuHub_TibnorS4_OrderConfirmation_ORDRSP", 'appId == "TILKKUHA"'),
            "RaaheTilkku": ("7_ORDRSP_RaaheTilkku-to-Tibnor",
                            "Map_RaaheTilkkuHub_TibnorS4_OrderConfirmation_ORDRSP", 'appId == "TILKKURA"')}),
    "DESADV": dict(
        object="DespatchAdvice", ns="http://www.ruukki.com/schemas/eai/rucomef/otc",
        root="/p1:DeliveryBatch", app_id="/p1:DeliveryBatchId",
        rows=[(SOURCE_SYSTEM, "/p1:SourceSystem"),
              ("CH_PurchaseOrder", "/p1:Reference[p1:ReferenceType=&apos;BuyersOrderId&apos;][1]/p1:ReferenceId")],
        route_rows=[("FinMessageHubSender", "/p1:Header/p1:InterchangeSender"),
                    ("FinMessageHubRecipient", "/p1:Header/p1:InterchangeRecipient")], guard=True,
        children={
            "HameenlinnaMetocs": ("3_Tibnor SSABEuropeHameenlinnaMetocs [80008] EDI DESADV in",
                                  "Map_HammelinnaMetocsHub_TibnorS4_DeliveryNotice_DESADV", METOCS),
            "HameenlinnaTilkku": ("12_DESADV_HameenlinnaTilkku-to-Tibnor",
                                  "Map_HammelinnaTilkkuHub_TibnorS4_DeliveryNotice_DESADV", HAMEENLINNA),
            "RaaheTilkku": ("8_DESADV_RaaheTilkku-to-Tibnor",
                            "Map_RaaheTilkkuHub_TibnorS4_DeliveryNotice_DESADV", RAAHE)}),
    "INVOIC": dict(
        object="Invoice", ns=None,                    # <Invoice> has no namespace: no Namespace Mapping
        root="/Invoice", app_id="/DocumentId/DocumentNo",
        rows=[(SOURCE_SYSTEM, "/Header/SourceSystem"),
              ("CH_PurchaseOrder", "/Reference[@Type=&apos;ON&apos;][1]/ReferenceIdentification")],
        route_rows=[("FinMessageHubSender", "/Header/InterchangeSender"),
                    ("FinMessageHubRecipient", "/Header/RecipientIdentification")], guard=True,
        children={
            "HameenlinnaMetocs": ("4_Tibnor SSABEuropeHameenlinnaMetocs [80008] EDI INVOIC in",
                                  "Map_HammelinnaMetocsHub_TibnorS4_Invoice_INVOIC", METOCS),
            "HameenlinnaTilkku": ("13_INVOIC_HameenlinnaTilkku-to-Tibnor",
                                  "Map_HammelinnaTilkkuHub_TibnorS4_Invoice_INVOIC", HAMEENLINNA),
            "RaaheTilkku": ("9_INVOIC_RaaheTilkku-to-Tibnor",
                            "Map_RaaheTilkkuHub_TibnorS4_Invoice_INVOIC", RAAHE)}),
}
VERSIONS = {"ORDRSP": "1.0.0", "DESADV": "1.0.0", "INVOIC": "1.0.0"}


def parent_name(mt: str) -> str:
    return f"{NUMBER}_P_{FLOWS[mt]['object']}_FinMessageHub_MQToJMS"


def child_name(mt: str, mill: str) -> str:
    return f"{NUMBER}_{FLOWS[mt]['object']}_FinMessageHub_{mill}_TibnorS4_JMSToIDoc"


VERSION = {}
for _mt, _cfg in FLOWS.items():
    VERSION[parent_name(_mt)] = VERSIONS[_mt]
    VERSION.update({child_name(_mt, m): VERSIONS[_mt] for m in _cfg["children"]})

I2017 = "I2017_PurchaseOrder_SalesOrderBulkRequest_TILKKU_MSAP_IBMMQtoSOAP"
I2052 = "I2052_DocumentInfoRecord_Update_DOCMAS05_CLFMAS02_SmarTeam_MSAP_PDToIDoc"
FORBIDDEN = ["SmarTeam", "StreamServe", "I2017", "I2018", "I2023", "I2034", "I2052", "SalesOrder", "AURORA",
             "PurchaseOrder_ORDERS", "HubEnvironment", "Enviroinment"]

# IBM MQ sender parameters of I2017 -> our names (fix the names with brackets and spaces; LocationID gets the
# IBMMQ_ prefix; 'delay' is "Polling Interval (in ms)" in the propdef)
MQ_RENAMES = {"IBMMQ_CharacterSetID(CCSID)forNonASCIINames": "IBMMQ_CCSID",
              "IBMMQ_ConnectionCheckInterval(in ms)": "IBMMQ_PollingInterval",
              "LocationID": "IBMMQ_LocationID",
              "IBMMQ_SSLCipherSuite": "IBMMQ_SSL_Cipher_Suite",          # same names as the ORDERS MQ receiver
              "IBMMQ_QueueManagerName": "IBMMQ_Queue_ManagerName",
              "IBMMQ_TransactionalJMSSession": "IBMMQ_Transactional_JMS_Session"}
MQ_EMPTY = {"IBMMQ_QueueName", "IBMMQ_DLQueueName"}   # set on the tenant (queue names not known yet)
MQ_EXTRA = [("IBMMQ_InitialDelay", "initialDelay", "Initial Delay (in ms)"),
            ("IBMMQ_TransactionFailedHandling", "transactionFailedHandling", "Transaction Failed Handling"),
            ("IBMMQ_TargetClient", "targetClient", "Target Client")]


def prop_unescape(k: str) -> str:
    return re.sub(r"\\(.)", r"\1", k)


def set_namespace_mapping(xml: str, ns) -> str:
    if not ns:
        return xml
    root = iflow_lib.parse(xml)
    coll = root.find(".//bpmn2:collaboration", NS)
    v = iflow_lib.get_prop(root, coll, "namespaceMapping")
    assert not (v.text or ""), v.text
    v.text = f"xmlns:p1={ns}"
    return iflow_lib.serialize(root)


def swap_channel(xml: str, old_name: str, new_name: str, src_xml: str, src_name: str, system: str) -> str:
    """Replace the settings of channel old_name with those of channel src_name in src_xml (copied unchanged)."""
    root = iflow_lib.parse(xml)
    mf = iflow_lib._owner(root, old_name, "messageFlow")
    sroot = iflow_lib.parse(src_xml)
    src = (st.by_id(sroot, src_name) if src_name.startswith("MessageFlow_")
           else iflow_lib._owner(sroot, src_name, "messageFlow"))
    mf.remove(mf.find("bpmn2:extensionElements", NS))
    mf.insert(0, copy.deepcopy(src.find("bpmn2:extensionElements", NS)))
    mf.set("name", new_name)
    iflow_lib.get_prop(root, mf, "system").text = system
    return iflow_lib.serialize(root)


def smi_id(xml: str) -> str:
    """The Set Monitoring Identifiers step that carries the monitoring headers."""
    root = iflow_lib.parse(xml)
    return [e for e in root.iter(_q("bpmn2:callActivity")) if e.get("name") == "Set Monitoring Identifiers"
            and "SAP_Sender" in (iflow_lib.get_prop(root, e, "headerTable").text or "")][0].get("id")


def xpath_rows(cfg, key="rows"):
    return [tb.row("xpath", n, cfg["root"] + x, "java.lang.String") for n, x in cfg[key]]


def rename_participant_plain(xml: str, old: str, new: str) -> str:
    return st.replace_counted(xml, [(f'name="{old}"', f'name="{new}"', 1)])


# ---------------------------------------------------------------------------
# Parent
# ---------------------------------------------------------------------------

def rd_groovy(mt: str) -> str:
    cfg = FLOWS[mt]
    ind = "        " if cfg["guard"] else "    "
    rules = "\n".join(
        f'{ind}{"if" if i == 0 else "else if"} ({rule}) {{\n'
        f'{ind}    arr_receiversQueueList.add("{QUEUE}")\n'
        f'{ind}    arr_receiversIFlowList.add("{child_name(mt, mill)}")\n'
        f'{ind}}}' for i, (mill, (_, _, rule)) in enumerate(cfg["children"].items()))
    get = '(message.getProperty("%s") ?: "").toString().trim()'
    if not cfg["guard"]:
        doc = f""" * The mill comes from Header/ApplicationId, read by XPath into property {APP_ID} in
 * "Set Monitoring Identifiers": no payload parsing here (user, 2026-11-24).
 *   METOCS*  -> Hameenlinna Metocs, TILKKUHA -> Hameenlinna Tilkku, TILKKURA -> Raahe Tilkku"""
        body = f"""    def appId = {get % APP_ID}

{rules}"""
    else:
        doc = """ * All values are read by XPath in "Set Monitoring Identifiers": no payload parsing here (user, 2026-11-24).
 * As the PO conditions (user, 2026-11-24): only for a recipient GLN in property AllowedRecipients, then
 *   SourceSystem METOCS*  -> Hameenlinna Metocs
 *   else by mill GLN (InterchangeSender): 00372389445751 -> Hameenlinna Tilkku, 00372389445741 -> Raahe Tilkku"""
        body = f"""    def sourceSystem = {get % SOURCE_SYSTEM}
    def sender = {get % "FinMessageHubSender"}
    def recipient = {get % "FinMessageHubRecipient"}
    def allowedRecipients = {get % "AllowedRecipients"}.split(",")*.trim()

    if (allowedRecipients.contains(recipient)) {{
{rules}
    }}"""
    return f"""import com.sap.gateway.ip.core.customdev.util.Message

/*
 * Receiver determination for {parent_name(mt)}
{doc}
 * No receiver found: the lists stay empty, arr_receiversLastIndex = -1 and the
 * "Receivers Exist?" router sends the message to the Error End.
 */
def Message processData(Message message) {{

    def arr_receiversQueueList = []
    def arr_receiversIFlowList = []

{body}

    message.setProperty("arr_receiversQueueList", arr_receiversQueueList)
    message.setProperty("arr_receiversIFlowList", arr_receiversIFlowList)
    message.setProperty("arr_receiversLastIndex", arr_receiversQueueList.size() - 1)

    return message
}}
"""


def mq_sender_params(xml: str, p, src_prop: str, src_def: str) -> str:
    """Rename the I2017 placeholders in the channel and copy values, types and references."""
    for old, new in MQ_RENAMES.items():
        xml = st.replace_counted(xml, [("{{%s}}" % old, "{{%s}}" % new, 1)])
    used = sorted(set(re.findall(r"\{\{((?:IBMMQ_)[^}]+)\}\}", xml)))
    back = {v: k for k, v in MQ_RENAMES.items()}
    lines = {prop_unescape(m.group(1)): m.group(2)
             for m in re.finditer(r"^([^#!\s](?:\\.|[^=:\\])*)=(.*)$", src_prop, re.M)}
    for new in used:
        old = back.get(new, new)
        p.set(new, "" if new in MQ_EMPTY else lines[old])
        blk = re.search(r"<parameter>\s*<key/>\s*<name>" + re.escape(old) + r"</name>.*?</parameter>", src_def, re.S)
        p.propdef = p.propdef.replace("<param_references>",
                                      blk.group(0).replace(f"<name>{old}</name>", f"<name>{new}</name>")
                                      + "<param_references>", 1)
        ref = re.search(r'<reference [^>]*param_key="' + re.escape(old) + r'"/>', src_def).group(0)
        ref = ref.replace(f'param_key="{old}"', f'param_key="{new}"').replace(
            'attribute_category="TILKKU"', f'attribute_category="{MQ_SYSTEM}"')
        p.propdef = p.propdef.replace("</param_references>", ref + "</param_references>", 1)
    variant = re.search(r'attribute_id="(ctype::Adapter/cname::IBMMQ/[^"]*?)/attrId::', src_def).group(1)
    for param, key, label in MQ_EXTRA:
        cur = re.search(r"<key>%s</key>\s*<value>([^<]*)</value>" % key, xml).group(1)
        xml = iflow_lib.externalize(xml, "IBMMQ", key, "{{%s}}" % param, expect=cur)
        p.add(param, cur, ref=(MQ_SYSTEM, variant + "/attrId::" + key, label))
    print(f"  IBM MQ sender: {len(used)} parameters from I2017 + {len(MQ_EXTRA)} externalized here")
    return xml


def build_parent(mt: str) -> str:
    cfg, name = FLOWS[mt], parent_name(mt)
    files = tb.template("Tibnor_SSAB_EDIMigration", tb.PARENT)
    xml = tb.iflw_of(files)
    tb.set_identity(files, name)
    files[RES + "script/ReceiverDetermination.groovy"] = rd_groovy(mt).encode("utf-8")
    src = zipfile.ZipFile(os.path.join(tb.SOURCE, I2017 + ".jar"))
    src_xml = [src.read(n).decode("utf-8") for n in src.namelist() if n.endswith(".iflw")][0]
    p = iflow_lib.Params(files[RES + "parameters.prop"].decode("utf-8"),
                         files[RES + "parameters.propdef"].decode("utf-8"))
    # ProcessDirect sender -> IBM MQ sender (I2017 settings), participant FinMessageHub
    xml = swap_channel(xml, "ProcessDirect", "IBMMQ", src_xml, "IBMMQ", MQ_SYSTEM)
    xml = rename_participant_plain(xml, tb.SENDER, MQ_SYSTEM)
    xml = mq_sender_params(xml, p, src.read(RES + "parameters.prop").decode("utf-8"),
                           src.read(RES + "parameters.propdef").decode("utf-8"))
    xml = set_namespace_mapping(xml, cfg["ns"])
    # monitoring: hub message keys instead of the IDoc ones
    sid = smi_id(xml)
    add = xpath_rows(cfg) + xpath_rows(cfg, "route_rows")
    if cfg["guard"]:
        add.append(tb.row("constant", "AllowedRecipients", "{{FinMessageHub_AllowedRecipients}}"))
        p.add("FinMessageHub_AllowedRecipients", RECIPIENTS)
    xml = tb.edit_table(xml, sid, "propertyTable", drop=("CH_IdocNumber", "CH_PurchaseOrder", "RCVPRN"), add=add)
    xml = tb.edit_table(xml, sid, "headerTable", xpaths={"SAP_ApplicationID": cfg["root"] + cfg["app_id"]})
    p.set("HTTPS_Address", "/" + name)
    p.set("SAP_Sender", MQ_SYSTEM)
    p.set("SAP_MessageType", mt)
    st.remove_unused(xml, p)
    return st.finish(name, files, xml, p, VERSION[name], FORBIDDEN, rename=False)


# ---------------------------------------------------------------------------
# Children
# ---------------------------------------------------------------------------

def build_child(mt: str, mill: str) -> str:
    cfg = FLOWS[mt]
    folder, mapping, _ = cfg["children"][mill]
    name = child_name(mt, mill)
    files = tb.template("Tibnor_SSAB_EDIMigration", tb.CHILD)
    xml = tb.iflw_of(files)
    files = {n: b for n, b in files.items()
             if not n.endswith(".iflw") and not n.startswith(tuple(RES + d for d in ("mapping/", "script/", "xsd/")))}
    tb.set_identity(files, name)
    mz = zipfile.ZipFile(os.path.join(MAPPINGS, folder, "build", mapping + ".zip"))
    for n in mz.namelist():
        files[RES + n] = mz.read(n)
    ref = zipfile.ZipFile(os.path.join(tb.SOURCE, I2052 + ".zip"))
    ref_xml = [ref.read(n).decode("utf-8") for n in ref.namelist() if n.endswith(".iflw")][0]
    ref_def = ref.read(RES + "parameters.propdef").decode("utf-8")
    p = iflow_lib.Params(files[RES + "parameters.prop"].decode("utf-8"),
                         files[RES + "parameters.propdef"].decode("utf-8"))

    # IBM MQ receiver -> ProcessDirect receiver to the shared IDoc flow (I2052 "IDoc to SAP" settings)
    # I2052 has a ProcessDirect sender and receiver of the same name: take the receiver ("Send IDoc to MSAP")
    xml = swap_channel(xml, "IBMMQ", "ProcessDirect", ref_xml, "MessageFlow_22285626", IDOC_SYSTEM)
    xml = st.replace_counted(xml, [("{{MSAP_IDocEndpoint}}", "{{TibnorS4_IDocEndpoint}}", 1),
                                   ('name="Send To MQ"', 'name="Send To TibnorS4"', 1)])
    aid = re.search(r'attribute_id="([^"]*)"[^>]*param_key="MSAP_IDocEndpoint"', ref_def).group(1)
    p.add("TibnorS4_IDocEndpoint", IDOC_ENDPOINT, ref=(IDOC_SYSTEM, aid, "Address"))
    # participants: sender TibnorS4 -> FinMessageHub, receiver FinMessageHub -> TibnorS4
    xml = rename_participant_plain(xml, tb.SENDER, "__SENDER__")
    xml = rename_participant_plain(xml, MQ_SYSTEM, IDOC_SYSTEM)
    xml = rename_participant_plain(xml, "__SENDER__", MQ_SYSTEM)
    p.propdef = (p.propdef.replace(f'attribute_category="{tb.SENDER}"', 'attribute_category="__S__"')
                 .replace(f'attribute_category="{MQ_SYSTEM}"', f'attribute_category="{IDOC_SYSTEM}"')
                 .replace('attribute_category="__S__"', f'attribute_category="{MQ_SYSTEM}"'))
    # mapping step -> the mill's mapping
    root = iflow_lib.parse(xml)
    m = st.by_id(root, tb.MAP_STEP)
    m.set("name", mapping)
    for key, val in (("mappinguri", f"dir://mmap/src/main/resources/mapping/{mapping}.mmap"),
                     ("mappingname", mapping), ("mappingpath", f"src/main/resources/mapping/{mapping}")):
        iflow_lib.get_prop(root, m, key).text = val
    xml = iflow_lib.serialize(root)
    xml = set_namespace_mapping(xml, cfg["ns"])
    # monitoring + IDoc control values read by the mapping (getProperty SNDPOR / RCVPOR / RCVPRN)
    xml = tb.edit_table(xml, tb.SMI_CHILD, "propertyTable",
                        drop=("CH_IdocNumber", "CH_PurchaseOrder", "HubEnvironment"),
                        add=xpath_rows(cfg) + [tb.row("constant", k, "{{TibnorS4_%s}}" % k)
                                               for k in ("SNDPOR", "RCVPOR", "RCVPRN")])
    xml = tb.edit_table(xml, tb.SMI_CHILD, "headerTable", xpaths={"SAP_ApplicationID": cfg["root"] + cfg["app_id"]})
    for k in ("SNDPOR", "RCVPOR", "RCVPRN"):
        p.add(f"TibnorS4_{k}", "")                     # set on the tenant (user, 2026-11-24)
    p.set("PD_Address", "/" + name)
    p.set("HTTPS_Address", "/" + name)
    p.set("SAP_Sender", MQ_SYSTEM)
    p.set("SAP_Receiver", IDOC_SYSTEM)
    p.set("SAP_MessageType", mt)
    st.remove_unused(xml, p)
    return st.finish(name, files, xml, p, VERSION[name], FORBIDDEN, rename=True)


st.KNOWN_PARTICIPANTS |= {MQ_SYSTEM, IDOC_SYSTEM}


def main():
    mt = sys.argv[sys.argv.index("--flow") + 1]
    only = sys.argv[sys.argv.index("--only") + 1] if "--only" in sys.argv else None
    jobs = [(m, lambda m=m: build_child(mt, m)) for m in FLOWS[mt]["children"]] + [("parent", lambda: build_parent(mt))]
    for key, fn in jobs:
        if only in (None, key):
            print(f"== {mt} {key}")
            name = fn()
            z = st.read_archive(tb.LONG + os.path.join(PKG, name, "build", name + ".zip"))[0]
            for fl in iflow_lib.best_practice_flags(tb.iflw_of(z), z[RES + "parameters.prop"].decode("utf-8")):
                print("  FLAG:", fl)


if __name__ == "__main__":
    main()
