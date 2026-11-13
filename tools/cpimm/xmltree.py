"""Lossless minimal XML tree for CPI .mmap files.

Keeps attribute order, and whether an empty element was written as
``<a/>`` or ``<a></a>``, so a parsed file can be written back byte for byte.
.mmap files contain no comments, processing instructions, CDATA or prolog.
Those constructs are rejected.
"""
from __future__ import annotations

import re
from dataclasses import dataclass, field

_TOKEN = re.compile(r"<(/?)([A-Za-z_][\w:.-]*)((?:\s+[^\s=/>]+=\"[^\"]*\")*)\s*(/?)>|([^<]+)")
_ATTR = re.compile(r"([^\s=/>]+)=\"([^\"]*)\"")


def unescape(s: str) -> str:
    return (s.replace("&lt;", "<").replace("&gt;", ">").replace("&quot;", '"')
             .replace("&apos;", "'").replace("&amp;", "&"))


def escape_text(s: str) -> str:
    return s.replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;")


def escape_attr(s: str) -> str:
    return s.replace("&", "&amp;").replace("<", "&lt;").replace('"', "&quot;")


@dataclass
class Node:
    tag: str
    attrs: list[tuple[str, str]] = field(default_factory=list)   # unescaped values
    children: list["Node"] = field(default_factory=list)
    text: str | None = None          # unescaped text of a leaf element
    selfclose: bool = False          # only meaningful when empty

    # --- helpers -------------------------------------------------------
    def get(self, name: str, default=None):
        for k, v in self.attrs:
            if k == name:
                return v
        return default

    def find(self, tag: str) -> "Node | None":
        for c in self.children:
            if c.tag == tag:
                return c
        return None

    def findall(self, tag: str) -> list["Node"]:
        return [c for c in self.children if c.tag == tag]

    def iter(self, tag: str | None = None):
        if tag is None or self.tag == tag:
            yield self
        for c in self.children:
            yield from c.iter(tag)


def parse(raw: str) -> Node:
    if raw.startswith("﻿") or raw.startswith("<?") or "<!--" in raw or "<![CDATA[" in raw:
        raise ValueError("unsupported construct (BOM, prolog, comment or CDATA)")
    stack: list[Node] = []
    root: Node | None = None
    pos = 0
    for m in _TOKEN.finditer(raw):
        if m.start() != pos:
            raise ValueError(f"unparsable content at offset {pos}")
        pos = m.end()
        closing, tag, attrs, selfc, text = m.groups()
        if text is not None:
            if not stack:
                raise ValueError("text outside root element")
            cur = stack[-1]
            if cur.children:
                raise ValueError(f"mixed content in <{cur.tag}>")
            cur.text = (cur.text or "") + unescape(text)
            continue
        if closing:
            node = stack.pop()
            if node.tag != tag:
                raise ValueError(f"mismatched </{tag}> for <{node.tag}>")
            continue
        node = Node(tag, [(k, unescape(v)) for k, v in _ATTR.findall(attrs)], selfclose=bool(selfc))
        if stack:
            if stack[-1].text is not None:
                raise ValueError(f"mixed content in <{stack[-1].tag}>")
            stack[-1].children.append(node)
        elif root is None:
            root = node
        else:
            raise ValueError("multiple root elements")
        if not selfc:
            stack.append(node)
    if pos != len(raw) or stack or root is None:
        raise ValueError("truncated or empty document")
    return root


def write(node: Node) -> str:
    out: list[str] = []
    _write(node, out)
    return "".join(out)


def _write(n: Node, out: list[str]) -> None:
    attrs = "".join(f' {k}="{escape_attr(v)}"' for k, v in n.attrs)
    if not n.children and not n.text:
        out.append(f"<{n.tag}{attrs}/>" if n.selfclose else f"<{n.tag}{attrs}></{n.tag}>")
        return
    out.append(f"<{n.tag}{attrs}>")
    if n.text:
        out.append(escape_text(n.text))
    for c in n.children:
        _write(c, out)
    out.append(f"</{n.tag}>")


def E(tag: str, *children: Node, attrs=None, text: str | None = None, sc: bool = True) -> Node:
    """Build helper: E('a', E('b'), attrs=[('x','1')]). Empty elements self-close unless sc=False."""
    return Node(tag, list(attrs or []), list(children), text, sc)
