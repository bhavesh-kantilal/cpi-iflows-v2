"""Render an iFlow's BPMN diagram (shapes + edges) to a simple SVG for a quick visual check.

Usage: py -I tools/iflow_render.py <iflow.zip|.iflw> <out.svg>
"""
import sys
import zipfile
from html import escape

from lxml import etree

sys.stdout.reconfigure(encoding="utf-8")
NS = {
    "bpmn2": "http://www.omg.org/spec/BPMN/20100524/MODEL",
    "bpmndi": "http://www.omg.org/spec/BPMN/20100524/DI",
    "dc": "http://www.omg.org/spec/DD/20100524/DC",
    "di": "http://www.omg.org/spec/DD/20100524/DI",
}


def load(path: str) -> bytes:
    if path.endswith(".zip"):
        z = zipfile.ZipFile(path)
        return z.read(next(n for n in z.namelist() if n.endswith(".iflw")))
    return open(path, "rb").read()


def render(xml: bytes) -> str:
    root = etree.fromstring(xml)
    names = {e.get("id"): (etree.QName(e).localname, e.get("name") or "") for e in root.iter() if e.get("id")}
    plane = root.find(".//bpmndi:BPMNPlane", NS)
    parts, xs, ys = [], [], []
    for s in plane.findall("bpmndi:BPMNShape", NS):
        b = s.find("dc:Bounds", NS)
        x, y, w, h = (float(b.get(k)) for k in ("x", "y", "width", "height"))
        xs += [x, x + w]; ys += [y, y + h]
        kind, name = names.get(s.get("bpmnElement"), ("?", "?"))
        if kind == "participant":
            parts.append(f'<rect x="{x}" y="{y}" width="{w}" height="{h}" fill="none" stroke="#888"/>'
                         f'<text x="{x + w / 2}" y="{y + 14}" font-size="11" text-anchor="middle">{escape(name)}</text>')
        elif kind.endswith("Event"):
            parts.append(f'<circle cx="{x + w / 2}" cy="{y + h / 2}" r="{w / 2}" fill="#fff" stroke="#333"/>'
                         f'<text x="{x + w / 2}" y="{y + h + 12}" font-size="9" text-anchor="middle">{escape(name)}</text>')
        elif kind.endswith("Gateway"):
            parts.append(f'<polygon points="{x + w / 2},{y} {x + w},{y + h / 2} {x + w / 2},{y + h} {x},{y + h / 2}" fill="#fff" stroke="#333"/>')
        else:
            parts.append(f'<rect x="{x}" y="{y}" width="{w}" height="{h}" fill="#e8f1fb" stroke="#36c"/>'
                         f'<text x="{x + w / 2}" y="{y + h / 2 + 3}" font-size="9" text-anchor="middle">{escape(name[:22])}</text>')
    for e in plane.findall("bpmndi:BPMNEdge", NS):
        pts = [(float(w.get("x")), float(w.get("y"))) for w in e.findall("di:waypoint", NS)]
        kind = names.get(e.get("bpmnElement"), ("?",))[0]
        dash = ' stroke-dasharray="4 3"' if kind == "messageFlow" else ""
        parts.append(f'<polyline points="{" ".join(f"{a},{b}" for a, b in pts)}" fill="none" '
                     f'stroke="#c00" stroke-width="1.5" marker-end="url(#a)"{dash}/>')
    x0, y0 = min(xs) - 20, min(ys) - 20
    w, h = max(xs) - x0 + 20, max(ys) - y0 + 20
    return (f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="{x0} {y0} {w} {h}" width="{w}" height="{h}" '
            f'style="background:#fff;font-family:sans-serif">'
            '<defs><marker id="a" markerWidth="8" markerHeight="8" refX="7" refY="4" orient="auto">'
            '<path d="M0,0 L8,4 L0,8 z" fill="#c00"/></marker></defs>' + "".join(parts) + "</svg>")


if __name__ == "__main__":
    open(sys.argv[2], "w", encoding="utf-8").write(render(load(sys.argv[1])))
    print(sys.argv[2])
