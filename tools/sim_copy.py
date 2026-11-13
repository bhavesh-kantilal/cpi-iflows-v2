"""Make a simulator copy of a sample payload: <name>_sim.xml next to the original.

    py -I tools/sim_copy.py <file.xml> [...]

The CPI mapping simulator fails on a root element that declares xmlns:xsi and uses xsi:* attributes
(`The prefix "ns6" for attribute "ns6:schemaLocation" ... is not bound`, ORDRSP 2026-11-13, CLAUDE.md).
The copy is byte-identical to the original except that those attributes are removed from the root start tag.
The original is never changed.
"""
import re
import sys
from pathlib import Path

from lxml import etree

sys.stdout.reconfigure(encoding="utf-8")
XSI = re.compile(rb'\s+(xmlns:xsi|xsi:[A-Za-z]+)="[^"]*"')


def sim_copy(src: Path) -> Path | None:
    data = src.read_bytes()
    root = re.search(rb"<(?![?!])[^>]*>", data)                 # first element start tag
    tag = root.group(0)
    new_tag = XSI.sub(b"", tag)
    if new_tag == tag:
        return None
    out = src.with_name(src.stem + "_sim.xml")
    new = data[:root.start()] + new_tag + data[root.end():]
    etree.fromstring(new)                                       # still well-formed
    out.write_bytes(new)
    return out


if __name__ == "__main__":
    for a in sys.argv[1:]:
        p = Path(a)
        if p.stem.endswith("_sim"):
            continue
        r = sim_copy(p)
        print(f"{p.name}: " + (f"-> {r.name}" if r else "no xsi attributes on the root, no copy needed"))
