"""Make a self-contained WSDL: copy the external XSDs a WSDL imports by URL into its <types>.

    py -I tools/wsdl_inline.py <in.wsdl> <out.wsdl> <namespace>=<file.xsd> [...]

For every <import namespace="X" schemaLocation="..."> inside <types>, the schemaLocation attribute is removed
and the schema from the matching file is added to <types> as its own <schema> block.
That is the layout of the SAP WSDLs in _reference/ (several inline schemas joined by namespace-only imports,
e.g. CostCentertoMedius, SupplierMastertoMedius). The input WSDL is not changed.

The schemas are spliced in as TEXT, each with all namespace declarations of its own root. Moving them as XML
elements loses declarations that are only used inside attribute values (ref="tns:x", type="tns:T"): the
library sees no element using the prefix and drops it, so 'tns' silently falls back to the WSDL's own 'tns'
and none of the types resolve (NShift v1.0.0, CPI showed an empty Consignment, 2026-11-13).
As a self-check, the merged schema set is compiled before the file is written.
"""
import re
import sys
import tempfile
from pathlib import Path

from lxml import etree

sys.stdout.reconfigure(encoding="utf-8")
WSDL = "http://schemas.xmlsoap.org/wsdl/"
XSD = "http://www.w3.org/2001/XMLSchema"


def schema_text(f: Path, ns: str) -> bytes:
    root = etree.parse(str(f)).getroot()
    if root.get("targetNamespace") != ns:
        raise SystemExit(f"{f}: targetNamespace {root.get('targetNamespace')} != {ns}")
    text = etree.tostring(root)                     # the root's own xmlns:* declarations are all written
    for prefix, uri in root.nsmap.items():
        decl = (f'xmlns:{prefix}="{uri}"' if prefix else f'xmlns="{uri}"').encode()
        if decl not in text.split(b">", 1)[0]:
            raise SystemExit(f"{f}: declaration {decl!r} missing on the schema root")
    return text


def compile_check(wsdl_bytes: bytes):
    """Compile all <types> schemas together (imports resolved locally). Raises on unresolved references."""
    types = etree.fromstring(wsdl_bytes).find(f"{{{WSDL}}}types")
    schemas = types.findall(f"{{{XSD}}}schema")
    with tempfile.TemporaryDirectory() as d:
        files = []
        for i, s in enumerate(schemas):
            # re-serialise with the WSDL root's declarations in scope, as a parser of the WSDL would see them
            s = etree.fromstring(etree.tostring(s))
            for imp in s.findall(f"{{{XSD}}}import"):
                j = [k for k, x in enumerate(schemas) if x.get("targetNamespace") == imp.get("namespace")]
                if j:
                    imp.set("schemaLocation", f"s{j[0]}.xsd")
            p = Path(d) / f"s{i}.xsd"
            p.write_bytes(etree.tostring(s))
            files.append(p)
        for p in files:
            etree.XMLSchema(etree.parse(str(p)))


def inline(src: Path, out: Path, schemas: dict[str, Path]):
    data = src.read_bytes()
    for ns in schemas:
        pat = re.compile(rb'(<(?:\w+:)?import\b[^>]*namespace="' + re.escape(ns.encode()) + rb'"[^>]*?)\s+schemaLocation="[^"]*"')
        data, n = pat.subn(rb"\1", data)
        if n == 0:
            data2 = re.sub(rb'(<(?:\w+:)?import\b)([^>]*?)\s+schemaLocation="[^"]*"([^>]*namespace="'
                           + re.escape(ns.encode()) + rb'")', rb"\1\2\3", data)
            if data2 == data:
                raise SystemExit(f"no URL import found for {ns}")
            data = data2
    end = re.search(rb"</(?:\w+:)?types>", data)
    blocks = b"".join(b"\n\t\t" + schema_text(f, ns) for ns, f in schemas.items())
    data = data[:end.start()] + blocks + b"\n\t" + data[end.start():]
    left = re.findall(rb'schemaLocation="([^"]*)"', data)
    if left:
        raise SystemExit(f"still external: {left}")
    compile_check(data)
    out.write_bytes(data)


if __name__ == "__main__":
    pairs = dict(a.split("=", 1) for a in sys.argv[3:])
    inline(Path(sys.argv[1]), Path(sys.argv[2]), {k: Path(v) for k, v in pairs.items()})
    print("written", sys.argv[2], "(schema set compiles)")
