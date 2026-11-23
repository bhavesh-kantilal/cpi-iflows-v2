"""
Reusable iFlow (.iflw / parameters.prop / parameters.propdef) helpers.

- fix_diagram():      keep the BPMN diagram in line with the process model
                      (drop orphan shapes/edges, set bounds, add missing edges)
- externalize():      replace an adapter/step property value with {{Param}}
- Params:             edit parameters.prop + parameters.propdef together
- check_iflow():      consistency checks used by every iFlow build

Lesson (I0539 v1.0.0 feedback, L2, 2026-11-16): rewriting a process without
updating BPMNDiagram leaves CPI without arrows ("connection missing").
"""
import re

from lxml import etree

NS = {
    "bpmn2": "http://www.omg.org/spec/BPMN/20100524/MODEL",
    "bpmndi": "http://www.omg.org/spec/BPMN/20100524/DI",
    "dc": "http://www.omg.org/spec/DD/20100524/DC",
    "di": "http://www.omg.org/spec/DD/20100524/DI",
    "ifl": "http:///com.sap.ifl.model/Ifl.xsd",
    "xsi": "http://www.w3.org/2001/XMLSchema-instance",
}
XML_DECL = b'<?xml version="1.0" encoding="UTF-8"?>'


def parse(xml: str):
    return etree.fromstring(xml.encode("utf-8"))


def serialize(root) -> str:
    return (XML_DECL + etree.tostring(root, encoding="UTF-8")).decode("utf-8")


def _q(tag: str) -> str:
    p, local = tag.split(":")
    return "{%s}%s" % (NS[p], local)


# ---------------------------------------------------------------------------
# Diagram
# ---------------------------------------------------------------------------

def _model_ids(root) -> set:
    plane = root.find(".//bpmndi:BPMNPlane", NS)
    ids = set()
    for el in root.iter():
        if plane is not None and el is not plane and _is_descendant(el, plane):
            continue
        i = el.get("id")
        if i:
            ids.add(i)
    return ids


def _is_descendant(el, anc) -> bool:
    p = el.getparent()
    while p is not None:
        if p is anc:
            return True
        p = p.getparent()
    return False


def _bounds(shape):
    b = shape.find("dc:Bounds", NS)
    return tuple(float(b.get(k)) for k in ("x", "y", "width", "height"))


def _flow_node_kinds():
    return {"startEvent", "endEvent", "callActivity", "serviceTask", "task",
            "exclusiveGateway", "parallelGateway", "intermediateCatchEvent",
            "intermediateThrowEvent", "subProcess"}


def flow_ref_mismatches(root) -> list[tuple]:
    """(element, expected_in, expected_out) for every flow node whose
    <incoming>/<outgoing> lists differ from the sequenceFlows of its process."""
    out = []
    for proc in root.iter(_q("bpmn2:process")):
        flows = proc.findall("bpmn2:sequenceFlow", NS)
        for el in proc:
            if etree.QName(el).localname not in _flow_node_kinds():
                continue
            i = el.get("id")
            exp_in = [f.get("id") for f in flows if f.get("targetRef") == i]
            exp_out = [f.get("id") for f in flows if f.get("sourceRef") == i]
            has_in = [e.text for e in el.findall("bpmn2:incoming", NS)]
            has_out = [e.text for e in el.findall("bpmn2:outgoing", NS)]
            if sorted(has_in) != sorted(exp_in) or sorted(has_out) != sorted(exp_out):
                out.append((el, exp_in, exp_out))
    return out


def sync_flow_refs(xml: str) -> tuple[str, list[str]]:
    """Rebuild <incoming>/<outgoing> of flow nodes whose lists do not match the
    sequenceFlows (e.g. a step still pointing to a removed flow)."""
    root = parse(xml)
    log = []
    for el, exp_in, exp_out in flow_ref_mismatches(root):
        for e in el.findall("bpmn2:incoming", NS) + el.findall("bpmn2:outgoing", NS):
            el.remove(e)
        ext = el.find("bpmn2:extensionElements", NS)
        pos = (list(el).index(ext) + 1) if ext is not None else 0
        for tag, ids in (("incoming", exp_in), ("outgoing", exp_out)):
            for fid in ids:
                n = etree.Element(_q("bpmn2:" + tag))
                n.text = fid
                el.insert(pos, n)
                pos += 1
        log.append(f"refs {el.get('id')}: in={exp_in} out={exp_out}")
    return serialize(root), log


def remove_sequence_flow(xml: str, flow_id: str) -> str:
    root = parse(xml)
    f = root.find(f".//bpmn2:sequenceFlow[@id='{flow_id}']", NS)
    f.getparent().remove(f)
    return serialize(root)


def fix_diagram(xml: str, bounds: dict | None = None,
                shift: tuple | None = None) -> tuple[str, list[str]]:
    """bounds: {bpmnElement_id: (x, y, w, h)} overrides.
    shift: (ids, dx): move these shapes by dx, and the waypoints of edges between them.
    Returns (xml, log). Removes DI elements whose bpmnElement no longer exists,
    applies shift and bounds, then (re)creates edges for flows touching a moved
    shape and adds edges for flows that have none."""
    root = parse(xml)
    log = []
    plane = root.find(".//bpmndi:BPMNPlane", NS)
    ids = _model_ids(root)

    for di_el in list(plane):
        ref = di_el.get("bpmnElement")
        if ref and ref not in ids:
            plane.remove(di_el)
            log.append(f"removed orphan {etree.QName(di_el).localname} {ref}")

    shapes = {s.get("bpmnElement"): s for s in plane.findall("bpmndi:BPMNShape", NS)}
    moved = set()
    if shift:
        sids, dx = shift
        shape_ids = {shapes[r].get("id") for r in sids if r in shapes}
        for r in sids:
            if r in shapes:
                b = shapes[r].find("dc:Bounds", NS)
                b.set("x", repr(float(b.get("x")) + dx))
        for e in plane.findall("bpmndi:BPMNEdge", NS):
            if e.get("sourceElement") in shape_ids and e.get("targetElement") in shape_ids:
                for wp in e.findall("di:waypoint", NS):
                    wp.set("x", repr(float(wp.get("x")) + dx))
        moved |= {r for r in sids if r in shapes}
        log.append(f"shifted {len(sids)} shapes by {dx}")
    for ref, (x, y, w, h) in (bounds or {}).items():
        s = shapes.get(ref)
        if s is None:   # new step without a shape: create it
            proc_el = root.find(f".//*[@id='{ref}']", NS)
            s = etree.SubElement(plane, _q("bpmndi:BPMNShape"))
            s.set("bpmnElement", ref)
            s.set("id", "BPMNShape_" + ref)
            etree.SubElement(s, _q("dc:Bounds"))
            shapes[ref] = s
            log.append(f"added shape {ref} ({proc_el.get('name') if proc_el is not None else ''})")
        b = s.find("dc:Bounds", NS)
        for k, v in zip(("height", "width", "x", "y"), (h, w, x, y)):
            b.set(k, repr(float(v)))
        moved.add(ref)
        log.append(f"bounds {ref} -> {x},{y},{w},{h}")
    shifted_both = set()
    if shift:
        shifted_both = {r for r in shift[0] if r in shapes}

    edges = {e.get("bpmnElement"): e for e in plane.findall("bpmndi:BPMNEdge", NS)}
    flows = root.findall(".//bpmn2:sequenceFlow", NS) + root.findall(".//bpmn2:messageFlow", NS)
    for f in flows:
        fid, src, tgt = f.get("id"), f.get("sourceRef"), f.get("targetRef")
        stale = fid in edges and src in shapes and tgt in shapes and (
            edges[fid].get("sourceElement") != shapes[src].get("id")
            or edges[fid].get("targetElement") != shapes[tgt].get("id"))
        if fid in edges and src not in moved and tgt not in moved and not stale:
            continue
        if (fid in edges and not stale and src in shifted_both and tgt in shifted_both
                and src not in (bounds or {}) and tgt not in (bounds or {})):
            continue   # moved together with its ends
        if src not in shapes or tgt not in shapes:
            log.append(f"WARN no shape for {fid} ({src}->{tgt})")
            continue
        sx, sy, sw, sh = _bounds(shapes[src])
        tx, ty, tw, th = _bounds(shapes[tgt])
        if tx >= sx + sw:                       # target to the right: side to side
            p1, p2 = (sx + sw, sy + sh / 2), (tx, ty + th / 2)
        elif ty >= sy + sh:                     # target below: bottom to top
            p1, p2 = (sx + sw / 2, sy + sh), (tx + tw / 2, ty)
        elif ty + th <= sy:                     # target above: top to bottom
            p1, p2 = (sx + sw / 2, sy), (tx + tw / 2, ty + th)
        else:                                   # target to the left
            p1, p2 = (sx, sy + sh / 2), (tx + tw, ty + th / 2)
        if fid in edges:
            e = edges[fid]
            for wp in e.findall("di:waypoint", NS):
                e.remove(wp)
            e.set("sourceElement", shapes[src].get("id"))
            e.set("targetElement", shapes[tgt].get("id"))
            action = "rerouted"
        else:
            e = etree.SubElement(plane, _q("bpmndi:BPMNEdge"))
            e.set("bpmnElement", fid)
            e.set("id", "BPMNEdge_" + fid)
            e.set("sourceElement", shapes[src].get("id"))
            e.set("targetElement", shapes[tgt].get("id"))
            action = "added edge"
        for x, y in (p1, p2):
            wp = etree.SubElement(e, _q("di:waypoint"))
            wp.set("x", repr(float(x)))
            wp.set(_q("xsi:type"), "dc:Point")
            wp.set("y", repr(float(y)))
        log.append(f"{action} {fid}")
    return serialize(root), log


# ---------------------------------------------------------------------------
# Externalization
# ---------------------------------------------------------------------------

def _owner(root, name: str, kind: str):
    hits = [e for e in root.iter(_q("bpmn2:" + kind)) if e.get("name") == name]
    if len(hits) != 1:
        raise ValueError(f"{kind} '{name}': {len(hits)} matches")
    return hits[0]


def get_prop(root, owner, key: str):
    for p in owner.iterfind("bpmn2:extensionElements/ifl:property", NS):
        if p.findtext("key") == key:
            return p.find("value")
    raise KeyError(f"{owner.get('name')}: property {key} not found")


def externalize(xml: str, owner_name: str, key: str, new_value: str,
                kind: str = "messageFlow", expect: str | None = None) -> str:
    """Set property <key> of the bpmn2:<kind> named owner_name to new_value
    (usually '{{Param}}'). expect: the value that must be there now."""
    root = parse(xml)
    v = get_prop(root, _owner(root, owner_name, kind), key)
    if expect is not None and (v.text or "") != expect:
        raise ValueError(f"{owner_name}.{key}: expected {expect!r}, found {v.text!r}")
    v.text = new_value
    return serialize(root)


def add_table_row(xml: str, step_name: str, table: str, row: str) -> str:
    """Append a <row>…</row> to a Content Modifier propertyTable/headerTable."""
    root = parse(xml)
    v = get_prop(root, _owner(root, step_name, "callActivity"), table)
    v.text = (v.text or "") + row
    return serialize(root)


# ---------------------------------------------------------------------------
# parameters.prop + parameters.propdef
# ---------------------------------------------------------------------------

PARAM_TMPL = """<parameter>
    <key/>
    <name>{name}</name>
    <type>{type}</type>
    <isRequired>false</isRequired>
    <constraint/>
    <description/>
    {meta}
  </parameter>"""


class Params:
    def __init__(self, prop: str, propdef: str):
        self.prop = prop
        self.propdef = propdef

    # prop
    def set(self, key: str, value: str):
        line = f"{key}={value}"
        if re.search(r"^" + re.escape(key) + r"=", self.prop, re.M):
            self.prop = re.sub(r"^" + re.escape(key) + r"=.*$", lambda m: line, self.prop, flags=re.M)
        else:
            self.prop = self.prop.rstrip("\n") + "\n" + line + "\n"

    def keys(self) -> list[str]:
        """Parameter names as used in {{…}}: java.util.Properties escapes (`Body\\ Size`) undone.
        (I2050_P, 2026-11-23: names with spaces were reported as unused.)"""
        raw = re.findall(r"^([^#!\s](?:\\.|[^=:\\])*)[=:]", self.prop, re.M)
        return [re.sub(r"\\(.)", r"\1", k) for k in raw]

    @staticmethod
    def _key_re(name: str) -> str:
        """Regex for a key as written in parameters.prop (spaces, ':' and '=' escaped)."""
        return "".join("\\\\" + re.escape(c) if c in " :=" else re.escape(c) for c in name)

    def names(self) -> list[str]:
        return re.findall(r"<name>([^<]*)</name>", self.propdef)

    # both
    def add(self, name: str, value: str, type_: str = "xsd:string", ref: tuple | None = None,
            combobox: bool | None = None):
        """ref = (attribute_category, attribute_id, attribute_uilabel).
        combobox: True/False writes <additionalMetadata><isCombobox>…</isCombobox> (as CPI does
        for dropdown / checkbox fields, e.g. HTTP_Authorization / HTTP_CSRFProtected)."""
        self.set(name, value)
        self.propdef = self.propdef.replace("<param_references/>", "<param_references></param_references>")
        if name not in self.names():
            self.propdef = self.propdef.replace(
                "<param_references>", PARAM_TMPL.format(name=name, type=type_, meta=(
                    "<additionalMetadata/>" if combobox is None else
                    "<additionalMetadata>\n      <isCombobox>%s</isCombobox>\n    </additionalMetadata>"
                    % str(combobox).lower())) + "<param_references>", 1)
        if ref:
            cat, aid, label = ref
            r = (f'<reference attribute_category="{cat}" attribute_id="{aid}" '
                 f'attribute_uilabel="{label}" param_key="{name}"/>')
            if r not in self.propdef:
                self.propdef = self.propdef.replace("</param_references>", r + "</param_references>", 1)

    def remove(self, name: str):
        self.prop = re.sub(r"^" + self._key_re(name) + r"=.*\n?", "", self.prop, flags=re.M)
        self.propdef = re.sub(r"<parameter>\s*<key/>\s*<name>" + re.escape(name) +
                              r"</name>.*?</parameter>", "", self.propdef, flags=re.S)
        self.propdef = re.sub(r'<reference [^>]*param_key="' + re.escape(name) + r'"/>', "", self.propdef)

    def rename(self, old: str, new: str):
        self.prop = re.sub(r"^" + self._key_re(old) + "=", lambda m: new + "=", self.prop, flags=re.M)
        self.propdef = self.propdef.replace(f"<name>{old}</name>", f"<name>{new}</name>")
        self.propdef = self.propdef.replace(f'param_key="{old}"', f'param_key="{new}"')


# ---------------------------------------------------------------------------
# Checks
# ---------------------------------------------------------------------------

# Groovy scripts must stream the body into XML parsers (user, 2026-11-23, CPI script editor warning
# "parse the message body using XmlSlurper without streaming"): parse(message.getBody(java.io.Reader)),
# never parseText(message.getBody(String)) or a body String.
_PARSE_NO_STREAM = re.compile(
    r"(XmlSlurper|XmlParser)\s*\([^)]*\)\s*\.\s*parseText\s*\("
    r"|\.parse\s*\(\s*message\.getBody\s*\(\s*(java\.lang\.)?String\b"
    r"|DocumentBuilder[\w.]*\.parse\s*\(\s*new\s+InputSource\s*\(\s*new\s+StringReader")


def script_parse_errors(files: dict[str, bytes]) -> list[str]:
    """Groovy files that parse XML from the body without streaming."""
    errs = []
    for n, b in files.items():
        if n.endswith(".groovy"):
            for i, line in enumerate(b.decode("utf-8", errors="replace").splitlines(), 1):
                if _PARSE_NO_STREAM.search(line) and not line.lstrip().startswith(("//", "*")):
                    errs.append(f"{n}:{i}: XML parsed without streaming; use "
                                f"parse(message.getBody(java.io.Reader))")
    return errs


def check_iflow(xml: str, prop: str | None = None, propdef: str | None = None) -> list[str]:
    """Return a list of problems (empty = OK)."""
    errs = []
    try:
        root = parse(xml)
    except etree.XMLSyntaxError as e:
        return [f"iflw not well-formed: {e}"]
    plane = root.find(".//bpmndi:BPMNPlane", NS)
    ids = _model_ids(root)
    di_refs = {e.get("bpmnElement") for e in plane}
    for el in plane:
        r = el.get("bpmnElement")
        if r and r not in ids:
            errs.append(f"orphan DI element for {r}")
    shape_of = {s.get("bpmnElement"): s.get("id") for s in plane.findall("bpmndi:BPMNShape", NS)}
    edge_of = {e.get("bpmnElement"): e for e in plane.findall("bpmndi:BPMNEdge", NS)}
    for kind in ("sequenceFlow", "messageFlow"):
        for f in root.iter(_q("bpmn2:" + kind)):
            if f.get("id") not in di_refs:
                errs.append(f"{kind} {f.get('id')} has no BPMNEdge")
                continue
            e = edge_of[f.get("id")]
            if (e.get("sourceElement") != shape_of.get(f.get("sourceRef"))
                    or e.get("targetElement") != shape_of.get(f.get("targetRef"))):
                errs.append(f"{kind} {f.get('id')}: edge ends do not match its source/target")
    for kind in ("task", "serviceTask", "callActivity", "startEvent", "endEvent",
                 "exclusiveGateway", "participant"):
        for el in root.iter(_q("bpmn2:" + kind)):
            if el.get("id") not in di_refs:
                errs.append(f"{kind} {el.get('id')} has no BPMNShape")
    # sequence-flow wiring
    for el, exp_in, exp_out in flow_ref_mismatches(root):
        errs.append(f"{el.get('id')} ({el.get('name')}): incoming/outgoing do not match its flows "
                    f"(expected in={exp_in} out={exp_out})")
    for f in root.iter(_q("bpmn2:sequenceFlow")):
        for end in ("sourceRef", "targetRef"):
            if f.get(end) not in ids:
                errs.append(f"sequenceFlow {f.get('id')} {end} -> missing {f.get(end)}")
    if prop is not None:
        used = set(re.findall(r"\{\{([^}]+)\}\}", xml))
        p = Params(prop, propdef or "")
        keys, names = set(p.keys()), set(p.names())
        for u in sorted(used - keys):
            errs.append(f"{{{{{u}}}}} used but not in parameters.prop")
        for u in sorted(keys - used):
            errs.append(f"parameter {u} in parameters.prop but not used")
        if propdef is not None:
            try:
                etree.fromstring(propdef.encode("utf-8"))
            except etree.XMLSyntaxError as e:
                errs.append(f"propdef not well-formed: {e}")
            for u in sorted(used - names):
                errs.append(f"{{{{{u}}}}} used but not in parameters.propdef")
            for u in sorted(names - used):
                errs.append(f"parameter {u} in propdef but not used")
            for k in sorted(set(re.findall(r'param_key="([^"]+)"', propdef)) - used):
                errs.append(f"param_reference {k} not used")
    return errs


# ---------------------------------------------------------------------------
# SSAB Integration Suite Best Practises (PDF v1.9, L2) - reported as FLAGs
# ---------------------------------------------------------------------------
# Not build failures: existing flows predate some rules. Builds print them so they are
# fixed or confirmed with the user. Section numbers refer to the PDF.

_STEP_KINDS = ("task", "serviceTask", "callActivity", "exclusiveGateway", "parallelGateway")


def _props(el) -> dict:
    """key -> value of the ifl:property children directly under el's extensionElements."""
    out = {}
    ext = el.find("bpmn2:extensionElements", NS)
    if ext is not None:
        for p in ext.findall("ifl:property", NS):
            out[p.findtext("key") or ""] = p.findtext("value") or ""
    return out


def _resolve(value: str, params: dict) -> str:
    m = re.fullmatch(r"\{\{([^}]+)\}\}", value or "")
    return params.get(m.group(1), value) if m else value


def _cm_rows(xml: str) -> list[tuple[str, str, str, str]]:
    """(table, name, type, value) for every Content Modifier header/property row."""
    rows = []
    for table, body in re.findall(r"<key>(headerTable|propertyTable)</key>\s*<value>([^<]*)</value>", xml):
        body = (body.replace("&lt;", "<").replace("&gt;", ">")
                .replace("&apos;", "'").replace("&quot;", '"').replace("&amp;", "&"))
        for row in re.findall(r"<row>(.*?)</row>", body):
            c = dict(re.findall(r"<cell id='([^']+)'>([^<]*)</cell>", row))
            rows.append((table, c.get("Name", ""), c.get("Type", ""), c.get("Value", "")))
    return rows


def best_practice_flags(xml: str, prop: str | None = None) -> list[str]:
    """FLAG messages for the SSAB best-practice rules (PDF v1.9; CLAUDE.md "Best Practises")."""
    flags = []
    root = parse(xml)
    params = {}
    for line in (prop or "").splitlines():
        if "=" in line and not line.startswith("#"):
            k, v = line.split("=", 1)
            params[k.strip()] = v.replace("\\:", ":").strip()
    processes = list(root.iter(_q("bpmn2:process")))
    names = [(p.get("name") or "") for p in processes]

    # A JMS dispatcher (PD address from SSAB_Dispatcher_ReceiverIFlow) gets SAP_* from the parent's
    # headers and has no Main Process in the PDF sample (§3.10.5.4).
    dispatcher = "${header.SSAB_Dispatcher_ReceiverIFlow}" in xml

    # §3.1 Main Process; §3.2 at most 15 steps per process
    if not dispatcher and not any(n.strip().lower() == "main process" for n in names):
        flags.append("§3.1 no local process 'Main Process'")
    for p in processes:
        n = sum(1 for c in p if isinstance(c.tag, str) and etree.QName(c).localname in _STEP_KINDS)
        if n > 15:
            flags.append(f"§3.2 process '{p.get('name')}' has {n} steps (max 15)")

    channels = []
    for mf in root.iter(_q("bpmn2:messageFlow")):
        d = _props(mf)
        channels.append((d.get("ComponentType", ""), d.get("direction", "")))
    jms_rcv = [c for c in channels if c == ("JMS", "Receiver")]
    jdbc = [c for c in channels if c[0] == "JDBC"]

    # §3.7.1.1/2 no * in the sender's Allowed Headers or a receiver's request headers
    for el in root.iter(_q("ifl:property")):
        key = el.findtext("key") or ""
        if re.search(r"allowedHeader|RequestHeaders", key, re.I):
            if _resolve(el.findtext("value") or "", params).strip() == "*":
                msg = f"§3.7.1 '{key}' is * (list only the expected headers)"
                if msg not in flags:
                    flags.append(msg)

    # §3.8 transaction handling
    if jms_rcv and jdbc:
        flags.append("§3.8.1 JMS and JDBC in one iFlow (CPI has no distributed transactions)")
    tx = [(_props(p).get("transactionalHandling", ""), _props(p).get("transactionTimeout", ""))
          for p in processes]
    if len(jms_rcv) > 1 or (jms_rcv and "CamelLoopIndex" in xml):
        if not any(h == "Required for JMS" for h, _ in tx):
            flags.append("§3.8.2 several JMS writes but no process has 'Required for JMS' (timeout 1 min)")
        elif any(h == "Required for JMS" and t != "1" for h, t in tx):
            flags.append("§3.8.2 'Required for JMS' timeout is not 1 min")
    if len(jdbc) > 1 and not any(h == "Required for JDBC" for h, _ in tx):
        flags.append("§3.8.3 several JDBC receivers but no 'Required for JDBC'")

    # §3.9 session handling externalized ('On Integration Flow' by default)
    for m in re.finditer(r"<key>httpSessionHandling</key>\s*<value>([^<]*)</value>", xml):
        if not m.group(1).startswith("{{"):
            flags.append(f"§3.9 session handling '{m.group(1)}' is not externalized")

    # §3.6 mandatory externalized parameters (SAP_Receiver optional: dynamic receivers, user 2026-11-23)
    by_name = {}
    for table, name, typ, value in _cm_rows(xml):
        by_name.setdefault(name, []).append((typ, value))

    def externalized(name):
        return all(v.startswith("{{") or t.lower() == "xpath" for t, v in by_name.get(name, []))

    for name in ("SAP_Sender", "SAP_MessageType"):
        if name not in by_name and not dispatcher:
            flags.append(f"§3.6 header {name} is not set")
        elif not externalized(name):
            flags.append(f"§3.6 {name} is a fixed value, not externalized")
    if "SAP_Receiver" in by_name and not externalized("SAP_Receiver"):
        flags.append("§3.6 SAP_Receiver is a fixed value, not externalized")
    logs = "logPayloadAsAttachment" in xml or "UTIL_LogPayloadAsAttachment" in xml
    for name in ("LogPayload", "LogPayloadSize"):
        if name not in by_name:
            if logs:
                flags.append(f"§3.6 property {name} is not set")
        elif not externalized(name):
            flags.append(f"§3.6 {name} is a fixed value, not externalized")
    if "SAPJMSRetries" in xml and "{{MaxRetries}}" not in xml:
        flags.append("§3.6 SAPJMSRetries check without externalized {{MaxRetries}}")
    if any(v.startswith("{{") for _, v in by_name.get("AttachmentName", [])):
        flags.append("§1.2.1 AttachmentName must not be externalized")

    # §3.3.2 retrigger needs the 'IncomingPayload' attachment
    if logs and any("retrigger" in n.lower() for n in names) and "IncomingPayload" not in xml:
        flags.append("§3.3.2 retrigger flow without an 'IncomingPayload' attachment")
    return flags
