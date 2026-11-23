"""Validate all built iFlow ZIPs: well-formed XML + no AI strings + manifest match."""
import os, re, sys, zipfile
sys.stdout.reconfigure(encoding="utf-8")
from lxml import etree
sys.path.insert(0, "tools")
import iflow_lib

iflows = [
    "I0710_P_JMSDispatcher_Medius",
    "I0539_P_CostCenter_FSAP_SOAPToJMS",
    "I0541_P_InternalOrder_FSAP_SOAPToJMS",
    "I0545_P_WBSElement_FSAP_SOAPToJMS",
    "I0539_CostCenter_FSAP_Medius_PDToREST",
    "I0541_InternalOrder_FSAP_Medius_PDToREST",
    "I0545_WBSElement_FSAP_Medius_PDToREST",
    "I0711_P_JMSDispatcher_StreamServe",
    "I0544_P_BusinessPartner_FSAP_SOAPToJMS",
    "I0544_BusinessPartner_FSAP_Medius_PDToREST",
    "I0544_BusinessPartner_FSAP_StreamServeDDS_PDToJDBC",
    "SmarTeam/I2050_MaintenanceBOM_MSAP_SmarTeam_JMSToHTTP",
    "SmarTeam/I2050_P_MaintenanceBOM_MSAP_AMQPToJMS",
    "SmarTeam/I2049_MaterialBOM_MSAP_SmarTeam_JMSToHTTP",
    "SmarTeam/I2049_P_MaterialBOM_MSAP_AMQPToJMS",
    "SmarTeam/I2018_Material_MSAP_SmarTeam_JMSToHTTP",
    "SmarTeam/I2018_P_Material_MSAP_SOAPToJMS",
    "SmarTeam/I2023_Equipment_COD_EQUIPMENT_SAVE_COD_EQUIPMENT_SAVE01_MSAP_SmarTeam_JMSToHTTP",
    "SmarTeam/I2023_P_Equipment_COD_EQUIPMENT_SAVE_COD_EQUIPMENT_SAVE01_MSAP_IDocToJMS",
    "SmarTeam/I2024_FunctionLocation_COD_FUNCTIONAL_LOCATION_SAVE_COD_FUNCTIONAL_LOCATION_SAVE01_MSAP_SmarTeam_JMSToHTTP",
    "SmarTeam/I2024_P_FunctionLocation_COD_FUNCTIONAL_LOCATION_SAVE_COD_FUNCTIONAL_LOCATION_SAVE01_MSAP_IDocToJMS",
    "Tibnor_SSAB_EDIMigration/IXXXX_P_PurchaseOrder_ORDERS_ORDERS02_TibnorS4_IDocToJMS",
    "Tibnor_SSAB_EDIMigration/IXXXX_PurchaseOrder_ORDERS_ORDERS02_TibnorS4_FinMessageHub_HameenlinnaMetocs_JMSToMQ",
]

all_ok = True
for entry in iflows:
    name = entry.split("/")[-1]   # "<Package>/<IFlowName>" or "<IFlowName>"
    # \\?\ + absolute path: the I2023/I2024 SmarTeam names exceed 260 characters on Windows
    zip_path = "\\\\?\\" + os.path.abspath(os.path.join("iflows", *entry.split("/"), "build", name + ".zip"))
    with zipfile.ZipFile(zip_path) as z:
        entries = z.namelist()
        iflw_path = next(n for n in entries if n.endswith(".iflw"))
        xml_bytes = z.read(iflw_path)
        prop_path = "src/main/resources/parameters.prop"
        prop_text = z.read(prop_path).decode("utf-8") if prop_path in entries else None
        # Check no AI strings
        bad = []
        for e in entries:
            if e.endswith((".iflw", ".prop", ".groovy", ".xml")):
                content = z.read(e).decode("utf-8", errors="replace")
                if "claude" in content.lower() or "anthropic" in content.lower():
                    bad.append(e)
        # Check MANIFEST
        mf_name = ""
        try:
            mf = z.read("META-INF/MANIFEST.MF").decode("utf-8")
            mf = re.sub(r"\r?\n ", "", mf)   # undo the 72-byte line wrapping
            for line in mf.splitlines():
                if line.startswith("Bundle-Name:"):
                    mf_name = line.split(":", 1)[1].strip()
        except KeyError:
            pass

    # Check XML well-formed
    xml_ok = True
    xml_err = ""
    try:
        etree.fromstring(xml_bytes)
    except etree.XMLSyntaxError as e:
        xml_ok = False
        xml_err = str(e)

    # Line count sanity
    line_count = len(xml_bytes.decode("utf-8").splitlines())

    diag = iflow_lib.check_iflow(xml_bytes.decode("utf-8")) if xml_ok else []
    ok = xml_ok and not bad and mf_name == name and not diag
    status = "OK " if ok else "FAIL"
    if not ok:
        all_ok = False
    print(f"{status}  {name}  ({line_count} lines)")
    if not xml_ok:
        print(f"     XML: {xml_err}")
    if bad:
        print(f"     AI strings in: {bad}")
    for d in diag:
        print(f"     DIAGRAM: {d}")
    # SSAB best practices (PDF v1.9): reported, not a failure
    if xml_ok:
        for f in iflow_lib.best_practice_flags(xml_bytes.decode("utf-8"), prop_text):
            print(f"     FLAG: {f}")
    if mf_name != name:
        print(f"     MANIFEST: '{mf_name}'")

print()
print("All OK" if all_ok else "FAILURES detected")
