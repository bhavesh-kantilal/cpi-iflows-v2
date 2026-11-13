"""Semantic diff of two mappings: compares logic per target, ignoring layout (viewData) and uid numbering."""
from __future__ import annotations

from .model import Func, Mapping, Ref, Src


def expr_text(x, defs: dict | None = None) -> str:
    """Readable one-line form. Shared nodes are expanded, so uid numbering does not matter."""
    defs = {} if defs is None else defs
    if x is None:
        return "-"
    if isinstance(x, Ref):
        return defs.get(x.uid, f"<ref {x.uid}>")
    if isinstance(x, Src):
        s = x.path + (f" [ctx {x.context}]" if x.context else "")
    elif x.fname == "const" and x.fns == "dflt" and not x.args:
        s = repr(x.params[0].text if x.params else "")
    else:
        name = x.fname if x.fns == "dflt" else f"{x.fns}::{x.fname}"
        parts = [(f"out{a.out}:" if a.out else "") + expr_text(a.expr, defs) for a in x.args]
        for p in x.params or []:
            v = p.text if p.text is not None else (dict(p.table) if p.table is not None else dict(p.calend))
            parts.append(f"{p.name}={v!r}")
        s = f"{name}({', '.join(parts)})"
    if getattr(x, "uid", None):
        defs[x.uid] = s
    return s


def _targets(m: Mapping) -> dict[str, str]:
    defs: dict = {}
    out = {}
    for t in m.targets:
        flags = (" [disabled]" if t.disabled else "") + (f" [out{t.out}]" if t.out else "")
        out[t.path] = expr_text(t.expr, defs) + flags
    return out


def diff(a: Mapping, b: Mapping) -> list[str]:
    lines = []
    for field in ("source", "target", "udfs", "namespaces", "additional_properties", "blank_xmlns", "label"):
        va, vb = getattr(a, field), getattr(b, field)
        if va != vb:
            lines.append(f"HEADER {field}: {va!r} -> {vb!r}")
    ta, tb = _targets(a), _targets(b)
    for p in ta:
        if p not in tb:
            lines.append(f"REMOVED {p}\n    was: {ta[p]}")
    for p in tb:
        if p not in ta:
            lines.append(f"ADDED   {p}\n    now: {tb[p]}")
        elif ta[p] != tb[p]:
            lines.append(f"CHANGED {p}\n    was: {ta[p]}\n    now: {tb[p]}")
    order_a = [p for p in ta if p in tb]
    order_b = [p for p in tb if p in ta]
    if order_a != order_b:
        lines.append("NOTE target order differs (no effect on logic)")
    return lines
