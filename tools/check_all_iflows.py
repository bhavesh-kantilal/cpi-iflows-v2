"""Validate all 7 built iFlow ZIPs: well-formed XML + no AI strings + manifest match."""
import sys, zipfile
sys.stdout.reconfigure(encoding="utf-8")
from lxml import etree

iflows = [
    "I0702_P_JMSDispatcher_Medius",
    "I0539_P_CostCenter_FSAP_SOAPToJMS",
    "I0541_P_InternalOrder_FSAP_SOAPToJMS",
    "I0545_P_WBSElement_FSAP_SOAPToJMS",
    "I0539_CostCenter_FSAP_Medius_PDToREST",
    "I0541_InternalOrder_FSAP_Medius_PDToREST",
    "I0545_WBSElement_FSAP_Medius_PDToREST",
]

all_ok = True
for name in iflows:
    zip_path = f"iflows/{name}/build/{name}.zip"
    with zipfile.ZipFile(zip_path) as z:
        entries = z.namelist()
        iflw_path = next(n for n in entries if n.endswith(".iflw"))
        xml_bytes = z.read(iflw_path)
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

    ok = xml_ok and not bad and mf_name == name
    status = "OK " if ok else "FAIL"
    if not ok:
        all_ok = False
    print(f"{status}  {name}  ({line_count} lines)")
    if not xml_ok:
        print(f"     XML: {xml_err}")
    if bad:
        print(f"     AI strings in: {bad}")
    if mf_name != name:
        print(f"     MANIFEST: '{mf_name}'")

print()
print("All OK" if all_ok else "FAILURES detected")
