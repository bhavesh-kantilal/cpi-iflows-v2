"""Make a self-contained WSDL: copy the external XSDs a WSDL imports by URL into its <types>.

    py -I tools/wsdl_inline.py <in.wsdl> <out.wsdl> <namespace>=<file.xsd> [...]

For every <import namespace="X" schemaLocation="..."> inside <types>, the schemaLocation attribute is removed
and the schema from the matching file is appended to <types> as its own <schema> block.
That is the layout of the SAP WSDLs in _reference/ (several inline schemas joined by namespace-only imports,
e.g. CostCentertoMedius, SupplierMastertoMedius). The input WSDL is not changed.
"""
import sys
from pathlib import Path

from lxml import etree

sys.stdout.reconfigure(encoding="utf-8")
WSDL = "http://schemas.xmlsoap.org/wsdl/"
XSD = "http://www.w3.org/2001/XMLSchema"


def inline(src: Path, out: Path, schemas: dict[str, Path]):
    tree = etree.parse(str(src))
    types = tree.getroot().find(f"{{{WSDL}}}types")
    done = set()
    for imp in types.iter(f"{{{XSD}}}import"):
        ns = imp.get("namespace")
        if imp.get("schemaLocation") and ns in schemas:
            del imp.attrib["schemaLocation"]
            done.add(ns)
    missing = set(schemas) - done
    if missing:
        raise SystemExit(f"no URL import found for {missing}")
    for ns, f in schemas.items():
        root = etree.parse(str(f)).getroot()
        if root.get("targetNamespace") != ns:
            raise SystemExit(f"{f}: targetNamespace {root.get('targetNamespace')} != {ns}")
        types.append(root)
    left = [i.get("schemaLocation") for i in types.iter(f"{{{XSD}}}import") if i.get("schemaLocation")]
    if left:
        raise SystemExit(f"still external: {left}")
    tree.write(str(out), xml_declaration=True, encoding="UTF-8")


if __name__ == "__main__":
    pairs = dict(a.split("=", 1) for a in sys.argv[3:])
    inline(Path(sys.argv[1]), Path(sys.argv[2]), {k: Path(v) for k, v in pairs.items()})
    print("written", sys.argv[2])
