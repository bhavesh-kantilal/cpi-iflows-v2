"""
tools/iflow_add_request_reply.py
Insert the Request-Reply (Send to SmarTeam) + response-logging block into an iFlow ZIP
that currently ends at: Mapping → Set AttachmentName(OutputPayload) → Log Payload → End.

After this script the tail becomes:
  ... → Set AttachmentName(OutputPayload) → Log Payload(output)
      → Send to SmarTeam (ExternalCall/HTTP)
      → Set AttachmentName(SmartTeamResponse)
      → Log Payload(response)
      → End

Usage:
  py -I tools/iflow_add_request_reply.py
"""
import sys, zipfile, io
from lxml import etree
from pathlib import Path

sys.stdout.reconfigure(encoding="utf-8")

# ── namespace constants ────────────────────────────────────────────────────────
B    = "http://www.omg.org/spec/BPMN/20100524/MODEL"
DI   = "http://www.omg.org/spec/BPMN/20100524/DI"
DC   = "http://www.omg.org/spec/DD/20100524/DC"
DIPT = "http://www.omg.org/spec/DD/20100524/DI"
IFL  = "http:///com.sap.ifl.model/Ifl.xsd"
XSI  = "http://www.w3.org/2001/XMLSchema-instance"

NS = {
    "bpmn2":  B,
    "bpmndi": DI,
    "dc":     DC,
    "di":     DIPT,
    "ifl":    IFL,
    "xsi":    XSI,
}

IFLW_ENTRY = (
    "src/main/resources/scenarioflows/integrationflow/"
    "I0579_CostCentreGroupHierarchyReplication_FSAP_MSAP_JMSToSOAP.iflw"
)

SMARTEAM_URL = "http://smarteam-test.ssab.com:443/SmarTeam.InboundService/inbound"


# ── helpers ────────────────────────────────────────────────────────────────────
def ifl_prop(key: str, val: str) -> etree._Element:
    """Return <ifl:property><key>k</key><value>v</value></ifl:property>."""
    p = etree.Element(f"{{{IFL}}}property")
    etree.SubElement(p, "key").text = key
    etree.SubElement(p, "value").text = val
    return p


def add_shape(plane, elem_id: str, x: float, y: float,
              w: float = 100.0, h: float = 60.0) -> etree._Element:
    shape = etree.SubElement(plane, f"{{{DI}}}BPMNShape",
                              bpmnElement=elem_id,
                              id=f"BPMNShape_{elem_id}")
    etree.SubElement(shape, f"{{{DC}}}Bounds",
                     height=f"{h}", width=f"{w}", x=f"{x}", y=f"{y}")
    return shape


def add_edge(plane, sf_id: str, src_id: str, tgt_id: str,
             x1: float, y1: float, x2: float, y2: float) -> etree._Element:
    edge = etree.SubElement(plane, f"{{{DI}}}BPMNEdge",
                             bpmnElement=sf_id,
                             id=f"BPMNEdge_{sf_id}",
                             sourceElement=f"BPMNShape_{src_id}",
                             targetElement=f"BPMNShape_{tgt_id}")
    for x, y in [(x1, y1), (x2, y2)]:
        wp = etree.SubElement(edge, f"{{{DIPT}}}waypoint",
                               x=f"{x}", y=f"{y}")
        wp.set(f"{{{XSI}}}type", "dc:Point")
    return edge


# ── main transform ─────────────────────────────────────────────────────────────
def process_iflow(zip_path: Path, id_prefix: str) -> None:
    print(f"\n── Processing {zip_path.name} (prefix={id_prefix}) ──")

    # Read ZIP contents
    with zipfile.ZipFile(zip_path, "r") as zin:
        infos = {info.filename: info for info in zin.infolist()}
        contents = {name: zin.read(name) for name in zin.namelist()}

    # Parse iflw
    raw = contents[IFLW_ENTRY]
    root: etree._Element = etree.fromstring(raw)

    # ── Locate Process_28 ──────────────────────────────────────────────────────
    p28 = root.find(f'{{{B}}}process[@id="Process_28"]')
    assert p28 is not None, "Process_28 not found"

    # EndEvent in Process_28
    end_ev = p28.find(f"{{{B}}}endEvent")
    assert end_ev is not None, "endEvent not found in Process_28"
    end_ev_id = end_ev.get("id")

    # The SequenceFlow whose targetRef is EndEvent
    sf_to_end = p28.find(f'{{{B}}}sequenceFlow[@targetRef="{end_ev_id}"]')
    assert sf_to_end is not None, f"No SF targeting {end_ev_id}"
    sf_to_end_id = sf_to_end.get("id")
    last_log_id  = sf_to_end.get("sourceRef")   # the last Log Payload callActivity

    # ── New element IDs ────────────────────────────────────────────────────────
    p = id_prefix
    new_part_id   = f"{p}_Participant_SmarTeam"
    new_mf_id     = f"{p}_MessageFlow_HTTP"
    new_st_id     = f"{p}_ServiceTask_Send"
    new_sf_st_id  = f"{p}_SF_toSend"      # redirect: last Log Payload → ServiceTask
    new_sf_att_id = f"{p}_SF_toSetAtt"    # ServiceTask → Set AttachmentName
    new_sf_log_id = f"{p}_SF_toLogResp"   # Set AttachmentName → Log Payload (resp)
    new_sf_end_id = f"{p}_SF_toEnd"       # Log Payload (resp) → EndEvent
    new_att_id    = f"{p}_CA_SetAtt"
    new_logr_id   = f"{p}_CA_LogResp"

    # ── Rewire existing SF (last Log Payload → End) → now points to ServiceTask ──
    sf_to_end.set("targetRef", new_st_id)
    sf_to_end.set("id", new_sf_st_id)         # give it a cleaner ID
    # Update EndEvent's <incoming> and last Log Payload's <outgoing>
    end_ev.find(f"{{{B}}}incoming").text = new_sf_end_id
    last_log = p28.find(f'{{{B}}}callActivity[@id="{last_log_id}"]')
    last_log.find(f"{{{B}}}outgoing").text = new_sf_st_id

    # ── New elements in Process_28 ─────────────────────────────────────────────

    # 1. ServiceTask — Send to SmarTeam
    st = etree.SubElement(p28, f"{{{B}}}serviceTask",
                           id=new_st_id, name="Send to SmarTeam")
    ext = etree.SubElement(st, f"{{{B}}}extensionElements")
    for k, v in [("componentVersion", "1.0"),
                 ("activityType", "ExternalCall"),
                 ("cmdVariantUri",
                  "ctype::FlowstepVariant/cname::ExternalCall/version::1.0.4")]:
        ext.append(ifl_prop(k, v))
    etree.SubElement(st, f"{{{B}}}incoming").text = new_sf_st_id
    etree.SubElement(st, f"{{{B}}}outgoing").text  = new_sf_att_id

    # 2. SF: ServiceTask → Set AttachmentName (SmartTeamResponse)
    etree.SubElement(p28, f"{{{B}}}sequenceFlow",
                     id=new_sf_att_id, sourceRef=new_st_id, targetRef=new_att_id)

    # 3. CallActivity — Set AttachmentName = SmartTeamResponse
    prop_table = (
        "<row>"
        "<cell id='Action'>Create</cell>"
        "<cell id='Type'>constant</cell>"
        "<cell id='Value'>SmartTeamResponse</cell>"
        "<cell id='Default'></cell>"
        "<cell id='Name'>AttachmentName</cell>"
        "<cell id='Datatype'></cell>"
        "</row>"
    )
    ca_att = etree.SubElement(p28, f"{{{B}}}callActivity",
                               id=new_att_id, name="Set AttachmentName")
    ext = etree.SubElement(ca_att, f"{{{B}}}extensionElements")
    for k, v in [("bodyType", "constant"),
                 ("propertyTable", prop_table),
                 ("headerTable", ""),
                 ("wrapContent", ""),
                 ("componentVersion", "1.6"),
                 ("activityType", "Enricher"),
                 ("cmdVariantUri",
                  "ctype::FlowstepVariant/cname::Enricher/version::1.6.5")]:
        ext.append(ifl_prop(k, v))
    etree.SubElement(ca_att, f"{{{B}}}incoming").text = new_sf_att_id
    etree.SubElement(ca_att, f"{{{B}}}outgoing").text  = new_sf_log_id

    # 4. SF: Set AttachmentName → Log Payload (response)
    etree.SubElement(p28, f"{{{B}}}sequenceFlow",
                     id=new_sf_log_id, sourceRef=new_att_id, targetRef=new_logr_id)

    # 5. CallActivity — Log Payload (response), calls Process_12
    ca_log = etree.SubElement(p28, f"{{{B}}}callActivity",
                               id=new_logr_id, name="Log Payload")
    ext = etree.SubElement(ca_log, f"{{{B}}}extensionElements")
    for k, v in [("processId", "Process_12"),
                 ("componentVersion", "1.0"),
                 ("activityType", "ProcessCallElement"),
                 ("cmdVariantUri",
                  "ctype::FlowstepVariant/cname::NonLoopingProcess/version::1.0.4"),
                 ("subActivityType", "NonLoopingProcess")]:
        ext.append(ifl_prop(k, v))
    etree.SubElement(ca_log, f"{{{B}}}incoming").text = new_sf_log_id
    etree.SubElement(ca_log, f"{{{B}}}outgoing").text  = new_sf_end_id

    # 6. SF: Log Payload (response) → EndEvent
    etree.SubElement(p28, f"{{{B}}}sequenceFlow",
                     id=new_sf_end_id, sourceRef=new_logr_id, targetRef=end_ev_id)

    # ── Add SmarTeam participant + HTTP channel to collaboration ───────────────
    collab = root.find(f"{{{B}}}collaboration")

    part = etree.SubElement(collab, f"{{{B}}}participant",
                             id=new_part_id, name="SmarTeam")
    part.set(f"{{{IFL}}}type", "EndpointRecevier")
    ext = etree.SubElement(part, f"{{{B}}}extensionElements")
    ext.append(ifl_prop("ifl:type", "EndpointRecevier"))

    mf = etree.SubElement(collab, f"{{{B}}}messageFlow",
                           id=new_mf_id, name="HTTP",
                           sourceRef=new_st_id, targetRef=new_part_id)
    ext = etree.SubElement(mf, f"{{{B}}}extensionElements")
    for k, v in [
        ("apiName", ""), ("Description", ""), ("methodSourceExpression", ""),
        ("apiArtifactType", ""), ("providerAuth", ""), ("retryOnExceptionsTable", ""),
        ("ComponentNS", "sap"), ("privateKeyAlias", ""), ("httpMethod", "POST"),
        ("apiprovider_location_id", ""), ("allowedResponseHeaders", "*"),
        ("Name", "HTTP"), ("internetProxyType", ""), ("TransportProtocolVersion", "1.22.1"),
        ("retryOnException", "false"), ("proxyPort", ""), ("ComponentSWCVName", "external"),
        ("streaming", "false"), ("enableMPLAttachments", "true"),
        ("pooledConnectionIdleTimeout", "300000"), ("httpAddressQuery", ""),
        ("httpRequestTimeout", "60000"), ("ComponentSWCVId", "1.22.1"),
        ("providerName", ""), ("allowedRequestHeaders", "traceparent"),
        ("MessageProtocol", "None"), ("direction", "Receiver"), ("ComponentType", "HTTP"),
        ("httpShouldSendBody", "false"), ("throwExceptionOnFailure", "true"),
        ("proxyType", "sapcc"), ("componentVersion", "1.22"), ("retryIteration", "1"),
        ("proxyHost", ""), ("providerUrl", ""), ("retryOnConnectionFailure", "false"),
        ("system", "SmarTeam"), ("authenticationMethod", "None"), ("locationID", ""),
        ("retryInterval", "5"), ("TransportProtocol", "HTTP"),
        ("cmdVariantUri",
         "ctype::AdapterVariant/cname::sap:HTTP/tp::HTTP/mp::None"
         "/direction::Receiver/version::1.22.1"),
        ("httpErrorResponseCodes", ""), ("credentialName", ""), ("apiDisplayName", ""),
        ("MessageProtocolVersion", "1.22.1"), ("providerRelativeUrl", ""),
        ("httpAddressWithoutQuery", SMARTEAM_URL),
    ]:
        ext.append(ifl_prop(k, v))

    # ── BPMNDiagram updates ────────────────────────────────────────────────────
    plane = root.find(f".//{{{DI}}}BPMNPlane")

    # Get current EndEvent shape position
    end_shape  = plane.find(f'.//{{{DI}}}BPMNShape[@bpmnElement="{end_ev_id}"]')
    end_bounds = end_shape.find(f"{{{DC}}}Bounds")
    end_x = float(end_bounds.get("x"))
    end_y = float(end_bounds.get("y"))

    # Get last Log Payload shape position
    log_shape  = plane.find(f'.//{{{DI}}}BPMNShape[@bpmnElement="{last_log_id}"]')
    log_bounds = log_shape.find(f"{{{DC}}}Bounds")
    log_x = float(log_bounds.get("x"))
    step_y = float(log_bounds.get("y"))   # same row y for all Main Process steps
    mid_y  = step_y + 30.0                # vertical centre of 60px-tall shapes

    # New step x positions (160px pitch matching the reference iFlow)
    x_st  = log_x + 160.0   # ServiceTask
    x_att = log_x + 320.0   # Set AttachmentName
    x_log = log_x + 480.0   # Log Payload (response)
    x_end = log_x + 640.0   # EndEvent (shifted right)

    # Move existing EndEvent shape
    end_bounds.set("x", f"{x_end}")

    # Update the BPMNEdge for the existing SF (was → EndEvent, now → ServiceTask).
    # sf_to_end_id holds the original id before we renamed the SF element above.
    old_edge = plane.find(
        f'.//{{{DI}}}BPMNEdge[@bpmnElement="{sf_to_end_id}"]')
    if old_edge is None:
        # Fallback: find by sourceElement (last Log Payload shape)
        for edge in plane.findall(f".//{{{DI}}}BPMNEdge"):
            if edge.get("sourceElement") == f"BPMNShape_{last_log_id}":
                old_edge = edge
                break

    if old_edge is not None:
        old_edge.set("bpmnElement", new_sf_st_id)
        old_edge.set("id", f"BPMNEdge_{new_sf_st_id}")
        old_edge.set("targetElement", f"BPMNShape_{new_st_id}")
        wps = old_edge.findall(f"{{{DIPT}}}waypoint")
        if len(wps) >= 2:
            wps[-1].set("x", f"{x_st}")
            wps[-1].set("y", f"{mid_y}")
    else:
        print("  WARN: could not find BPMNEdge for old SF → will add new edge")
        add_edge(plane, new_sf_st_id, last_log_id, new_st_id,
                 log_x + 100.0, mid_y, x_st, mid_y)

    # Add new shapes
    add_shape(plane, new_st_id,  x_st,  step_y)
    add_shape(plane, new_att_id, x_att, step_y)
    add_shape(plane, new_logr_id, x_log, step_y)
    # SmarTeam participant box (below ServiceTask, same x as reference pattern)
    add_shape(plane, new_part_id, x_st, step_y + 187.0, w=100.0, h=140.0)

    # Add new edges
    add_edge(plane, new_sf_att_id, new_st_id,  new_att_id,
             x_st  + 100.0, mid_y, x_att,       mid_y)
    add_edge(plane, new_sf_log_id, new_att_id, new_logr_id,
             x_att + 100.0, mid_y, x_log,        mid_y)
    add_edge(plane, new_sf_end_id, new_logr_id, end_ev_id,
             x_log + 100.0, mid_y, x_end + 16.0, mid_y)   # +16 = centre of 32px EndEvent

    # MessageFlow edge: ServiceTask ↓ SmarTeam participant
    mf_edge = etree.SubElement(plane, f"{{{DI}}}BPMNEdge",
                                bpmnElement=new_mf_id,
                                id=f"BPMNEdge_{new_mf_id}",
                                sourceElement=f"BPMNShape_{new_st_id}",
                                targetElement=f"BPMNShape_{new_part_id}")
    for x_, y_ in [(x_st + 50.0, step_y + 60.0), (x_st + 50.0, step_y + 187.0)]:
        wp = etree.SubElement(mf_edge, f"{{{DIPT}}}waypoint", x=f"{x_}", y=f"{y_}")
        wp.set(f"{{{XSI}}}type", "dc:Point")

    # Widen Participant_Process_28 lane to cover new steps
    p28_shape = plane.find(
        f'.//{{{DI}}}BPMNShape[@bpmnElement="Participant_Process_28"]')
    if p28_shape is not None:
        p28_b = p28_shape.find(f"{{{DC}}}Bounds")
        old_w = float(p28_b.get("width"))
        p28_b.set("width", f"{old_w + 480.0}")

    # ── Serialize ──────────────────────────────────────────────────────────────
    new_iflw = etree.tostring(root, xml_declaration=True,
                               encoding="UTF-8", pretty_print=True)

    contents[IFLW_ENTRY] = new_iflw

    # Re-zip (preserve all other files byte-for-byte)
    buf = io.BytesIO()
    with zipfile.ZipFile(buf, "w", zipfile.ZIP_DEFLATED) as zout:
        for name, data in contents.items():
            zout.writestr(infos[name], data)
    zip_path.write_bytes(buf.getvalue())
    print(f"  Written: {zip_path}")
    print(f"  New elements: {new_st_id}, {new_att_id}, {new_logr_id}")
    print(f"  SmarTeam channel: {new_mf_id} → {SMARTEAM_URL}")


# ── version / description stamping ────────────────────────────────────────────
def _next_version(current: str) -> str:
    """Increment the patch component: '1.0.1' → '1.0.2', '1.0.2' → '1.0.3'."""
    parts = current.strip().split(".")
    parts[-1] = str(int(parts[-1]) + 1)
    return ".".join(parts)


def set_iflow_version(zip_path: Path, description: str) -> str:
    """
    Read Bundle-Version from MANIFEST.MF, increment the patch, write it back
    together with the description in metainfo.prop.  Returns the new version string.
    """
    with zipfile.ZipFile(zip_path, "r") as zin:
        infos    = {info.filename: info for info in zin.infolist()}
        contents = {name: zin.read(name) for name in zin.namelist()}

    # -- MANIFEST.MF: bump Bundle-Version --
    manifest_raw = contents["META-INF/MANIFEST.MF"].decode("utf-8")
    old_ver = ""
    new_lines = []
    for line in manifest_raw.splitlines(keepends=True):
        if line.startswith("Bundle-Version:"):
            old_ver = line.split(":", 1)[1].strip()
            new_ver = _next_version(old_ver)
            new_lines.append(f"Bundle-Version: {new_ver}\n")
        else:
            new_lines.append(line)
    contents["META-INF/MANIFEST.MF"] = "".join(new_lines).encode("utf-8")

    # -- metainfo.prop: set description --
    prop_raw = contents["metainfo.prop"].decode("utf-8")
    prop_lines = []
    for line in prop_raw.splitlines(keepends=True):
        if line.startswith("description="):
            prop_lines.append(f"description={description}\n")
        else:
            prop_lines.append(line)
    contents["metainfo.prop"] = "".join(prop_lines).encode("utf-8")

    # -- re-zip --
    buf = io.BytesIO()
    with zipfile.ZipFile(buf, "w", zipfile.ZIP_DEFLATED) as zout:
        for name, data in contents.items():
            zout.writestr(infos[name], data)
    zip_path.write_bytes(buf.getvalue())
    print(f"  {zip_path.name}: {old_ver} → {new_ver}  |  description set")
    return new_ver


# ── run ────────────────────────────────────────────────────────────────────────
# To add Request-Reply steps to a fresh iFlow, call process_iflow() first:
#   process_iflow(zip_path, id_prefix)
# Then stamp the version:
#   set_iflow_version(zip_path, description)

BASE = Path(r"C:\work\cpi-mappings\iflowdevelopment")
DESCRIPTION = "Added step for send to smarteam and payload logging"

set_iflow_version(BASE / "I2049_MaterialBOM_MSAP_SmarTeam_PDToHTTP.zip", DESCRIPTION)
set_iflow_version(BASE / "I2050_MaintananceBOM_MSAP_SmarTeam_PDToHTTP.zip", DESCRIPTION)

print("\nDone. Import each ZIP into CPI to verify version and description.")
