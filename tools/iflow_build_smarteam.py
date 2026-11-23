"""
tools/iflow_build_smarteam.py
Build the SmarTeam package iFlows (CPI package folder iflows/SmarTeam/).

Input:  iflows/SmarTeam/source/   (Bhavesh's exports, copied from the drop folder iflowdevelopment/)
Output: iflows/SmarTeam/<IFlowName>/build/<IFlowName>.zip + extracted <IFlowName>/

Usage:
  py -I tools/iflow_build_smarteam.py --only I2050_MaintenanceBOM_MSAP_SmarTeam_JMSToHTTP
  py -I tools/iflow_build_smarteam.py --selftest

Evidence for the jar -> design-time conversion: Bhavesh's I2049 runtime jar and design-time
Download zip of the same version 1.0.3 (L2, 2026-11-23). --selftest checks that the conversion
gives the design-time MANIFEST byte for byte.
"""
import copy
import datetime
import os
import re
import shutil
import sys
import zipfile

sys.stdout.reconfigure(encoding="utf-8")
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import iflow_lib  # noqa: E402
from iflow_lib import NS, _q  # noqa: E402

REPO = os.path.normpath(os.path.join(os.path.dirname(os.path.abspath(__file__)), ".."))
PKG = os.path.join(REPO, "iflows", "SmarTeam")
SOURCE = os.path.join(PKG, "source")
IFLW_DIR = "src/main/resources/scenarioflows/integrationflow/"


# ---------------------------------------------------------------------------
# Archives and MANIFEST
# ---------------------------------------------------------------------------

def read_archive(path: str) -> tuple[dict[str, bytes], dict[str, tuple]]:
    z = zipfile.ZipFile(path)
    return ({n: z.read(n) for n in z.namelist() if not n.endswith("/")},
            {i.filename: i.date_time for i in z.infolist()})


def mf_parse(b: bytes) -> tuple[str, list[list[str]]]:
    """-> (newline, [[key, raw_value]]); raw_value keeps its leading space."""
    t = b.decode("utf-8")
    nl = "\r\n" if "\r\n" in t else "\n"
    out = []
    for line in t.split(nl):
        if line.startswith(" "):
            out[-1][1] += line[1:]
        elif line:
            k, v = line.split(":", 1)
            out.append([k, v])
    return nl, out


def mf_write(nl: str, hdrs: list[list[str]]) -> bytes:
    """Write headers wrapped at 72 bytes (continuation lines start with one space)."""
    lines = []
    for k, v in hdrs:
        s = f"{k}:{v}"
        lines.append(s[:72])
        s = s[72:]
        while s:
            lines.append(" " + s[:71])
            s = s[71:]
    return (nl.join(lines) + nl + nl).encode("utf-8")


DESIGN_KEYS = ["Manifest-Version", "Bundle-ManifestVersion", "Bundle-Name", "Bundle-SymbolicName",
               "Bundle-Version", "SAP-BundleType", "SAP-NodeType", "SAP-RuntimeProfile",
               "Import-Package", "Origin-Bundle-Name", "Origin-Bundle-SymbolicName",
               "Require-Capability"]
DESIGN_IMPORT_START = "com.sap.esb.application.services.cxf.interceptor"


def jar_manifest_to_design(b: bytes) -> bytes:
    """Runtime MANIFEST -> design-time MANIFEST (rule from the I2049 jar/zip pair):
    keep only DESIGN_KEYS; Import-Package without the runtime prefix; Require-Capability
    with only the scriptcollection.* entries."""
    nl, hdrs = mf_parse(b)
    out = []
    for k, v in hdrs:
        if k not in DESIGN_KEYS:
            continue
        if k == "Import-Package":
            i = v.index(DESIGN_IMPORT_START)
            v = " " + v[i:]
        if k == "Require-Capability":
            items = [x for x in v.strip().split(",") if x.startswith("scriptcollection.")]
            v = " " + ",".join(items)
        out.append([k, v])
    return mf_write(nl, out)


def mf_set(b: bytes, values: dict[str, str]) -> bytes:
    nl, hdrs = mf_parse(b)
    for h in hdrs:
        if h[0] in values:
            h[1] = " " + values[h[0]]
    return mf_write(nl, hdrs)


def java_date(dt: tuple) -> str:
    d = datetime.datetime(*dt)
    return d.strftime("%a %b %d %H:%M:%S UTC %Y")


def to_design(files: dict[str, bytes], dates: dict[str, tuple], template_project: bytes) -> dict[str, bytes]:
    """Runtime jar -> design-time file set (src/main/resources/**, MANIFEST, .project, metainfo.prop)."""
    out = {n: b for n, b in files.items() if n.startswith("src/main/resources/")}
    out["META-INF/MANIFEST.MF"] = jar_manifest_to_design(files["META-INF/MANIFEST.MF"])
    out[".project"] = template_project
    out["metainfo.prop"] = ("#Store metainfo properties\n#%s\ndescription=\n"
                            % java_date(dates["META-INF/MANIFEST.MF"])).encode("utf-8")
    return out


def selftest() -> None:
    jar, _ = read_archive(os.path.join(SOURCE, "I2049_MaterialBOM_MSAP_SmarTeam_PDToHTTP.jar"))
    zp, _ = read_archive(os.path.join(SOURCE, "I2049_MaterialBOM_MSAP_SmarTeam_PDToHTTP.zip"))
    nl, h = mf_parse(zp["META-INF/MANIFEST.MF"])
    assert mf_write(nl, h) == zp["META-INF/MANIFEST.MF"], "MANIFEST round trip differs"
    assert jar_manifest_to_design(jar["META-INF/MANIFEST.MF"]) == zp["META-INF/MANIFEST.MF"], \
        "jar -> design MANIFEST differs from the I2049 design-time zip"
    iflw = [n for n in zp if n.endswith(".iflw")][0]
    assert jar[iflw] == zp[iflw], "I2049 jar and zip iflw differ"
    print("selftest OK: I2049 jar -> design-time MANIFEST is byte-identical to the Download zip")


# ---------------------------------------------------------------------------
# iflw edits
# ---------------------------------------------------------------------------

def by_id(root, i):
    el = root.find(f".//*[@id='{i}']")
    if el is None:
        raise KeyError(i)
    return el


def error_end_to_message_end(xml: str, end_id: str, name: str = "End") -> str:
    """Error End -> Message End, structure as in Bhavesh's I2018 export (EndEvent_734105, L2)."""
    root = iflow_lib.parse(xml)
    ev = by_id(root, end_id)
    ed = ev.find("bpmn2:errorEventDefinition", NS)
    assert ed is not None, f"{end_id} is not an error end"
    incoming = [e.text for e in ev.findall("bpmn2:incoming", NS)]
    for c in list(ev):
        ev.remove(c)
    ext = etree_sub(ev, "bpmn2:extensionElements")
    for k, v in (("componentVersion", "1.1"),
                 ("cmdVariantUri", "ctype::FlowstepVariant/cname::MessageEndEvent/version::1.1.0")):
        p = etree_sub(ext, "ifl:property")
        etree_sub(p, "key").text = k
        etree_sub(p, "value").text = v
    for i in incoming:
        etree_sub(ev, "bpmn2:incoming").text = i
    etree_sub(ev, "bpmn2:messageEventDefinition")
    ev.set("name", name)
    return iflow_lib.serialize(root)


def etree_sub(parent, tag):
    from lxml import etree
    return etree.SubElement(parent, _q(tag) if ":" in tag else tag)


def add_property_row(xml: str, step_id: str, row: str) -> str:
    root = iflow_lib.parse(xml)
    v = iflow_lib.get_prop(root, by_id(root, step_id), "propertyTable")
    v.text = (v.text or "") + row
    return iflow_lib.serialize(root)


def insert_step_after(xml: str, template_id: str, new_id: str, new_name: str,
                      after_id: str, flow_out_id: str, new_flow_id: str) -> str:
    """Copy step template_id as new_id and put it between after_id and the target of
    flow_out_id (which then starts at the new step). new_flow_id: after_id -> new step."""
    root = iflow_lib.parse(xml)
    tpl, after = by_id(root, template_id), by_id(root, after_id)
    new = copy.deepcopy(tpl)
    new.set("id", new_id)
    new.set("name", new_name)
    for e in new.findall("bpmn2:incoming", NS) + new.findall("bpmn2:outgoing", NS):
        new.remove(e)
    after.addnext(new)
    f_out = by_id(root, flow_out_id)
    assert f_out.get("sourceRef") == after_id
    f_out.set("sourceRef", new_id)
    f_new = copy.deepcopy(f_out)
    f_new.set("id", new_flow_id)
    f_new.set("sourceRef", after_id)
    f_new.set("targetRef", new_id)
    f_out.addprevious(f_new)
    xml = iflow_lib.serialize(root)
    xml, _ = iflow_lib.sync_flow_refs(xml)
    return xml


def unused_params(xml: str, prop: str) -> list[str]:
    used = set(re.findall(r"\{\{([^}]+)\}\}", xml))
    return [k for k in iflow_lib.Params(prop, "").keys() if k not in used]


# ---------------------------------------------------------------------------
# Checks + packing
# ---------------------------------------------------------------------------

def check_and_write(name: str, files: dict[str, bytes], forbidden: list[str]) -> None:
    iflw = [n for n in files if n.endswith(".iflw")]
    assert iflw == [IFLW_DIR + name + ".iflw"], f"iflw file name: {iflw}"
    xml = files[iflw[0]].decode("utf-8")
    prop = files["src/main/resources/parameters.prop"].decode("utf-8")
    propdef = files["src/main/resources/parameters.propdef"].decode("utf-8")
    errs = iflow_lib.check_iflow(xml, prop, propdef) + empty_logpayload_rows(xml) + logch_name_errors(xml)
    _, mf = mf_parse(files["META-INF/MANIFEST.MF"])
    mfd = dict(mf)
    for k in ("Bundle-Name", "Bundle-SymbolicName", "Origin-Bundle-Name", "Origin-Bundle-SymbolicName"):
        if mfd.get(k, "").strip() != name:
            errs.append(f"MANIFEST {k} = {mfd.get(k)!r}")
    if f"<name>{name}</name>" not in files[".project"].decode("utf-8"):
        errs.append(".project name differs")
    for n, b in files.items():
        t = b.decode("utf-8", errors="replace")
        for bad in ["claude", "anthropic"] + forbidden:
            if bad.lower() in t.lower():
                errs.append(f"'{bad}' found in {n}")
        if n.endswith((".iflw", ".propdef", ".xsd", ".mmap", ".project")):
            try:
                iflow_lib.etree.fromstring(b)
            except Exception as e:  # noqa: BLE001
                errs.append(f"{n} not well-formed: {e}")
    if errs:
        print("CHECKS FAILED:")
        for e in errs:
            print("  -", e)
        sys.exit(1)
    # \\?\ prefix: the I2023/I2024 names give paths over 260 characters on Windows
    out_dir = "\\\\?\\" + os.path.abspath(os.path.join(PKG, name, "build"))
    os.makedirs(out_dir, exist_ok=True)
    zpath = os.path.join(out_dir, name + ".zip")
    with zipfile.ZipFile(zpath, "w", zipfile.ZIP_DEFLATED) as z:
        for n, b in files.items():
            z.writestr(n, b)
    ext = os.path.join(out_dir, name)
    if os.path.isdir(ext):
        shutil.rmtree(ext)
    with zipfile.ZipFile(zpath) as z:
        z.extractall(ext)
    print(f"checks OK, wrote {os.path.relpath(os.path.join(PKG, name, 'build', name + '.zip'), REPO)}"
          " (+ extracted folder)")


# ---------------------------------------------------------------------------
# Generic steps (lessons from the I2050 round, 2026-11-23)
# ---------------------------------------------------------------------------

ROW_WORKID = ("<row><cell id='Action'>Create</cell><cell id='Type'>xpath</cell>"
              "<cell id='Value'>/InboundResponse/WorkId</cell>"
              "<cell id='Default'></cell><cell id='Name'>CH_SmarTeamWorkId</cell>"
              "<cell id='Datatype'>java.lang.String</cell></row>")
LOGCH_TEMPLATE = "CallActivity_734029"   # the UTIL_LogCustomHeaders step in every SmarTeam child
LOGCH_NAME = "LogCustomHeaders"          # step name for every logCustomHeaders.groovy step (user, 2026-11-23)
DX = 160


def add_workid_header(xml: str, prefix: str, send_id: str) -> str:
    """After the SmarTeam call: CH_SmarTeamWorkId in the Content Modifier that follows it, then a
    copy of "Set Custom Header". Steps to the right shift by DX; the pool widens by DX."""
    root = iflow_lib.parse(xml)
    proc = by_id(root, send_id).getparent()
    out = {f.get("sourceRef"): f for f in proc.findall("bpmn2:sequenceFlow", NS)}
    cm_id = out[send_id].get("targetRef")
    assert iflow_lib.get_prop(root, by_id(root, cm_id), "propertyTable") is not None
    flow_after_cm = out[cm_id].get("id")
    plane = root.find(".//bpmndi:BPMNPlane", NS)
    shapes = {s.get("bpmnElement"): s for s in plane.findall("bpmndi:BPMNShape", NS)}
    cx, cy, _, _ = iflow_lib._bounds(shapes[cm_id])
    node_ids = [e.get("id") for e in proc if e.get("id")]
    shift_ids = [i for i in node_ids if i in shapes and iflow_lib._bounds(shapes[i])[0] > cx]
    pool = root.find(f".//bpmn2:participant[@processRef='{proc.get('id')}']", NS).get("id")
    px, py, pw, ph = iflow_lib._bounds(shapes[pool])

    new_id = f"{prefix}_CA_LogCustomHeaders"
    xml = add_property_row(xml, cm_id, ROW_WORKID)
    xml = insert_step_after(xml, template_id=LOGCH_TEMPLATE, new_id=new_id, new_name=LOGCH_NAME,
                            after_id=cm_id, flow_out_id=flow_after_cm, new_flow_id=f"{prefix}_SF_toLogCH")
    xml, log = iflow_lib.fix_diagram(xml, bounds={new_id: (cx + DX, cy, 100, 60), pool: (px, py, pw + DX, ph)},
                                     shift=(shift_ids, DX))
    print(f"  WorkId header after {cm_id}; shifted {len(shift_ids)} steps")
    return xml


def odata_idle_settings(xml: str, p, channel: str, prefix: str, propdef_category: str):
    """Bhavesh's I2050_P 1.0.5 change (L2): externalize Delete Idle Connection (true) and
    Idle Timeout (300) on an OData GET receiver."""
    root = iflow_lib.parse(xml)
    mf = iflow_lib._owner(root, channel, "messageFlow")
    variant = iflow_lib.get_prop(root, mf, "cmdVariantUri").text      # …/version::1.32.1
    aid = variant + "/attrId::"
    for key, pname, value, type_, combo, label in (
            ("clearStaleConnection", f"{prefix}_DeleteIdleConnection", "true", "xsd:boolean", False,
             "Delete Idle Connection"),
            ("maxIdleTimeout", f"{prefix}_IdleTimeout", "300", "xsd:integer", None, "Idle Timeout (in seconds)")):
        v = iflow_lib.get_prop(root, mf, key)
        v.text = "{{%s}}" % pname
        p.add(pname, value, type_, ref=(propdef_category, aid + key, label), combobox=combo)
    return iflow_lib.serialize(root)


def is_logch(e, root) -> bool:
    props = {q.findtext("key"): q.findtext("value")
             for q in e.findall("bpmn2:extensionElements/ifl:property", NS)}
    return props.get("activityType") == "Script" and props.get("script") == "logCustomHeaders.groovy"


def name_logch_steps(xml: str) -> str:
    """Every logCustomHeaders.groovy step is named LogCustomHeaders (user, 2026-11-23: was
    "Set Custom Header", "Log Custom Header(s)", "Log Headers")."""
    root = iflow_lib.parse(xml)
    renamed = []
    for e in root.iter(_q("bpmn2:callActivity")):
        if is_logch(e, root) and e.get("name") != LOGCH_NAME:
            renamed.append(e.get("name"))
            e.set("name", LOGCH_NAME)
    if renamed:
        print(f"  step names -> {LOGCH_NAME}: {', '.join(repr(r) for r in renamed)}")
    return iflow_lib.serialize(root)


def logch_name_errors(xml: str) -> list[str]:
    root = iflow_lib.parse(xml)
    return [f"step {e.get('id')} {e.get('name')!r} runs logCustomHeaders.groovy but is not named {LOGCH_NAME}"
            for e in root.iter(_q("bpmn2:callActivity")) if is_logch(e, root) and e.get("name") != LOGCH_NAME]


def finish(name: str, files: dict, xml: str, p, version: str, forbidden: list[str], rename: bool) -> str:
    pp, pd = "src/main/resources/parameters.prop", "src/main/resources/parameters.propdef"
    for n in [n for n in files if n.endswith(".iflw")]:
        files.pop(n)
    xml = name_logch_steps(xml)
    files[IFLW_DIR + name + ".iflw"] = xml.encode("utf-8")
    files[pp], files[pd] = p.prop.encode("utf-8"), p.propdef.encode("utf-8")
    vals = {"Bundle-Version": version}
    if rename:
        vals.update({k: name for k in ("Bundle-Name", "Bundle-SymbolicName", "Origin-Bundle-Name",
                                       "Origin-Bundle-SymbolicName")})
        files[".project"] = re.sub(rb"<name>[^<]*</name>", b"<name>" + name.encode() + b"</name>",
                                   files[".project"], count=1)
    files["META-INF/MANIFEST.MF"] = mf_set(files["META-INF/MANIFEST.MF"], vals)
    order = [IFLW_DIR + name + ".iflw", pp, pd]
    files = {k: files[k] for k in order + sorted(k for k in files if k not in order)}
    check_and_write(name, files, forbidden=forbidden)
    return name


def read_folder_package(pkg_zip: str, folder: str) -> dict[str, bytes]:
    """One iFlow from a package export whose iFlows are plain folders (<folder>/META-INF/…)."""
    z = zipfile.ZipFile(os.path.join(SOURCE, pkg_zip))
    pre = folder + "/"
    files = {n[len(pre):]: z.read(n) for n in z.namelist() if n.startswith(pre) and not n.endswith("/")}
    if not files:
        raise FileNotFoundError(f"{folder} not in {pkg_zip}")
    return files


def replace_counted(text: str, pairs) -> str:
    for old, new, n in pairs:
        assert text.count(old) == n, f"{old!r}: found {text.count(old)}, expected {n}"
        text = text.replace(old, new)
    return text


def remove_unused(xml: str, p) -> None:
    removed = unused_params(xml, p.prop)
    for k in removed:
        p.remove(k)
    print("  removed unused parameters:", ", ".join(removed) or "-")


def rename_params(xml: str, p, pairs) -> str:
    for old, new in pairs:
        assert xml.count("{{%s}}" % old) >= 1, old
        assert new not in p.keys(), new
        xml = xml.replace("{{%s}}" % old, "{{%s}}" % new)
        p.rename(old, new)
    if pairs:
        print("  renamed parameters:", ", ".join(f"{o} -> {n}" for o, n in pairs))
    return xml


# ---------------------------------------------------------------------------
# Children
# ---------------------------------------------------------------------------

I2050_NEW = "I2050_MaintenanceBOM_MSAP_SmarTeam_JMSToHTTP"
I2050_OLD = "I2050_MaintananceBOM_MSAP_SmarTeam_PDToHTTP"
I2049_NEW = "I2049_MaterialBOM_MSAP_SmarTeam_JMSToHTTP"
I2049_OLD = "I2049_MaterialBOM_MSAP_SmarTeam_PDToHTTP"
I2018 = "I2018_Material_MSAP_SmarTeam_JMSToHTTP"
I2023 = "I2023_Equipment_COD_EQUIPMENT_SAVE_COD_EQUIPMENT_SAVE01_MSAP_SmarTeam_JMSToHTTP"
I2024 = "I2024_FunctionLocation_COD_FUNCTIONAL_LOCATION_SAVE_COD_FUNCTIONAL_LOCATION_SAVE01_MSAP_SmarTeam_JMSToHTTP"

# XPaths without local-name() (user rule 2026-11-23: only when asked or when there is a logical reason).
# Checked against Bhavesh's sample (I2050) and the mapping source XSD/WSDL of each flow.
SMI = "Set Monitoring Identifiers"
MBOM = "/BOMHeader/MaintBOMHeader_Type/"          # MaintBOMInput.xsd + sample 2026-11-23
XBOM = "/MaterialBOM/MaterialBOMType/"            # MaterialBOM_Input.xsd
PROD = "/*/ProductMDMReplicateRequestMessage/Product/"   # WSDL: root is namespaced, children are not -> /*
XPATH_I2050 = [(SMI, "CH_BillOfMaterial", MBOM + "BillOfMaterial"),
               (SMI, "CH_BillOfMaterialCategory", MBOM + "BillOfMaterialCategory"),
               (SMI, "CH_BillOfMaterialVariant", MBOM + "BillOfMaterialVariant"),   # read BillOfMaterialCategory
               (SMI, "CH_Plant", MBOM + "Plant"),
               (SMI, "CH_TechnicalObject", MBOM + "TechnicalObject"),
               (SMI, "SAP_ApplicationID", MBOM + "TechnicalObject")]
XPATH_I2049 = [(SMI, "CH_BillOfMaterial", XBOM + "BillOfMaterial"),
               (SMI, "CH_BillOfMaterialCategory", XBOM + "BillOfMaterialCategory"),
               (SMI, "CH_BillOfMaterialVariant", XBOM + "BillOfMaterialVariant"),   # read …VariantUsage
               (SMI, "CH_Plant", XBOM + "Plant"),
               (SMI, "CH_Material", XBOM + "Material"),
               (SMI, "SAP_ApplicationID", XBOM + "Material")]
XPATH_I2018 = [(SMI, "CH_Material", PROD + "ProductInternalID"),
               (SMI, "CH_MaterialType", PROD + "ProductTypeCode"),
               (SMI, "SAP_ApplicationID", PROD + "ProductInternalID")]
XPATH_I2018_P = [(SMI, "CH_Material", PROD + "ProductInternalID"),
                 (SMI, "CH_MessageID", "/*/MessageHeader/ID")]


def set_constant_rows(xml: str, fixes) -> str:
    """Set the Value of constant rows (by row Name) in Content Modifiers named `step`.
    Used for LogPayloadSize, which I2049_P/I2050_P create with an empty value (2026-11-23)."""
    root = iflow_lib.parse(xml)
    for step, name, new in fixes:
        hits = 0
        for owner in [e for e in root.iter(_q("bpmn2:callActivity")) if e.get("name") == step]:
            v = iflow_lib.get_prop(root, owner, "propertyTable")
            for row in re.findall(r"<row>.*?</row>", v.text or ""):
                if f"<cell id='Name'>{name}</cell>" in row and "<cell id='Type'>constant</cell>" in row:
                    v.text = v.text.replace(row, re.sub(r"<cell id='Value'>.*?</cell>",
                                                        lambda m: f"<cell id='Value'>{new}</cell>", row))
                    hits += 1
        assert hits == 1, f"{step}/{name}: {hits} constant rows"
        print(f"  constant {name} = {new}")
    return iflow_lib.serialize(root)


def empty_logpayload_rows(xml: str) -> list[str]:
    """Build check: a LogPayload / LogPayloadSize property row must not be empty."""
    errs = []
    for m in re.finditer(r'callActivity id="[^"]+" name="([^"]+)"(.*?)</bpmn2:callActivity>', xml, re.S):
        for row in re.findall(r"&lt;row&gt;(.*?)&lt;/row&gt;", m.group(2)):
            name = re.search(r"cell id='Name'&gt;(.*?)&lt;", row)
            value = re.search(r"cell id='Value'&gt;(.*?)&lt;", row)
            if name and name.group(1) in ("LogPayload", "LogPayloadSize") and value and not value.group(1):
                errs.append(f"{m.group(1)}: property {name.group(1)} has an empty value")
    return errs


def set_xpaths(xml: str, fixes) -> str:
    """Replace the Value of xpath rows (by row Name) in a Content Modifier's property/header table."""
    root = iflow_lib.parse(xml)
    for step, name, new in fixes:
        hits = 0
        for owner in [e for e in root.iter(_q("bpmn2:callActivity")) if e.get("name") == step]:
            for table in ("propertyTable", "headerTable"):
                try:
                    v = iflow_lib.get_prop(root, owner, table)
                except KeyError:
                    continue
                for row in re.findall(r"<row>.*?</row>", v.text or ""):
                    if f"<cell id='Name'>{name}</cell>" in row and "<cell id='Type'>xpath</cell>" in row:
                        new_row = re.sub(r"<cell id='Value'>.*?</cell>",
                                         lambda m: f"<cell id='Value'>{new}</cell>", row)
                        v.text = v.text.replace(row, new_row)
                        hits += 1
        assert hits >= 1, f"{step}/{name}: no xpath row"
        print(f"  xpath {name} = {new} ({hits} row{'s' if hits > 1 else ''})")
    xml = iflow_lib.serialize(root)
    assert "local-name()" not in xml, "local-name() left in the iflw"
    return xml


CHILD_ALLOWED_HEADERS = r"SSAB.*|SAP.*"   # as written in parameters.prop (I2023/I2024 already had it)

CHILDREN = {
    # name: source jar, old name, version, prefix, send step, error end, extra iflw edits, prop sets, OData lookup
    I2050_NEW: dict(src=I2050_OLD + ".jar", old=I2050_OLD, version="1.0.7", prefix="I2050",
                    send="I2050_ServiceTask_Send", error_end="EndEvent_734103",
                    props={"SAP_MessageType": "MaintenanceBOM"}, xpaths=XPATH_I2050),
    I2049_NEW: dict(src=I2049_OLD + ".jar", old=I2049_OLD, version="1.0.5", prefix="I2049",
                    send="I2049_ServiceTask_Send", error_end="EndEvent_734103", xpaths=XPATH_I2049),
    I2018: dict(src=I2018 + ".jar", old=I2018, version="1.1.2", prefix="I2018", send="ServiceTask_734107",
                xpaths=XPATH_I2018),
    I2023: dict(src=I2023 + ".jar", old=I2023, version="1.1.2", prefix="I2023", send="ServiceTask_734125",
                odata=("OData", "MSAP", "MSAP_Lookup")),
    I2024: dict(src=I2024 + ".jar", old=I2024, version="1.0.8", prefix="I2024", send="ServiceTask_734137",
                edits=[('name="Request Reply 1"', 'name="Send to SmarTeam"', 1)],
                odata=("OData", "MSAP", "Receiver1")),
}


def build_child(name: str) -> str:
    """Child round 2026-11-23: _JMSToHTTP name (typo fixed), success end, CH_SmarTeamWorkId header,
    unused parameters out, iflw file = iFlow name; OData lookups get the idle settings."""
    c = CHILDREN[name]
    src, dates = read_archive(os.path.join(SOURCE, c["src"]))
    tpl, _ = read_archive(os.path.join(SOURCE, "I2049_MaterialBOM_MSAP_SmarTeam_PDToHTTP.zip"))
    files = to_design(src, dates, tpl[".project"])
    xml = [b for n, b in files.items() if n.endswith(".iflw")][0].decode("utf-8")
    if c["old"] != name:
        xml = iflow_lib.externalize(xml, "ProcessDirect", "address", "/" + name, expect="/" + c["old"])
        xml = iflow_lib.externalize(xml, "HTTPS", "urlPath", "/" + name, expect="/" + c["old"])
    if c.get("error_end"):
        xml = error_end_to_message_end(xml, c["error_end"])
    xml = replace_counted(xml, c.get("edits", []))
    xml = add_workid_header(xml, c["prefix"], c["send"])
    xml = set_xpaths(xml, c.get("xpaths", []))
    p = iflow_lib.Params(files["src/main/resources/parameters.prop"].decode("utf-8"),
                         files["src/main/resources/parameters.propdef"].decode("utf-8"))
    for k, v in c.get("props", {}).items():
        p.set(k, v)
    # Every child: runtime Allowed Headers externalized as AllowedHeaders = SSAB.*|SAP.* (user, 2026-11-23)
    assert re.search(r"<key>allowedHeaderList</key>\s*<value>\{\{AllowedHeaders\}\}</value>", xml), \
        "Allowed Headers is not {{AllowedHeaders}}"
    p.set("AllowedHeaders", CHILD_ALLOWED_HEADERS)
    if c.get("odata"):
        xml = odata_idle_settings(xml, p, *c["odata"])
    remove_unused(xml, p)
    return finish(name, files, xml, p, c["version"], ["Maintanance", "PDToHTTP"], rename=True)


# ---------------------------------------------------------------------------
# Parents
# ---------------------------------------------------------------------------

PKG_PLANT_MAINT = "MSAPPlantMaintenanceMasterData_artifacts (1).zip"
PKG_CONTROLLING = "MSAPControllingMasterData_artifacts (4).zip"
S4_RENAMES = [  # OData receiver (S4) and HTTPS retrigger sender (user, 2026-11-23)
    ("S4 Address", "S4_Address"),
    ("S4 Authentication", "S4_Authentication"),
    ("S4 Credential Name", "S4_CredentialName"),
    ("S4 Location ID", "S4_LocationID"),
    ("S4 CSRF Protected", "S4_CSRFProtected"),
    ("S4 Reuse Connection", "S4_ReuseConnection"),
    ("proxy Type", "S4_ProxyType"),
    ("Body Size", "HTTPS_BodySize"),
]
I2050_P = "I2050_P_MaintenanceBOM_MSAP_AMQPToJMS"
I2049_P = "I2049_P_MaterialBOM_MSAP_AMQPToJMS"
I2018_P = "I2018_P_Material_MSAP_SOAPToJMS"
I2023_P = "I2023_P_Equipment_COD_EQUIPMENT_SAVE_COD_EQUIPMENT_SAVE01_MSAP_IDocToJMS"
I2024_P = "I2024_P_FunctionLocation_COD_FUNCTIONAL_LOCATION_SAVE_COD_FUNCTIONAL_LOCATION_SAVE01_MSAP_IDocToJMS"
FLOC_MT = "COD_FUNCTIONAL_LOCATION_SAVE.COD_FUNCTIONAL_LOCATION_SAVE01"

PARENTS = {
    # I2050_P: Bhavesh's CPI version 1.0.5 (2026-11-23) is the new baseline; only the misspelt name is fixed
    I2050_P: dict(src=(None, I2050_P + ".zip"), version="1.0.8",
                  renames=[("S4_DeleteIdleConnnectopn", "S4_DeleteIdleConnection")],
                  # 1.0.7: LogPayloadSize was an empty constant and not externalized (also in 1.0.3/1.0.5)
                  constants=[(SMI, "LogPayloadSize", "{{LogPayloadSize}}")],
                  new_params=[("LogPayloadSize", "512")]),
    I2049_P: dict(src=(PKG_PLANT_MAINT, I2049_P), version="1.0.5",
                  rd=[(f'"{I2049_OLD}"', f'"{I2049_NEW}"', 1)],
                  edits=[('name="Intial Properties"', 'name="Initial Properties"', 1)],
                  renames=S4_RENAMES, props={"S4_CSRFProtected": "false"}, odata=("OData", "S4", "MSAP_PO"),
                  # 1.0.5: LogPayloadSize was an empty constant (same gap as I2050_P)
                  constants=[(SMI, "LogPayloadSize", "{{LogPayloadSize}}")],
                  new_params=[("LogPayloadSize", "512")]),
    I2018_P: dict(src=(PKG_CONTROLLING, I2018_P), version="1.0.18", xpaths=XPATH_I2018_P),
    I2023_P: dict(src=(PKG_CONTROLLING, I2023_P), version="1.0.8"),
    I2024_P: dict(src=(PKG_CONTROLLING, I2024_P), version="1.0.9", props={"SAP_MessageType": FLOC_MT}),
}


def build_parent(name: str) -> str:
    """Parent round 2026-11-23: receiver iFlow name, typos, unused parameters out, spaced names
    renamed, iflw file = iFlow name; OData GET lookups: CSRF off + idle settings."""
    c = PARENTS[name]
    pkg, part = c["src"]
    files = read_folder_package(pkg, part) if pkg else read_archive(os.path.join(SOURCE, part))[0]
    nl, h = mf_parse(files["META-INF/MANIFEST.MF"])
    assert mf_write(nl, h) == files["META-INF/MANIFEST.MF"], "MANIFEST round trip differs"
    rd = "src/main/resources/script/ReceiverDetermination.groovy"
    if c.get("rd"):
        files[rd] = replace_counted(files[rd].decode("utf-8"), c["rd"]).encode("utf-8")
    xml = [b for n, b in files.items() if n.endswith(".iflw")][0].decode("utf-8")
    xml = replace_counted(xml, c.get("edits", []))
    xml = set_xpaths(xml, c.get("xpaths", []))
    xml = set_constant_rows(xml, c.get("constants", []))
    p = iflow_lib.Params(files["src/main/resources/parameters.prop"].decode("utf-8"),
                         files["src/main/resources/parameters.propdef"].decode("utf-8"))
    remove_unused(xml, p)
    xml = rename_params(xml, p, c.get("renames", []))
    for k, v in c.get("new_params", []):     # same definition as in the children (xsd:string)
        assert k not in p.keys(), k
        p.add(k, v)
    for k, v in c.get("props", {}).items():
        assert k in p.keys(), k
        p.set(k, v)
    if c.get("odata"):
        xml = odata_idle_settings(xml, p, *c["odata"])
    return finish(name, files, xml, p, c["version"],
                  ["Maintanance", "PDToHTTP", "Intial", "Contition", "Connnectopn"], rename=False)


ONLY = {**{n: (lambda n=n: build_child(n)) for n in CHILDREN},
        **{n: (lambda n=n: build_parent(n)) for n in PARENTS}}


def main():
    if len(sys.argv) >= 2 and sys.argv[1] == "--selftest":
        selftest()
        return
    if len(sys.argv) >= 2 and sys.argv[1] == "--all":
        selftest()
        for n in ONLY:
            print(f"== {n}")
            ONLY[n]()
        return
    if len(sys.argv) >= 3 and sys.argv[1] == "--only":
        for n in sys.argv[2:]:
            print(f"== {n}")
            ONLY[n]()
        return
    print(__doc__)


if __name__ == "__main__":
    main()
