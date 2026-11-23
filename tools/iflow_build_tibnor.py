"""
tools/iflow_build_tibnor.py
Build the Tibnor ORDERS iFlows (CPI package Tibnor_SSAB_EDIMigration, repo folder
iflows/Tibnor_SSAB_EDIMigration/).

  parent  IXXXX_P_PurchaseOrder_ORDERS_ORDERS02_TibnorS4_IDocToJMS
          ProcessDirect (+ Manual Retrigger) -> receiver determination on EDI_DC40/RCVPRN
          -> JMS queue I0707_FinMessageHub (dispatcher I0707, already on the tenant)
  child   IXXXX_PurchaseOrder_ORDERS_ORDERS02_TibnorS4_FinMessageHub_HameenlinnaMetocs_JMSToMQ
          ProcessDirect from the dispatcher -> Map_TibnorS4_HammelinnaMetocsHub_PurchaseOrder_ORDERS02
          -> IBM MQ receiver

Templates (no XML structure invented, CLAUDE.md):
  parent = our build of I2023_P_..._IDocToJMS 1.0.14 (L3, same IDoc-parent shape)
  child  = our build of I2018_Material_MSAP_SmarTeam_JMSToHTTP 1.1.5 (L3, simplest dispatcher child)
  IBM MQ receiver channel, its parameters and propdef = Bhavesh's export
           I2034_Pickinglist_..._StreamServe_JMSToIBMMQ 1.0.10 (L1, source/)
  mapping = mappings/1_ORDERS_Tibnor-to-HameenlinnaMetocs/build/<mapping>.zip

Usage:
  py -I tools/iflow_build_tibnor.py            (both)
  py -I tools/iflow_build_tibnor.py --only parent|child
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

REPO = st.REPO
PKG = os.path.join(REPO, "iflows", "Tibnor_SSAB_EDIMigration")
SOURCE = os.path.join(PKG, "source")
st.PKG = PKG          # check_and_write writes to <PKG>/<name>/build
LONG = "\\\\?\\"      # SmarTeam names give paths over 260 characters

# The interface number is not decided yet (user, 2026-11-23). Change it here only.
NUMBER = "IXXXX"
PARENT = f"{NUMBER}_P_PurchaseOrder_ORDERS_ORDERS02_TibnorS4_IDocToJMS"
CHILD = f"{NUMBER}_PurchaseOrder_ORDERS_ORDERS02_TibnorS4_FinMessageHub_HameenlinnaMetocs_JMSToMQ"
QUEUE = "I0707_FinMessageHub"            # dispatcher queue (user, 2026-11-23; dispatcher exists)
RCVPRN = "25200"                         # receiver partner, leading zeros ignored (user, 2026-11-23)
SENDER = "TibnorS4"                      # SAP_Sender, both flows (user, 2026-11-23)
RECEIVER = "FinMessageHub_HameenlinnaMetocs"   # SAP_Receiver, child only (user, 2026-11-23)
MQ_SYSTEM = "FinMessageHub"              # receiver participant: plain system name
MESSAGE_TYPE = "ORDERS.ORDERS02"
MAPPING = "Map_TibnorS4_HammelinnaMetocsHub_PurchaseOrder_ORDERS02"
VERSION = {PARENT: "1.0.1", CHILD: "1.0.0"}

I2023_P = "I2023_P_Equipment_COD_EQUIPMENT_SAVE_COD_EQUIPMENT_SAVE01_MSAP_IDocToJMS"
I2018 = "I2018_Material_MSAP_SmarTeam_JMSToHTTP"
I2034 = "I2034_Pickinglist_SCWM_WMTORD_SCWM_WMTOID01_MSAP_StreamServe_JMSToIBMMQ"
MAP_ZIP = os.path.join(REPO, "mappings", "1_ORDERS_Tibnor-to-HameenlinnaMetocs", "build", MAPPING + ".zip")
RES = "src/main/resources/"
FORBIDDEN = ["SmarTeam", "I2018", "I2023", "I2034", "StreamServe", "Pickinglist", "Equipment",
             "Enviroinment", "COD_EQUIPMENT"]


def template(pkg_folder: str, name: str) -> dict[str, bytes]:
    path = LONG + os.path.join(REPO, "iflows", pkg_folder, name, "build", name + ".zip")
    return st.read_archive(path)[0]


def iflw_of(files) -> str:
    return [b for n, b in files.items() if n.endswith(".iflw")][0].decode("utf-8")


def set_identity(files: dict, name: str) -> None:
    """MANIFEST bundle names and .project name = the new iFlow name."""
    files["META-INF/MANIFEST.MF"] = st.mf_set(files["META-INF/MANIFEST.MF"], {
        k: name for k in ("Bundle-Name", "Bundle-SymbolicName", "Origin-Bundle-Name", "Origin-Bundle-SymbolicName")})
    files[".project"] = re.sub(rb"<name>[^<]*</name>", b"<name>" + name.encode() + b"</name>",
                               files[".project"], count=1)


def row(type_: str, name: str, value: str, datatype: str = "") -> str:
    """One Content Modifier row as it sits in the (once unescaped) table text."""
    return (f"<row><cell id='Action'>Create</cell><cell id='Type'>{type_}</cell><cell id='Value'>{value}</cell>"
            f"<cell id='Default'></cell><cell id='Name'>{name}</cell><cell id='Datatype'>{datatype}</cell></row>")


def edit_table(xml: str, step_id: str, table: str, drop=(), add=(), xpaths=None) -> str:
    """Drop rows by Name, set xpath Values by Name, append rows."""
    root = iflow_lib.parse(xml)
    v = iflow_lib.get_prop(root, st.by_id(root, step_id), table)
    rows = re.findall(r"<row>.*?</row>", v.text or "")
    keep = []
    for r in rows:
        n = re.search(r"<cell id='Name'>(.*?)</cell>", r).group(1)
        if n in drop:
            continue
        if xpaths and n in xpaths:
            r = re.sub(r"<cell id='Value'>.*?</cell>", lambda m: f"<cell id='Value'>{xpaths[n]}</cell>", r)
        keep.append(r)
    missing = set(drop) - {re.search(r"<cell id='Name'>(.*?)</cell>", r).group(1) for r in rows}
    assert not missing, f"{step_id}/{table}: rows not found {missing}"
    v.text = "".join(keep) + "".join(add)
    return iflow_lib.serialize(root)


# ---------------------------------------------------------------------------
# Parent
# ---------------------------------------------------------------------------

RD_GROOVY = f"""import com.sap.gateway.ip.core.customdev.util.Message

/*
 * Receiver determination for {PARENT}
 * Reads EDI_DC40/RCVPRN of the ORDERS02 IDoc.
 * RCVPRN can be a partner number (0000025200) or a logical system / alphanumeric name
 * (e.g. TS4CLNT100): leading zeros are removed only when the value is all digits
 * (0000025200 = 25200); any other value is compared as it is (trimmed).
 * No receiver found: the lists stay empty, arr_receiversLastIndex = -1 and the
 * "Receivers Exist?" router sends the message to the Error End.
 */
def Message processData(Message message) {{

    def arr_receiversQueueList = []
    def arr_receiversIFlowList = []

    // Stream the body into the parser (no copy of the payload as a String)
    def idoc = new XmlSlurper().parse(message.getBody(java.io.Reader))
    def rcvprn = idoc.IDOC.EDI_DC40.RCVPRN.text().trim()
    if (rcvprn ==~ /\\d+/) {{
        rcvprn = rcvprn.replaceFirst(/^0+(?!$)/, '')
    }}

    if (rcvprn == "{RCVPRN}") {{
        arr_receiversQueueList.add("{QUEUE}")
        arr_receiversIFlowList.add("{CHILD}")
    }}

    message.setProperty("arr_receiversQueueList", arr_receiversQueueList)
    message.setProperty("arr_receiversIFlowList", arr_receiversIFlowList)
    message.setProperty("arr_receiversLastIndex", arr_receiversQueueList.size() - 1)

    return message
}}
"""


def build_parent() -> str:
    name = PARENT
    files = template("SmarTeam", I2023_P)
    xml = iflw_of(files)
    set_identity(files, name)
    files[RES + "script/ReceiverDetermination.groovy"] = RD_GROOVY.encode("utf-8")
    p = iflow_lib.Params(files[RES + "parameters.prop"].decode("utf-8"),
                         files[RES + "parameters.propdef"].decode("utf-8"))
    # Misspelt parameter and property name of the template (CLAUDE.md: fix misspelt names)
    xml = st.replace_counted(xml, [("{{Enviroinment}}", "{{Environment}}", 1),
                                   ("&lt;cell id='Name'&gt;Enviroinment&lt;", "&lt;cell id='Name'&gt;Environment&lt;", 1)])
    p.rename("Enviroinment", "Environment")
    p.set("ProcessDirect_Address", "/" + name)
    p.set("HTTPS_Address", "/" + name)
    p.set("SAP_Sender", SENDER)
    p.set("SAP_MessageType", MESSAGE_TYPE)
    # Searchable PO number next to the IDoc number (plain path, sample + ORDERS.ORDERS02.xsd)
    root = iflow_lib.parse(xml)
    smi = [e for e in root.iter(_q("bpmn2:callActivity")) if e.get("name") == "Set Monitoring Identifiers"
           and "SAP_Sender" in (iflow_lib.get_prop(root, e, "headerTable").text or "")][0].get("id")
    xml = edit_table(xml, smi, "propertyTable",
                     add=[row("xpath", "CH_PurchaseOrder", "/ORDERS02/IDOC/E1EDK01/BELNR", "java.lang.String")])
    xml = st.rename_participant(xml, p, "MSAP", SENDER)      # ProcessDirect sender = sending system
    st.remove_unused(xml, p)
    files[RES + "parameters.prop"] = p.prop.encode("utf-8")
    return st.finish(name, files, xml, p, VERSION[name], FORBIDDEN, rename=False)


# ---------------------------------------------------------------------------
# Child
# ---------------------------------------------------------------------------

SEND = "ServiceTask_734107"         # I2018 "Send to SmarTeam"
AFTER_SEND = ["CallActivity_734112", "I2018_CA_LogCustomHeaders", "CallActivity_734113"]   # response steps
AFTER_FLOWS = ["I2018_SF_toLogCH", "SequenceFlow_734114", "SequenceFlow_734115"]
SEND_TO_END = "SequenceFlow_734108"  # Send -> (was Set AttachmentName) -> now End
END = "EndEvent_30"
SMI_CHILD = "CallActivity_734026"
MAP_STEP = "CallActivity_734093"

# IBM MQ settings that are fixed in I2034 but someone may tune: externalized here (CLAUDE.md, all adapters).
# (param, key, label). `entity` (queue/topic) and `connectionProtocol` (tcpip) define the channel, not tuned.
MQ_EXTRA = [("IBMMQ_MessageType", "messageType", "Message Type"),
            ("IBMMQ_MessagePersistence", "messagePersistence", "Message Persistence"),
            ("IBMMQ_TargetClient", "targetClient", "Target Client")]
MQ_TECHNICAL = {"entity", "connectionProtocol"}


def mq_channel(i2034_xml: str):
    root = iflow_lib.parse(i2034_xml)
    return iflow_lib._owner(root, "IBMMQ", "messageFlow")


def build_child() -> str:
    name = CHILD
    files = template("SmarTeam", I2018)
    xml = iflw_of(files)
    files = {n: b for n, b in files.items()
             if not n.endswith(".iflw") and not n.startswith(tuple(RES + d for d in ("mapping/", "script/", "wsdl/", "xsd/")))}
    set_identity(files, name)
    # Mapping, its UDFs and schemas, as built (standalone layout -> src/main/resources/<folder>/)
    mz = zipfile.ZipFile(MAP_ZIP)
    for n in mz.namelist():
        files[RES + n] = mz.read(n)
    src = zipfile.ZipFile(os.path.join(SOURCE, I2034 + ".zip"))
    i2034 = {n: src.read(n) for n in src.namelist()}
    i2034_xml = [b for n, b in i2034.items() if n.endswith(".iflw")][0].decode("utf-8")

    p = iflow_lib.Params(files[RES + "parameters.prop"].decode("utf-8"),
                         files[RES + "parameters.propdef"].decode("utf-8"))

    # 1. HTTP receiver -> IBM MQ receiver: channel settings copied unchanged from I2034
    root = iflow_lib.parse(xml)
    http = iflow_lib._owner(root, "HTTP", "messageFlow")
    mq = mq_channel(i2034_xml)
    http.remove(http.find("bpmn2:extensionElements", NS))
    http.insert(0, copy.deepcopy(mq.find("bpmn2:extensionElements", NS)))
    http.set("name", "IBMMQ")
    sysv = iflow_lib.get_prop(root, http, "system")
    assert sysv.text == "StreamServe", sysv.text
    sysv.text = MQ_SYSTEM
    st.by_id(root, SEND).set("name", "Send To MQ")
    # 2. No response from MQ: drop the SmarTeam response steps, Send -> End
    proc = st.by_id(root, SEND).getparent()
    plane = root.find(".//bpmndi:BPMNPlane", NS)
    shapes = {s.get("bpmnElement"): s for s in plane.findall("bpmndi:BPMNShape", NS)}
    ax, ay, aw, ah = iflow_lib._bounds(shapes[AFTER_SEND[0]])
    for i in AFTER_SEND + AFTER_FLOWS:
        e = st.by_id(root, i)
        e.getparent().remove(e)
    f = st.by_id(root, SEND_TO_END)
    f.set("targetRef", END)
    assert f.getparent() is proc
    # 3. Mapping step -> our mapping
    m = st.by_id(root, MAP_STEP)
    m.set("name", MAPPING)
    for key, val in (("mappinguri", f"dir://mmap/src/main/resources/mapping/{MAPPING}.mmap"),
                     ("mappingname", MAPPING), ("mappingpath", f"src/main/resources/mapping/{MAPPING}")):
        iflow_lib.get_prop(root, m, key).text = val
    xml = iflow_lib.serialize(root)
    xml, _ = iflow_lib.sync_flow_refs(xml)
    # End event where the first response step was; the pool ends 60 px after it
    root = iflow_lib.parse(xml)
    pool = [pt for pt in root.iter(_q("bpmn2:participant")) if pt.get("name") == "Main Process"][0].get("id")
    px, py, _, ph = iflow_lib._bounds(root.find(f".//bpmndi:BPMNShape[@bpmnElement='{pool}']", NS))
    end_x = ax + 30
    xml, _ = iflow_lib.fix_diagram(xml, bounds={END: (end_x, ay + ah / 2 - 16, 32, 32),
                                                pool: (px, py, end_x + 32 + 60 - px, ph)})

    # 4. Set Monitoring Identifiers: IDoc keys instead of the material ones, HubEnvironment for the mapping
    docnum = "format-number(/ORDERS02/IDOC/EDI_DC40/DOCNUM,&apos;#&apos;)"
    xml = edit_table(xml, SMI_CHILD, "propertyTable", drop=("CH_Material", "CH_MaterialType"), add=[
        row("xpath", "CH_IdocNumber", docnum, "java.lang.String"),
        row("xpath", "CH_PurchaseOrder", "/ORDERS02/IDOC/E1EDK01/BELNR", "java.lang.String"),
        row("constant", "HubEnvironment", "{{HubEnvironment}}")])
    xml = edit_table(xml, SMI_CHILD, "headerTable", xpaths={"SAP_ApplicationID": docnum})

    # 5. Parameters
    for k in [k for k in p.keys() if k.startswith("SmarTeam_")]:
        p.remove(k)
    p.set("PD_Address", "/" + name)
    p.set("HTTPS_Address", "/" + name)
    p.set("SAP_Sender", SENDER)
    p.set("SAP_Receiver", RECEIVER)
    p.set("SAP_MessageType", MESSAGE_TYPE)
    p.add("HubEnvironment", "TST")
    # IBM MQ parameters: values, types and references as in I2034; category = our participant
    i_prop = i2034[RES + "parameters.prop"].decode("utf-8")
    i_def = i2034[RES + "parameters.propdef"].decode("utf-8")
    used = sorted(set(re.findall(r"\{\{(IBMMQ_[^}]+)\}\}", xml)))
    for k in used:
        line = re.search(r"^" + re.escape(k) + r"=(.*)$", i_prop, re.M)
        value = "" if k == "IBMMQ_QueueName" else line.group(1)   # queue: set on the tenant (user, 2026-11-23)
        p.set(k, value)
        blk = re.search(r"<parameter>\s*<key/>\s*<name>" + re.escape(k) + r"</name>.*?</parameter>", i_def, re.S)
        p.propdef = p.propdef.replace("<param_references>", blk.group(0) + "<param_references>", 1)
        ref = re.search(r'<reference [^>]*param_key="' + re.escape(k) + r'"/>', i_def).group(0)
        p.propdef = p.propdef.replace("</param_references>",
                                      ref.replace('attribute_category="StreamServe"',
                                                  f'attribute_category="{MQ_SYSTEM}"') + "</param_references>", 1)
    variant = re.search(r'attribute_id="(ctype::Adapter/cname::IBMMQ/[^"]*?)/attrId::', i_def).group(1)
    for param, key, label in MQ_EXTRA:
        cur = re.search(r"<key>%s</key>\s*<value>([^<]*)</value>" % key, xml).group(1)
        xml = iflow_lib.externalize(xml, "IBMMQ", key, "{{%s}}" % param, expect=cur)
        p.add(param, cur, ref=(MQ_SYSTEM, variant + "/attrId::" + key, label))
    print(f"  IBM MQ receiver: {len(used)} parameters from I2034 + {len(MQ_EXTRA)} externalized here")

    xml = st.rename_participant(xml, p, "MSAP", SENDER)
    xml = st.replace_counted(xml, [('name="SmarTeam"', f'name="{MQ_SYSTEM}"', 1)])
    p.propdef = p.propdef.replace('attribute_category="SmarTeam', f'attribute_category="{MQ_SYSTEM}')
    st.remove_unused(xml, p)
    assert re.search(r"<key>allowedHeaderList</key>\s*<value>\{\{AllowedHeaders\}\}</value>", xml)
    assert p.prop.count("HTTPS_UserRole=" + st.CHILD_ROLE) == 1
    return st.finish(name, files, xml, p, VERSION[name], FORBIDDEN, rename=True)


# MQ channel fields that are not tunable are accepted by the fixed-value check
st.NOT_TUNABLE |= MQ_TECHNICAL
st.KNOWN_PARTICIPANTS |= {SENDER, MQ_SYSTEM}


def main():
    only = sys.argv[sys.argv.index("--only") + 1] if "--only" in sys.argv else None
    for key, fn in (("child", build_child), ("parent", build_parent)):
        if only in (None, key):
            print(f"== {key}")
            name = fn()
            xml = iflw_of(st.read_archive(LONG + os.path.join(PKG, name, "build", name + ".zip"))[0])
            prop = st.read_archive(LONG + os.path.join(PKG, name, "build", name + ".zip"))[0][RES + "parameters.prop"]
            for fl in iflow_lib.best_practice_flags(xml, prop.decode("utf-8")):
                print("  FLAG:", fl)


if __name__ == "__main__":
    main()
