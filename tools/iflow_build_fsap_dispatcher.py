#!/usr/bin/env python3
"""
iFlow Builder: FSAP Controlling Masterdata Dispatcher Migration
=================================================================
Builds 7 iFlows for the FSAP -> Medius dispatcher migration (v1.0 scope: Medius only).

Outputs:
  iflows/I0710_P_JMSDispatcher_Medius/build/           new Medius dispatcher
  iflows/I0539_P_CostCenter_FSAP_SOAPToJMS/build/      updated parent (arr_* loop)
  iflows/I0541_P_InternalOrder_FSAP_SOAPToJMS/build/   updated parent + IDoc splitter
  iflows/I0545_P_WBSElement_FSAP_SOAPToJMS/build/      updated parent
  iflows/I0539_CostCenter_FSAP_Medius_PDToREST/build/  new child (ProcessDirect entry)
  iflows/I0541_InternalOrder_FSAP_Medius_PDToREST/build/ new child
  iflows/I0545_WBSElement_FSAP_Medius_PDToREST/build/   new child

Design:
  Every build function is self-contained. Add new functions here as iFlow work grows.
  read_from_package() / create_iflow_zip() / update_manifest() are general helpers
  reusable for any iFlow ZIP work.

References used:
  _reference/iflows/I0701_P_JMSDispatcher_MSAP_PlantMaintenance.zip  (dispatcher template)
  _reference/iflows/FSAP_Controlling_MasterData.zip                   (FSAP parents + children)
  _reference/iflows/I2018_P_Material_MSAP_SOAPToJMS.zip               (new parent loop pattern)
"""
import io
import os
import re
import sys
import zipfile

sys.stdout.reconfigure(encoding="utf-8")

REPO = os.path.normpath(os.path.join(os.path.dirname(__file__), ".."))
REF_IFLOWS = os.path.join(REPO, "_reference", "iflows")
IFLOWS_OUT = os.path.join(REPO, "iflows")


# ---------------------------------------------------------------------------
# Generic helpers
# ---------------------------------------------------------------------------

def read_from_package(pkg_zip_path: str, bundle_name: str) -> dict[str, bytes]:
    """Read one iFlow from a CPI package ZIP (hash-named *_content entries).
    Returns {zip_entry_path: bytes} for all files inside that iFlow ZIP."""
    outer = zipfile.ZipFile(pkg_zip_path)
    for entry in outer.namelist():
        if not entry.endswith("_content"):
            continue
        data = outer.read(entry)
        inner = zipfile.ZipFile(io.BytesIO(data))
        try:
            mf = inner.read("META-INF/MANIFEST.MF").decode("utf-8")
        except KeyError:
            continue
        for line in mf.splitlines():
            if line.startswith("Bundle-Name:") and bundle_name in line:
                return {n: inner.read(n) for n in inner.namelist()}
    raise FileNotFoundError(f"Bundle '{bundle_name}' not found in {pkg_zip_path}")


def read_standalone_zip(zip_path: str) -> dict[str, bytes]:
    """Read a standalone iFlow ZIP into {path: bytes}."""
    z = zipfile.ZipFile(zip_path)
    return {n: z.read(n) for n in z.namelist()}


def create_iflow_zip(out_path: str, files: dict[str, bytes]) -> None:
    """Write an iFlow ZIP from a dict. Creates parent dirs if needed."""
    os.makedirs(os.path.dirname(out_path), exist_ok=True)
    with zipfile.ZipFile(out_path, "w", zipfile.ZIP_DEFLATED) as z:
        for name, data in files.items():
            z.writestr(name, data)


def update_manifest(mf_bytes: bytes, name: str, version: str) -> bytes:
    """Replace Bundle-Name, Bundle-SymbolicName, Origin-Bundle-* and Bundle-Version."""
    text = mf_bytes.decode("utf-8")
    # Collect long lines (MANIFEST wraps at 72 chars with space continuation)
    # Simple approach: replace key: value lines (single line values only)
    def _replace_key(t: str, key: str, val: str) -> str:
        return re.sub(
            r"^(" + re.escape(key) + r":)[ \t]*.*$",
            r"\1 " + val,
            t,
            flags=re.MULTILINE,
        )
    text = _replace_key(text, "Bundle-Name", name)
    text = _replace_key(text, "Bundle-SymbolicName", name)
    text = _replace_key(text, "Origin-Bundle-Name", name)
    text = _replace_key(text, "Origin-Bundle-SymbolicName", name)
    text = _replace_key(text, "Bundle-Version", version)
    return text.encode("utf-8")


def set_param(prop_text: str, key: str, value: str) -> str:
    """Set/replace a key=value line in a .prop file."""
    if re.search(r"^" + re.escape(key) + r"=", prop_text, re.MULTILINE):
        return re.sub(
            r"^" + re.escape(key) + r"=.*$",
            key + "=" + value,
            prop_text,
            flags=re.MULTILINE,
        )
    return prop_text + "\n" + key + "=" + value


def remove_param(prop_text: str, key: str) -> str:
    """Remove a key=... line from a .prop file."""
    return re.sub(
        r"^" + re.escape(key) + r"=.*\n?",
        "",
        prop_text,
        flags=re.MULTILINE,
    )


def iflow_xml_name(files: dict[str, bytes]) -> str:
    """Return the .iflw entry path from a files dict."""
    for name in files:
        if name.endswith(".iflw"):
            return name
    raise KeyError("No .iflw found")


def rename_iflw(files: dict[str, bytes], old_name: str, new_name: str) -> dict[str, bytes]:
    """Rename the .iflw entry."""
    old_path = None
    for n in files:
        if n.endswith(old_name + ".iflw") or n.endswith(".iflw"):
            if old_path is None or old_name in n:
                old_path = n
    if old_path is None:
        raise KeyError("iflw not found")
    new_path = os.path.dirname(old_path) + "/" + new_name + ".iflw"
    files[new_path] = files.pop(old_path)
    return files


def make_output_dir(iflow_name: str) -> str:
    """Create iflows/<name>/build/ and return the build dir path."""
    build_dir = os.path.join(IFLOWS_OUT, iflow_name, "build")
    os.makedirs(build_dir, exist_ok=True)
    input_dir = os.path.join(IFLOWS_OUT, iflow_name, "input")
    os.makedirs(input_dir, exist_ok=True)
    return build_dir


# ---------------------------------------------------------------------------
# BPMN2 / iflw XML helpers
# ---------------------------------------------------------------------------

def iflw_replace_all(xml: str, old: str, new: str) -> str:
    """Simple string replacement throughout the iflw XML."""
    return xml.replace(old, new)


# --- New Process_46 body (Iterating Splitter inner subprocess) ---
# Replaces the old custom-loop Process_46 (SetQueueNameHeader / RestorePayload /
# AddQueueIndex) with the new pattern: Get Current Index Receiver -> Send.
# IDs for the inner steps are fixed to match I2018_P (Process_100 uses 101-111).
# The existing Send step (ServiceTask_8075) and its JMS message flow are kept;
# only the Process_46 body elements change.
NEW_PROCESS_46_BODY = """\
        <bpmn2:startEvent id="StartEvent_47" name="Start">
            <bpmn2:extensionElements>
                <ifl:property>
                    <key>cmdVariantUri</key>
                    <value>ctype::FlowstepVariant/cname::StartEvent</value>
                </ifl:property>
                <ifl:property>
                    <key>activityType</key>
                    <value>StartEvent</value>
                </ifl:property>
            </bpmn2:extensionElements>
            <bpmn2:outgoing>SequenceFlow_P46_1</bpmn2:outgoing>
        </bpmn2:startEvent>
        <bpmn2:callActivity id="CallActivity_GetCurrentReceiver" name="Get Current Index Receiver">
            <bpmn2:extensionElements>
                <ifl:property>
                    <key>bodyType</key>
                    <value>expression</value>
                </ifl:property>
                <ifl:property>
                    <key>propertyTable</key>
                    <value>&lt;row&gt;&lt;cell id='Action'&gt;Create&lt;/cell&gt;&lt;cell id='Type'&gt;expression&lt;/cell&gt;&lt;cell id='Value'&gt;${property.arr_receiversQueueList[${property.CamelLoopIndex}]}&lt;/cell&gt;&lt;cell id='Default'&gt;&lt;/cell&gt;&lt;cell id='Name'&gt;QueueName&lt;/cell&gt;&lt;cell id='Datatype'&gt;String&lt;/cell&gt;&lt;/row&gt;</value>
                </ifl:property>
                <ifl:property>
                    <key>headerTable</key>
                    <value>&lt;row&gt;&lt;cell id='Action'&gt;Create&lt;/cell&gt;&lt;cell id='Type'&gt;expression&lt;/cell&gt;&lt;cell id='Value'&gt;${property.arr_receiversIFlowList[${property.CamelLoopIndex}]}&lt;/cell&gt;&lt;cell id='Default'&gt;&lt;/cell&gt;&lt;cell id='Name'&gt;SSAB_Dispatcher_ReceiverIFlow&lt;/cell&gt;&lt;cell id='Datatype'&gt;String&lt;/cell&gt;&lt;/row&gt;&lt;row&gt;&lt;cell id='Action'&gt;Create&lt;/cell&gt;&lt;cell id='Type'&gt;expression&lt;/cell&gt;&lt;cell id='Value'&gt;${header.SSAB_Dispatcher_ReceiverIFlow.split(&amp;apos;_&amp;apos;)[0]}&lt;/cell&gt;&lt;cell id='Default'&gt;&lt;/cell&gt;&lt;cell id='Name'&gt;SAP_MessageProcessingLogCustomStatus&lt;/cell&gt;&lt;cell id='Datatype'&gt;String&lt;/cell&gt;&lt;/row&gt;</value>
                </ifl:property>
                <ifl:property>
                    <key>wrapContent</key>
                    <value/>
                </ifl:property>
                <ifl:property>
                    <key>componentVersion</key>
                    <value>1.6</value>
                </ifl:property>
                <ifl:property>
                    <key>activityType</key>
                    <value>Enricher</value>
                </ifl:property>
                <ifl:property>
                    <key>cmdVariantUri</key>
                    <value>ctype::FlowstepVariant/cname::Enricher/version::1.6.3</value>
                </ifl:property>
            </bpmn2:extensionElements>
            <bpmn2:incoming>SequenceFlow_P46_1</bpmn2:incoming>
            <bpmn2:outgoing>SequenceFlow_P46_2</bpmn2:outgoing>
        </bpmn2:callActivity>
        <bpmn2:serviceTask id="ServiceTask_8075" name="Send">
            <bpmn2:extensionElements>
                <ifl:property>
                    <key>componentVersion</key>
                    <value>1.0</value>
                </ifl:property>
                <ifl:property>
                    <key>activityType</key>
                    <value>Send</value>
                </ifl:property>
                <ifl:property>
                    <key>cmdVariantUri</key>
                    <value>ctype::FlowstepVariant/cname::Send/version::1.0.4</value>
                </ifl:property>
            </bpmn2:extensionElements>
            <bpmn2:incoming>SequenceFlow_P46_2</bpmn2:incoming>
            <bpmn2:outgoing>SequenceFlow_P46_3</bpmn2:outgoing>
        </bpmn2:serviceTask>
        <bpmn2:endEvent id="EndEvent_48" name="End">
            <bpmn2:extensionElements>
                <ifl:property>
                    <key>cmdVariantUri</key>
                    <value>ctype::FlowstepVariant/cname::EndEvent</value>
                </ifl:property>
                <ifl:property>
                    <key>activityType</key>
                    <value>EndEvent</value>
                </ifl:property>
            </bpmn2:extensionElements>
            <bpmn2:incoming>SequenceFlow_P46_3</bpmn2:incoming>
        </bpmn2:endEvent>
        <bpmn2:sequenceFlow id="SequenceFlow_P46_1" sourceRef="StartEvent_47" targetRef="CallActivity_GetCurrentReceiver"/>
        <bpmn2:sequenceFlow id="SequenceFlow_P46_2" sourceRef="CallActivity_GetCurrentReceiver" targetRef="ServiceTask_8075"/>
        <bpmn2:sequenceFlow id="SequenceFlow_P46_3" sourceRef="ServiceTask_8075" targetRef="EndEvent_48"/>
"""

# --- Internal Order splitter step (I0541_P only) ---
# Insert after Set Monitoring Identifiers, before Log Payload.
# References namespace n0 = http://sap.com/xi/SAPGlobal20/Global (already in collaboration).
IO_SPLITTER_CALLACTIVITY = """\
        <bpmn2:callActivity id="CallActivity_IOSplitter" name="Internal Order Splitter">
            <bpmn2:extensionElements>
                <ifl:property>
                    <key>exprType</key>
                    <value>XPath</value>
                </ifl:property>
                <ifl:property>
                    <key>Streaming</key>
                    <value>true</value>
                </ifl:property>
                <ifl:property>
                    <key>StopOnExecution</key>
                    <value>false</value>
                </ifl:property>
                <ifl:property>
                    <key>SplitterThreads</key>
                    <value>10</value>
                </ifl:property>
                <ifl:property>
                    <key>splitExprValue</key>
                    <value>/n0:InternalOrderBulkReplicateRequest/InternalOrderReplicationRequest</value>
                </ifl:property>
                <ifl:property>
                    <key>ParallelProcessing</key>
                    <value>false</value>
                </ifl:property>
                <ifl:property>
                    <key>componentVersion</key>
                    <value>1.6</value>
                </ifl:property>
                <ifl:property>
                    <key>activityType</key>
                    <value>Splitter</value>
                </ifl:property>
                <ifl:property>
                    <key>cmdVariantUri</key>
                    <value>ctype::FlowstepVariant/cname::GeneralSplitter/version::1.6.0</value>
                </ifl:property>
                <ifl:property>
                    <key>grouping</key>
                    <value/>
                </ifl:property>
                <ifl:property>
                    <key>splitType</key>
                    <value>GeneralSplitter</value>
                </ifl:property>
                <ifl:property>
                    <key>timeOut</key>
                    <value>300</value>
                </ifl:property>
            </bpmn2:extensionElements>
            <bpmn2:incoming>SequenceFlow_IOSplit_in</bpmn2:incoming>
            <bpmn2:outgoing>SequenceFlow_IOSplit_out</bpmn2:outgoing>
        </bpmn2:callActivity>
"""


def apply_new_loop_to_parent_iflw(xml: str, with_io_splitter: bool = False) -> str:
    """Apply all iflw XML changes needed for the new arr_* Iterating Splitter pattern:
      - Replace Process_46 body
      - Update loop condition (QUEUE_INDEX/QUEUE_LIST_SIZE -> CamelLoopIndex/arr_receiversLastIndex)
      - Update gateway condition for 'Receivers Exist?'
      - Remove 'Set Receiver Determination Identifiers' step + re-wire sequence flow
      - Remove IO_QUEUES row from 'Set Monitoring Identifiers'
      - Fix JMS QueueName_outbound: ${header.QueueName} -> ${property.QueueName}
      - Optionally insert IO splitter step (I0541_P)
    """

    # 1. Replace Process_46 body (between its extensionElements and the closing tag)
    p46_start = xml.find('<bpmn2:process id="Process_46" name="Send to Receivers">')
    if p46_start < 0:
        raise ValueError("Process_46 not found")
    # Find the extensionElements closing for Process_46
    ext_end = xml.find("</bpmn2:extensionElements>", p46_start)
    ext_end += len("</bpmn2:extensionElements>")
    p46_end = xml.find("</bpmn2:process>", ext_end) + len("</bpmn2:process>")
    old_p46 = xml[p46_start:p46_end]
    # Build new Process_46
    p46_header = xml[p46_start:ext_end]
    new_p46 = p46_header + "\n" + NEW_PROCESS_46_BODY + "    </bpmn2:process>"
    xml = xml[:p46_start] + new_p46 + xml[p46_end:]

    # 2. Update loop condition in Process_15
    xml = xml.replace(
        "${property.QUEUE_INDEX} &lt; ${property.QUEUE_LIST_SIZE}",
        "${property.CamelLoopIndex} &lt; ${property.arr_receiversLastIndex}",
    )

    # 3. Update gateway 'Yes' condition (Receivers Exist?)
    xml = xml.replace(
        "${property.QUEUE_LIST_SIZE} &gt; '0'",
        "${property.arr_receiversLastIndex} &gt;= '0'",
    )

    # 4. Remove 'Set Receiver Determination Identifiers' step (CallActivity_20)
    #    and rewire SequenceFlow_29 target from CallActivity_20 to CallActivity_21
    # Remove the callActivity element
    ca20_start = xml.find('<bpmn2:callActivity id="CallActivity_20"')
    if ca20_start >= 0:
        ca20_end = xml.find("</bpmn2:callActivity>", ca20_start) + len("</bpmn2:callActivity>")
        xml = xml[:ca20_start] + xml[ca20_end:]
    # Rewire: SequenceFlow_29 target was CallActivity_20, change to CallActivity_21
    xml = xml.replace(
        'id="SequenceFlow_29" sourceRef="CallActivity_19" targetRef="CallActivity_20"',
        'id="SequenceFlow_29" sourceRef="CallActivity_19" targetRef="CallActivity_21"',
    )
    # Remove the orphaned SequenceFlow_30 (CallActivity_20 -> CallActivity_21)
    sf30_pat = re.compile(
        r'<bpmn2:sequenceFlow id="SequenceFlow_30"[^/]*/>\s*', re.DOTALL
    )
    xml = sf30_pat.sub("", xml)

    # 5. Remove IO_QUEUES row from Set Monitoring Identifiers (CallActivity_19)
    #    The row looks like: ...Create...constant...{{P_IO_QUEUES}}...IO_QUEUES...
    xml = re.sub(
        r"&lt;row&gt;&lt;cell id='Action'&gt;Create&lt;/cell&gt;&lt;cell id='Type'&gt;"
        r"constant&lt;/cell&gt;&lt;cell id='Value'&gt;\{\{P_IO_QUEUES\}\}&lt;/cell&gt;"
        r"&lt;cell id='Default'&gt;&lt;/cell&gt;&lt;cell id='Name'&gt;IO_QUEUES&lt;/cell&gt;"
        r"&lt;cell id='Datatype'&gt;&lt;/cell&gt;&lt;/row&gt;",
        "",
        xml,
    )

    # 6. Fix JMS outbound QueueName: ${header.QueueName} -> ${property.QueueName}
    xml = xml.replace(
        "<value>${header.QueueName}</value>",
        "<value>${property.QueueName}</value>",
    )

    # 7. I0541_P only: insert Internal Order Splitter between Set Monitoring Identifiers
    #    and Log Payload. Set Monitoring -> IOSplitter -> Log Payload.
    #    Original: SequenceFlow_29 goes Set Monitoring -> Log Payload (after step 4 above).
    if with_io_splitter:
        # Insert splitter callActivity element before the Log Payload callActivity
        log_payload_ca = xml.find('<bpmn2:callActivity id="CallActivity_21" name="Log Payload">')
        if log_payload_ca < 0:
            raise ValueError("CallActivity_21 (Log Payload) not found for IO splitter insertion")
        xml = xml[:log_payload_ca] + IO_SPLITTER_CALLACTIVITY + "        " + xml[log_payload_ca:]
        # Rewire: SequenceFlow_29 -> splitter; splitter -> Log Payload
        xml = xml.replace(
            'id="SequenceFlow_29" sourceRef="CallActivity_19" targetRef="CallActivity_21"',
            'id="SequenceFlow_29" sourceRef="CallActivity_19" targetRef="CallActivity_IOSplitter"',
        )
        # Also need to update Log Payload's incoming flow
        # Log Payload incoming was SequenceFlow_30 (removed) or SequenceFlow_29 (now going to splitter)
        # We need a new SequenceFlow_IOSplit_out -> CallActivity_21
        # Find where CallActivity_21 declares incoming and update it
        # Also add SequenceFlow_IOSplit_in and SequenceFlow_IOSplit_out at Process_15 level
        # Find the closing </bpmn2:process> after Process_15
        # Actually: replace CallActivity_21's incoming SequenceFlow with SequenceFlow_IOSplit_out
        xml = xml.replace(
            '<bpmn2:incoming>SequenceFlow_29</bpmn2:incoming>\n            <bpmn2:outgoing>SequenceFlow_31</bpmn2:outgoing>\n        </bpmn2:callActivity>',
            '<bpmn2:incoming>SequenceFlow_IOSplit_out</bpmn2:incoming>\n            <bpmn2:outgoing>SequenceFlow_31</bpmn2:outgoing>\n        </bpmn2:callActivity>',
        )
        # Update splitter incoming/outgoing references in IO_SPLITTER_CALLACTIVITY
        # (they already have SequenceFlow_IOSplit_in and SequenceFlow_IOSplit_out)
        # Add the two sequence flows for the splitter
        # Find Process_15's closing </bpmn2:process> and insert before it
        # (Process_15 is after the new Process_46 which we already replaced)
        p15_start = xml.find('<bpmn2:process id="Process_15"')
        p15_end = xml.find("</bpmn2:process>", p15_start) + len("</bpmn2:process>")
        insert_sf = (
            '        <bpmn2:sequenceFlow id="SequenceFlow_IOSplit_in" sourceRef="CallActivity_19" targetRef="CallActivity_IOSplitter"/>\n'
            '        <bpmn2:sequenceFlow id="SequenceFlow_IOSplit_out" sourceRef="CallActivity_IOSplitter" targetRef="CallActivity_21"/>\n'
        )
        xml = xml[:p15_end - len("</bpmn2:process>")] + insert_sf + "    </bpmn2:process>" + xml[p15_end:]

    return xml


def apply_jms_to_processdirect_sender(xml: str, iflow_name: str, old_sender_system: str) -> str:
    """Convert a JMSToREST child into a PDToREST child:
      - Replace JMS inbound adapter (MessageFlow to StartEvent_2) with ProcessDirect
      - Remove Max Retries gateway + Send to DLQ from Process_1
      - Remove CPI_DLQ participant
      - Update HTTPS retrigger urlPath
    """
    pd_address = "/" + iflow_name

    # --- Replace JMS inbound MessageFlow with ProcessDirect ---
    # Find the MessageFlow that sources from FSAP sender and targets StartEvent_2
    # It's identified by: targetRef="StartEvent_2" and ComponentType JMS Sender
    # We replace its entire block
    mf_jms_start = xml.find(f'name="JMS" sourceRef="{_find_fsap_participant(xml, old_sender_system)}" targetRef="StartEvent_2"')
    if mf_jms_start < 0:
        # Try without system name — just find the JMS inbound to StartEvent_2
        mf_jms_start = _find_jms_inbound_mf(xml)
    if mf_jms_start < 0:
        raise ValueError("JMS inbound MessageFlow not found")
    # Back up to find the MessageFlow element opening
    mf_elem_start = xml.rfind("<bpmn2:messageFlow", 0, mf_jms_start)
    mf_elem_end = xml.find("</bpmn2:messageFlow>", mf_elem_start) + len("</bpmn2:messageFlow>")
    mf_id_match = re.search(r'id="([^"]+)"', xml[mf_elem_start:mf_elem_start+100])
    mf_id = mf_id_match.group(1) if mf_id_match else "MessageFlow_JMSInbound"

    # Find the FSAP sender participant id
    fsap_pid = _find_participant_id(xml, old_sender_system)

    new_pd_mf = f"""<bpmn2:messageFlow id="{mf_id}" name="ProcessDirect" sourceRef="{fsap_pid}" targetRef="StartEvent_2">
            <bpmn2:extensionElements>
                <ifl:property>
                    <key>ComponentType</key>
                    <value>ProcessDirect</value>
                </ifl:property>
                <ifl:property>
                    <key>Description</key>
                    <value/>
                </ifl:property>
                <ifl:property>
                    <key>address</key>
                    <value>{pd_address}</value>
                </ifl:property>
                <ifl:property>
                    <key>ComponentNS</key>
                    <value>sap</value>
                </ifl:property>
                <ifl:property>
                    <key>Vendor</key>
                    <value>SAP</value>
                </ifl:property>
                <ifl:property>
                    <key>componentVersion</key>
                    <value>1.1</value>
                </ifl:property>
                <ifl:property>
                    <key>Name</key>
                    <value>ProcessDirect</value>
                </ifl:property>
                <ifl:property>
                    <key>TransportProtocolVersion</key>
                    <value>1.1.2</value>
                </ifl:property>
                <ifl:property>
                    <key>ComponentSWCVName</key>
                    <value>external</value>
                </ifl:property>
                <ifl:property>
                    <key>system</key>
                    <value>{old_sender_system}</value>
                </ifl:property>
                <ifl:property>
                    <key>TransportProtocol</key>
                    <value>Not Applicable</value>
                </ifl:property>
                <ifl:property>
                    <key>cmdVariantUri</key>
                    <value>ctype::AdapterVariant/cname::ProcessDirect/vendor::SAP/tp::Not Applicable/mp::Not Applicable/direction::Sender/version::1.1.2</value>
                </ifl:property>
                <ifl:property>
                    <key>MessageProtocol</key>
                    <value>Not Applicable</value>
                </ifl:property>
                <ifl:property>
                    <key>MessageProtocolVersion</key>
                    <value>1.1.2</value>
                </ifl:property>
                <ifl:property>
                    <key>ComponentSWCVId</key>
                    <value>1.1.2</value>
                </ifl:property>
                <ifl:property>
                    <key>direction</key>
                    <value>Sender</value>
                </ifl:property>
            </bpmn2:extensionElements>
        </bpmn2:messageFlow>"""
    xml = xml[:mf_elem_start] + new_pd_mf + xml[mf_elem_end:]

    # --- Simplify Process_1 (Integration Process from Source):
    #     Remove Max Retries gateway + Send to DLQ; wire Start -> Main Process -> End
    # Find Process_1
    p1_start = xml.find('<bpmn2:process id="Process_1" name="Integration Process from Source">')
    if p1_start < 0:
        return xml  # Different structure; skip
    p1_end = xml.find("</bpmn2:process>", p1_start) + len("</bpmn2:process>")
    p1_xml = xml[p1_start:p1_end]

    # Find the Main Process callActivity id in Process_1
    main_ca = re.search(r'<bpmn2:callActivity id="([^"]+)" name="Main Process"', p1_xml)
    main_ca_id = main_ca.group(1) if main_ca else "CallActivity_503"
    main_process_ref = re.search(r'<key>processId</key>\s*<value>([^<]+)</value>', p1_xml)
    main_pid = main_process_ref.group(1) if main_process_ref else "Process_487"

    new_p1 = f"""<bpmn2:process id="Process_1" name="Integration Process from Source">
        <bpmn2:extensionElements>
            <ifl:property>
                <key>transactionTimeout</key>
                <value>30</value>
            </ifl:property>
            <ifl:property>
                <key>componentVersion</key>
                <value>1.2</value>
            </ifl:property>
            <ifl:property>
                <key>cmdVariantUri</key>
                <value>ctype::FlowElementVariant/cname::IntegrationProcess/version::1.2.1</value>
            </ifl:property>
            <ifl:property>
                <key>transactionalHandling</key>
                <value>Not Required</value>
            </ifl:property>
        </bpmn2:extensionElements>
        <bpmn2:startEvent id="StartEvent_2" name="Start">
            <bpmn2:extensionElements>
                <ifl:property>
                    <key>componentVersion</key>
                    <value>1.0</value>
                </ifl:property>
                <ifl:property>
                    <key>cmdVariantUri</key>
                    <value>ctype::FlowstepVariant/cname::MessageStartEvent/version::1.0</value>
                </ifl:property>
            </bpmn2:extensionElements>
            <bpmn2:outgoing>SequenceFlow_PDToREST_1</bpmn2:outgoing>
            <bpmn2:messageEventDefinition/>
        </bpmn2:startEvent>
        <bpmn2:callActivity id="{main_ca_id}" name="Main Process">
            <bpmn2:extensionElements>
                <ifl:property>
                    <key>processId</key>
                    <value>{main_pid}</value>
                </ifl:property>
                <ifl:property>
                    <key>componentVersion</key>
                    <value>1.0</value>
                </ifl:property>
                <ifl:property>
                    <key>activityType</key>
                    <value>ProcessCallElement</value>
                </ifl:property>
                <ifl:property>
                    <key>cmdVariantUri</key>
                    <value>ctype::FlowstepVariant/cname::NonLoopingProcess/version::1.0.4</value>
                </ifl:property>
                <ifl:property>
                    <key>subActivityType</key>
                    <value>NonLoopingProcess</value>
                </ifl:property>
            </bpmn2:extensionElements>
            <bpmn2:incoming>SequenceFlow_PDToREST_1</bpmn2:incoming>
            <bpmn2:outgoing>SequenceFlow_PDToREST_2</bpmn2:outgoing>
        </bpmn2:callActivity>
        <bpmn2:endEvent id="EndEvent_2" name="End">
            <bpmn2:extensionElements>
                <ifl:property>
                    <key>componentVersion</key>
                    <value>1.1</value>
                </ifl:property>
                <ifl:property>
                    <key>cmdVariantUri</key>
                    <value>ctype::FlowstepVariant/cname::MessageEndEvent/version::1.1.0</value>
                </ifl:property>
            </bpmn2:extensionElements>
            <bpmn2:incoming>SequenceFlow_PDToREST_2</bpmn2:incoming>
            <bpmn2:messageEventDefinition/>
        </bpmn2:endEvent>
        <bpmn2:sequenceFlow id="SequenceFlow_PDToREST_1" sourceRef="StartEvent_2" targetRef="{main_ca_id}"/>
        <bpmn2:sequenceFlow id="SequenceFlow_PDToREST_2" sourceRef="{main_ca_id}" targetRef="EndEvent_2"/>
    </bpmn2:process>"""
    xml = xml[:p1_start] + new_p1 + xml[p1_end:]

    # --- Remove CPI_DLQ participant and its JMS DLQ send MessageFlow ---
    xml = _remove_participant_and_mf(xml, "CPI_DLQ")

    # --- Update HTTPS retrigger urlPath ---
    # Find urlPath that contains the old iflow name pattern and replace with new one
    # Pattern: /I0540_CostCenter_FSAP_Medius_JMSToREST -> /I0539_CostCenter_FSAP_Medius_PDToREST
    xml = re.sub(
        r"(<key>urlPath</key>\s*<value>)/[^<]+JMSToREST(</value>)",
        r"\g<1>" + pd_address + r"\2",
        xml,
    )

    return xml


def _find_participant_id(xml: str, name: str) -> str:
    m = re.search(r'<bpmn2:participant id="([^"]+)"[^>]+name="' + re.escape(name) + '"', xml)
    if m:
        return m.group(1)
    return "Participant_1"


def _find_fsap_participant(xml: str, system_name: str) -> str:
    return _find_participant_id(xml, system_name)


def _find_jms_inbound_mf(xml: str) -> int:
    """Find position of JMS inbound MessageFlow name= attribute targeting StartEvent_2."""
    m = re.search(r'<bpmn2:messageFlow id="[^"]+" name="JMS" sourceRef="[^"]+" targetRef="StartEvent_2"', xml)
    if m:
        return m.start() + len('<bpmn2:messageFlow id="xxx" ')
    # Fallback: find any MessageFlow to StartEvent_2 that has JMS
    m = re.search(r'targetRef="StartEvent_2"', xml)
    return m.start() if m else -1


def _remove_participant_and_mf(xml: str, participant_name: str) -> str:
    """Remove a participant element and any MessageFlow that references it."""
    pid_m = re.search(r'<bpmn2:participant id="([^"]+)"[^>]+name="' + re.escape(participant_name) + '"', xml)
    if not pid_m:
        return xml
    pid = pid_m.group(1)
    # Remove the participant element.
    # pid_m.start() IS the start of <bpmn2:participant — no rfind needed.
    p_start = pid_m.start()
    p_sc = xml.find("/>", p_start)
    p_fc = xml.find("</bpmn2:participant>", p_start)
    if p_fc >= 0 and (p_sc < 0 or p_fc < p_sc):
        p_end = p_fc + len("</bpmn2:participant>")
    elif p_sc >= 0:
        p_end = p_sc + 2
    else:
        return xml
    xml = xml[:p_start] + xml[p_end:]
    # Remove any MessageFlow referencing this participant (search the modified xml).
    # The regex starts with <bpmn2:messageFlow, so mf_m.start() IS the element start.
    for mf_m in list(re.finditer(
        r'<bpmn2:messageFlow id="[^"]+"[^>]*(?:sourceRef|targetRef)="' + re.escape(pid) + '"',
        xml,
    )):
        mf_start = mf_m.start()
        mf_end_find = xml.find("</bpmn2:messageFlow>", mf_start)
        if mf_end_find >= 0:
            mf_end = mf_end_find + len("</bpmn2:messageFlow>")
        else:
            mf_sc = xml.find("/>", mf_start)
            if mf_sc >= 0:
                mf_end = mf_sc + 2
            else:
                continue
        xml = xml[:mf_start] + xml[mf_end:]
        break
    return xml


# ---------------------------------------------------------------------------
# 1. I0710_P_JMSDispatcher_Medius
# ---------------------------------------------------------------------------

def build_i0710_dispatcher():
    """New Medius JMS dispatcher, cloned from I0701."""
    name = "I0710_P_JMSDispatcher_Medius"
    version = "1.0.0"
    print(f"Building {name} v{version}...")

    src_zip = os.path.join(REF_IFLOWS, "I0701_P_JMSDispatcher_MSAP_PlantMaintenance.zip")
    files = read_standalone_zip(src_zip)

    # Rename iflw file
    old_iflw = iflow_xml_name(files)
    new_iflw_path = os.path.dirname(old_iflw) + "/" + name + ".iflw"
    xml = files.pop(old_iflw).decode("utf-8")

    # Text replacements throughout iflw
    old_name = "I0701_P_JMSDispatcher_MSAP_PlantMaintenance"
    xml = xml.replace(old_name, name)
    xml = xml.replace("MSAPPlantMaintenanceDispatcher", "MediusDispatcher")
    xml = xml.replace("I0701_MSAP_PlantMaintenance", "I0710_Medius")

    files[new_iflw_path] = xml.encode("utf-8")

    # Update MANIFEST.MF
    files["META-INF/MANIFEST.MF"] = update_manifest(
        files["META-INF/MANIFEST.MF"], name, version
    )

    # Update parameters.prop
    prop = files["src/main/resources/parameters.prop"].decode("utf-8")
    prop = set_param(prop, "JMS_QueueName", "I0710_Medius")
    # Update SAP_Sender for FSAP source
    prop = set_param(prop, "SAP_Sender", "DR1_350")
    files["src/main/resources/parameters.prop"] = prop.encode("utf-8")

    # Update metainfo.prop if present
    if "metainfo.prop" in files:
        mi = files["metainfo.prop"].decode("utf-8")
        mi = mi.replace(old_name, name)
        files["metainfo.prop"] = mi.encode("utf-8")

    # Update .project if present
    if ".project" in files:
        proj = files[".project"].decode("utf-8")
        proj = proj.replace(old_name, name)
        files[".project"] = proj.encode("utf-8")

    build_dir = make_output_dir(name)
    out_zip = os.path.join(build_dir, name + ".zip")
    create_iflow_zip(out_zip, files)
    print(f"  -> {out_zip}")
    return out_zip


# ---------------------------------------------------------------------------
# 2–4. Updated Parent iFlows
# ---------------------------------------------------------------------------

FSAP_PKG = os.path.join(REF_IFLOWS, "FSAP_Controlling_MasterData.zip")


def _new_recv_det_i0539() -> str:
    return """\
import com.sap.gateway.ip.core.customdev.util.Message

def Message processData(Message message) {
    def arr_receiversQueueList = []
    def arr_receiversIFlowList = []
    def counter = 0

    // Medius -> I0702 common dispatcher queue
    arr_receiversQueueList.add("I0710_Medius")
    arr_receiversIFlowList.add("I0539_CostCenter_FSAP_Medius_PDToREST")
    counter++

    // Oracle -> dedicated queue (dummy: iFlow name = queue name)
    arr_receiversQueueList.add("I0539_ORACLE")
    arr_receiversIFlowList.add("I0539_ORACLE")
    counter++

    message.setProperty("arr_receiversQueueList", arr_receiversQueueList)
    message.setProperty("arr_receiversIFlowList", arr_receiversIFlowList)
    message.setProperty("arr_receiversLastIndex", counter - 1)
    return message
}
"""


def _new_recv_det_i0541() -> str:
    return """\
import com.sap.gateway.ip.core.customdev.util.Message

def Message processData(Message message) {
    def arr_receiversQueueList = []
    def arr_receiversIFlowList = []
    def counter = 0

    // Medius -> I0702 common dispatcher queue (only receiver; ASAP decommissioned)
    arr_receiversQueueList.add("I0710_Medius")
    arr_receiversIFlowList.add("I0541_InternalOrder_FSAP_Medius_PDToREST")
    counter++

    message.setProperty("arr_receiversQueueList", arr_receiversQueueList)
    message.setProperty("arr_receiversIFlowList", arr_receiversIFlowList)
    message.setProperty("arr_receiversLastIndex", counter - 1)
    return message
}
"""


def _new_recv_det_i0545() -> str:
    return """\
import com.sap.gateway.ip.core.customdev.util.Message

def Message processData(Message message) {
    def arr_receiversQueueList = []
    def arr_receiversIFlowList = []
    def counter = 0

    // Medius -> I0702 common dispatcher queue
    arr_receiversQueueList.add("I0710_Medius")
    arr_receiversIFlowList.add("I0545_WBSElement_FSAP_Medius_PDToREST")
    counter++

    // Mobile -> dedicated queue (dummy: iFlow name = queue name)
    arr_receiversQueueList.add("I0546_MOBILE")
    arr_receiversIFlowList.add("I0546_MOBILE")
    counter++

    message.setProperty("arr_receiversQueueList", arr_receiversQueueList)
    message.setProperty("arr_receiversIFlowList", arr_receiversIFlowList)
    message.setProperty("arr_receiversLastIndex", counter - 1)
    return message
}
"""


def _build_parent(bundle_name: str, new_name: str, new_version: str,
                  recv_det_groovy: str, with_io_splitter: bool = False,
                  extra_iflw_transforms=None):
    """Generic parent builder. extra_iflw_transforms: optional fn(xml)->xml."""
    print(f"Building {new_name} v{new_version}...")

    files = read_from_package(FSAP_PKG, bundle_name)

    # Rename iflw to match the actual iFlow name
    old_iflw = iflow_xml_name(files)
    new_iflw_path = os.path.dirname(old_iflw) + "/" + new_name + ".iflw"
    xml = files.pop(old_iflw).decode("utf-8")

    # Apply new loop pattern
    xml = apply_new_loop_to_parent_iflw(xml, with_io_splitter=with_io_splitter)

    # Apply any extra transforms (e.g. remove ASAP gateway for I0541_P)
    if extra_iflw_transforms:
        xml = extra_iflw_transforms(xml)

    files[new_iflw_path] = xml.encode("utf-8")

    # Update MANIFEST.MF
    files["META-INF/MANIFEST.MF"] = update_manifest(
        files["META-INF/MANIFEST.MF"], new_name, new_version
    )

    # Replace ReceiverDetermination.groovy
    rd_key = "src/main/resources/script/ReceiverDetermination.groovy"
    files[rd_key] = recv_det_groovy.encode("utf-8")

    # Remove old loop scripts
    for script in [
        "src/main/resources/script/AddQueueIndex.groovy",
        "src/main/resources/script/SetQueueNameHeader.groovy",
        "src/main/resources/script/RestorePayload.groovy",
    ]:
        files.pop(script, None)

    # Update parameters.prop: remove P_IO_QUEUES and IO_QUEUES
    prop_key = "src/main/resources/parameters.prop"
    if prop_key in files:
        prop = files[prop_key].decode("utf-8")
        prop = remove_param(prop, "P_IO_QUEUES")
        prop = remove_param(prop, "IO_QUEUES")
        # Remove the malformed key "I0541_MEDIUS,I0542_MOBILE=..." artifact
        prop = re.sub(r"^I0\d+_[A-Z]+,[^=\n]+=.*\n?", "", prop, flags=re.MULTILINE)
        # Same for I0545 artifact "I0545_MEDIUS,I0546_MOBILE=..."
        prop = re.sub(r"^I0545_[A-Z]+,[^=\n]+=.*\n?", "", prop, flags=re.MULTILINE)
        files[prop_key] = prop.encode("utf-8")

    # Update .project
    if ".project" in files:
        proj = files[".project"].decode("utf-8")
        proj = proj.replace(bundle_name, new_name)
        files[".project"] = proj.encode("utf-8")

    build_dir = make_output_dir(new_name)
    out_zip = os.path.join(build_dir, new_name + ".zip")
    create_iflow_zip(out_zip, files)
    print(f"  -> {out_zip}")
    return out_zip


def _remove_asap_gateway(xml: str) -> str:
    """I0541_P only: remove ExclusiveGateway_8099 (ASAP?) and its sequence flows.
    The gateway sits between SetQueueNameHeader and Send in old Process_46.
    Since Process_46 is already replaced, this is now a no-op — but left here
    as documentation that ASAP is handled by the Process_46 replacement."""
    # The ASAP gateway was entirely within Process_46, which we already replaced.
    # Nothing to do here.
    return xml


def build_i0539_parent():
    return _build_parent(
        "I0539_P_CostCenter_FSAP_SOAPToJMS",
        "I0539_P_CostCenter_FSAP_SOAPToJMS",
        "2.0.0",
        _new_recv_det_i0539(),
    )


def build_i0541_parent():
    return _build_parent(
        "I0541_P_InternalOrder_FSAP_SOAPToJMS",
        "I0541_P_InternalOrder_FSAP_SOAPToJMS",
        "2.0.0",
        _new_recv_det_i0541(),
        with_io_splitter=True,
        extra_iflw_transforms=_remove_asap_gateway,
    )


def build_i0545_parent():
    return _build_parent(
        "I0545_P_WBSElement_FSAP_SOAPToJMS",
        "I0545_P_WBSElement_FSAP_SOAPToJMS",
        "2.0.0",
        _new_recv_det_i0545(),
    )


# ---------------------------------------------------------------------------
# 5–7. New PDToREST Child iFlows
# ---------------------------------------------------------------------------

def _build_child_pdtorest(src_bundle: str, new_name: str, new_version: str,
                           old_sender_system: str = "FSAP",
                           remove_splitter: bool = False):
    """Convert a JMSToREST child into a PDToREST child."""
    print(f"Building {new_name} v{new_version}...")

    files = read_from_package(FSAP_PKG, src_bundle)

    # Rename iflw
    old_iflw = iflow_xml_name(files)
    new_iflw_path = os.path.dirname(old_iflw) + "/" + new_name + ".iflw"
    xml = files.pop(old_iflw).decode("utf-8")

    # Replace old iFlow name references in the XML with new name
    xml = xml.replace(src_bundle, new_name)

    # Convert JMS sender -> ProcessDirect + simplify Process_1
    xml = apply_jms_to_processdirect_sender(xml, new_name, old_sender_system)

    # Remove internal order splitter if moving it to parent
    if remove_splitter:
        xml = _remove_io_splitter(xml)

    files[new_iflw_path] = xml.encode("utf-8")

    # Update MANIFEST
    files["META-INF/MANIFEST.MF"] = update_manifest(
        files["META-INF/MANIFEST.MF"], new_name, new_version
    )

    # Update parameters.prop: replace QUEUE_NAME with PD address (informational)
    prop_key = "src/main/resources/parameters.prop"
    if prop_key in files:
        prop = files[prop_key].decode("utf-8")
        prop = remove_param(prop, "QUEUE_NAME")
        prop = remove_param(prop, "MaxRetries")
        files[prop_key] = prop.encode("utf-8")

    # Update .project
    if ".project" in files:
        proj = files[".project"].decode("utf-8")
        proj = proj.replace(src_bundle, new_name)
        files[".project"] = proj.encode("utf-8")

    build_dir = make_output_dir(new_name)
    out_zip = os.path.join(build_dir, new_name + ".zip")
    create_iflow_zip(out_zip, files)
    print(f"  -> {out_zip}")
    return out_zip


def _remove_io_splitter(xml: str) -> str:
    """Remove Internal Order Splitter from child (it moves to parent)."""
    ca_start = xml.find('<bpmn2:callActivity id="CallActivity_8565" name="Internal Order Splitter">')
    if ca_start < 0:
        return xml
    ca_end = xml.find("</bpmn2:callActivity>", ca_start) + len("</bpmn2:callActivity>")
    xml = xml[:ca_start] + xml[ca_end:]
    # Rewire: find incoming flow to splitter and change its targetRef to splitter's outgoing target
    # Splitter incoming: SequenceFlow_30 -> CallActivity_8565
    # Splitter outgoing: SequenceFlow_8566 -> (next step)
    # Find next step after splitter
    out_sf = re.search(r'<bpmn2:sequenceFlow id="SequenceFlow_8566" sourceRef="CallActivity_8565" targetRef="([^"]+)"', xml)
    if out_sf:
        next_id = out_sf.group(1)
        # Update the incoming flow to target next_id instead of splitter
        xml = xml.replace(
            'targetRef="CallActivity_8565"',
            f'targetRef="{next_id}"',
        )
        # Remove SequenceFlow_8566
        xml = re.sub(
            r'<bpmn2:sequenceFlow id="SequenceFlow_8566"[^/]*/>\s*',
            "",
            xml,
            flags=re.DOTALL,
        )
        # Update the step that had SequenceFlow_8566 as incoming
        xml = xml.replace(
            "<bpmn2:incoming>SequenceFlow_8566</bpmn2:incoming>",
            "<bpmn2:incoming>SequenceFlow_30</bpmn2:incoming>",
        )
    return xml


def build_i0539_child():
    return _build_child_pdtorest(
        "I0540_CostCenter_FSAP_Medius_JMSToREST",
        "I0539_CostCenter_FSAP_Medius_PDToREST",
        "1.0.0",
        old_sender_system="FSAP",
    )


def build_i0541_child():
    return _build_child_pdtorest(
        "I0541_InternalOrder_FSAP_Medius_JMSToREST",
        "I0541_InternalOrder_FSAP_Medius_PDToREST",
        "1.0.0",
        old_sender_system="FSAP",
        remove_splitter=True,
    )


def build_i0545_child():
    return _build_child_pdtorest(
        "I0545_WBSElement_FSAP_Medius_JMSToREST",
        "I0545_WBSElement_FSAP_Medius_PDToREST",
        "1.0.0",
        old_sender_system="FSAP",
    )


# ---------------------------------------------------------------------------
# CHANGELOG helpers
# ---------------------------------------------------------------------------

def write_changelog(iflow_name: str, version: str, entry: str) -> None:
    """Create or append to iflows/<name>/CHANGELOG.md."""
    cl_path = os.path.join(IFLOWS_OUT, iflow_name, "CHANGELOG.md")
    header = f"# CHANGELOG — {iflow_name}\n\n"
    block = f"## {version} — 2026-11-15\n{entry}\n\n"
    if os.path.exists(cl_path):
        existing = open(cl_path, encoding="utf-8").read()
        if version in existing:
            return  # already written
        # Prepend new entry after the header
        h_end = existing.find("\n\n") + 2
        content = existing[:h_end] + block + existing[h_end:]
    else:
        content = header + block
    with open(cl_path, "w", encoding="utf-8") as f:
        f.write(content)


# ---------------------------------------------------------------------------
# Main
# ---------------------------------------------------------------------------

def main():
    print("=" * 60)
    print("FSAP Dispatcher Migration — iFlow Build")
    print("=" * 60)

    results = []

    # Dispatcher
    results.append(build_i0710_dispatcher())
    write_changelog(
        "I0710_P_JMSDispatcher_Medius", "1.0.0",
        "New Medius JMS dispatcher for FSAP→Medius interfaces. "
        "Cloned from I0701_P_JMSDispatcher_MSAP_PlantMaintenance. "
        "Queue: I0710_Medius, DLQ: I0710_Medius_D. "
        "Routes via ProcessDirect to child iFlow named in SSAB_Dispatcher_ReceiverIFlow header.",
    )

    # Updated parents
    results.append(build_i0539_parent())
    write_changelog(
        "I0539_P_CostCenter_FSAP_SOAPToJMS", "2.0.0",
        "Migrated to new Iterating Splitter + arr_receiversQueueList pattern. "
        "Removed QUEUE_INDEX/QUEUE_LIST_SIZE loop (AddQueueIndex, SetQueueNameHeader, RestorePayload). "
        "Medius receiver now uses I0710_Medius dispatcher queue. "
        "Oracle receiver keeps I0539_ORACLE dedicated queue (dummy iFlow name). "
        "SAP_MessageProcessingLogCustomStatus set per iteration.",
    )

    results.append(build_i0541_parent())
    write_changelog(
        "I0541_P_InternalOrder_FSAP_SOAPToJMS", "2.0.0",
        "Migrated to new Iterating Splitter + arr_* pattern. "
        "ASAP gateway removed (ASAP decommissioned). "
        "Internal Order Splitter moved to parent (before ReceiverDetermination). "
        "Only Medius receiver via I0710_Medius dispatcher. "
        "IO_QUEUES (was empty) removed.",
    )

    results.append(build_i0545_parent())
    write_changelog(
        "I0545_P_WBSElement_FSAP_SOAPToJMS", "2.0.0",
        "Migrated to new Iterating Splitter + arr_* pattern. "
        "Medius receiver uses I0710_Medius dispatcher queue. "
        "Mobile receiver keeps I0546_MOBILE dedicated queue (dummy iFlow name). "
        "Removed malformed IO_QUEUES parameter artifact.",
    )

    # New PDToREST children
    results.append(build_i0539_child())
    write_changelog(
        "I0539_CostCenter_FSAP_Medius_PDToREST", "1.0.0",
        "New Medius child. ProcessDirect entry replacing JMS consumer (I0540_MEDIUS queue). "
        "All mapping, company filter, and UserResponsible logic carried over from I0540 unchanged. "
        "Bhavesh, no UDFs were added; ReplaceWithVirtualCompany.groovy copied unchanged from I0540.",
    )

    results.append(build_i0541_child())
    write_changelog(
        "I0541_InternalOrder_FSAP_Medius_PDToREST", "1.0.0",
        "New Medius child. ProcessDirect entry replacing JMS consumer (I0541_MEDIUS queue). "
        "Internal Order Splitter moved to I0541_P parent; child processes one order at a time. "
        "All REST/mapping logic carried over unchanged from I0541 (JMSToREST). "
        "Bhavesh, no UDFs were added; ReplaceWithVirtualCompany.groovy copied unchanged.",
    )

    results.append(build_i0545_child())
    write_changelog(
        "I0545_WBSElement_FSAP_Medius_PDToREST", "1.0.0",
        "New Medius child. ProcessDirect entry replacing JMS consumer (I0545_MEDIUS queue). "
        "OData lookup stays inside child unchanged. "
        "All REST/mapping logic carried over from I0545 (JMSToREST). "
        "Bhavesh, no UDFs were added; ReplaceWithVirtualCompany.groovy copied unchanged.",
    )

    print("\n" + "=" * 60)
    print("Build complete. ZIPs:")
    for r in results:
        print(f"  {r}")
    print("=" * 60)
    print("\nNext steps:")
    print("  1. Import I0710_P_JMSDispatcher_Medius first (creates the dispatcher)")
    print("  2. Import PDToREST children (I0539/I0541/I0545)")
    print("  3. Import updated parents (I0539_P / I0541_P / I0545_P)")
    print("  4. Queue I0710_Medius must be created in CPI before deploying dispatcher")
    print("  5. Old queues I0540_MEDIUS / I0541_MEDIUS / I0545_MEDIUS drain then retire")


if __name__ == "__main__":
    main()
