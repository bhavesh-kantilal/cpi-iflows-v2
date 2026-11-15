"""Schema path index + build checks (CLAUDE.md "Checks before finishing a build")."""
from __future__ import annotations

import posixpath
import re
import zipfile
from pathlib import Path

from lxml import etree

from .model import Func, Mapping, Ref, Src, read_mmap

XS = "{http://www.w3.org/2001/XMLSchema}"
FOLDER = {"src/main/resources/xsd": "xsd", "src/main/resources/wsdl": "wsdl",
          "src/main/resources/json": "json", "src/main/resources/script": "script"}
FORBIDDEN = re.compile(rb"claude|anthropic", re.I)


# ----------------------------------------------------------------------------- schema index
def relative_imports(root) -> list[str]:
    """schemaLocation values of <import>/<include> that are relative file paths (not http/https URLs).
    CPI resolves them from the importing file's own folder (NShift TestC/TestD, 2026-11-15); it does not fetch URLs."""
    locs = []
    for tag in ("import", "include"):
        for e in root.iter(XS + tag):
            loc = e.get("schemaLocation")
            if loc and not re.match(r"[a-zA-Z][a-zA-Z0-9+.-]*://", loc):
                locs.append(loc)
    return locs


def _schemas(path: Path, _seen: set | None = None):
    """Schemas of an XSD or WSDL file, plus the files it imports by relative schemaLocation (recursively)."""
    seen = set() if _seen is None else _seen
    path = path.resolve()
    if path in seen:
        return []
    seen.add(path)
    root = etree.parse(str(path)).getroot()
    found = [root] if root.tag == XS + "schema" else root.findall(".//" + XS + "schema")   # WSDL: embedded
    for loc in relative_imports(root):
        p = path.parent / loc
        if p.exists():
            found += _schemas(p, seen)
    return found


def schema_paths(path: Path, root_name: str, max_depth: int = 40) -> set[str]:
    """All element/attribute paths (local names, no prefixes) below global element root_name."""
    schemas = _schemas(path)
    gel, gct, ggrp, gag, gst = {}, {}, {}, {}, {}
    for s in schemas:
        for e in s:
            n = e.get("name")
            {XS + "element": gel, XS + "complexType": gct, XS + "group": ggrp,
             XS + "attributeGroup": gag, XS + "simpleType": gst}.get(e.tag, {}).__setitem__(n, e) if n else None
    loc = lambda q: q.split(":")[-1] if q else q
    out: set[str] = set()

    def walk_type(ct, prefix, depth, stack):
        if ct is None or depth > max_depth:
            return
        for c in ct.iter():
            pass
        _content(ct, prefix, depth, stack)

    def _content(node, prefix, depth, stack):
        for c in node:
            tag = c.tag
            if tag in (XS + "sequence", XS + "choice", XS + "all", XS + "complexContent", XS + "simpleContent"):
                _content(c, prefix, depth, stack)
            elif tag in (XS + "extension", XS + "restriction"):
                base = gct.get(loc(c.get("base")))
                if base is not None and base not in stack:
                    _content(base, prefix, depth, stack + [base])
                _content(c, prefix, depth, stack)
            elif tag == XS + "group":
                g = ggrp.get(loc(c.get("ref")))
                if g is not None:
                    _content(g, prefix, depth, stack)
            elif tag == XS + "attribute":
                n = c.get("name") or loc(c.get("ref"))
                out.add(f"{prefix}/@{n}")
            elif tag == XS + "attributeGroup":
                g = gag.get(loc(c.get("ref")))
                if g is not None:
                    _content(g, prefix, depth, stack)
            elif tag == XS + "element":
                elem(c, prefix, depth + 1, stack)

    def elem(e, prefix, depth, stack):
        if e.get("ref"):
            ref = gel.get(loc(e.get("ref")))
            if ref is None:
                return
            e = ref
        p = f"{prefix}/{e.get('name')}"
        out.add(p)
        if depth > max_depth:
            return
        ct = e.find(XS + "complexType")
        if ct is None and e.get("type"):
            ct = gct.get(loc(e.get("type")))
        if ct is not None and ct not in stack:
            _content(ct, p, depth, stack + [ct])

    r = gel.get(root_name)
    if r is None:
        raise ValueError(f"root element {root_name} not found in {path.name}")
    elem(r, "", 0, [])
    return out


_IDX = re.compile(r"\[\d+\]")


def norm(path: str) -> str:
    """Strip namespace prefixes and duplicate-subtree indexes: /ns0:A/b[2]/@c -> /A/b/@c"""
    return "/".join(_IDX.sub("", s.split(":")[-1]) if not s.startswith("@") else s for s in path.split("/"))


# ----------------------------------------------------------------------------- checks
def walk(x):
    yield x
    if isinstance(x, Func):
        for a in x.args:
            yield from walk(a.expr)


def check_paths(m: Mapping, folder: Path) -> list[str]:
    errs = []
    sides = {"source": m.source, "target": m.target}
    idx = {}
    for side, lk in sides.items():
        if lk.type_id == "json":
            idx[side] = None
            continue
        f = folder / FOLDER[lk.elems[1]] / lk.elems[0]
        if not f.exists():
            errs.append(f"{side} schema missing: {f}")
            idx[side] = None
            continue
        idx[side] = {norm(p) for p in schema_paths(f, lk.elems[2])}
    used_src, used_ctx = set(), set()
    for t in m.targets:
        if idx["target"] is not None and norm(t.path) not in idx["target"]:
            errs.append(f"target path not in schema: {t.path}")
        if t.expr is not None:
            for n in walk(t.expr):
                if isinstance(n, Src):
                    used_src.add(n.path)
                    if n.context:
                        used_ctx.add(n.context)
    if idx["source"] is not None:
        for p in sorted(used_src | used_ctx):
            if norm(p) not in idx["source"]:
                errs.append(f"source path not in schema: {p}")
    for side in sides:
        if idx[side] is None and sides[side].type_id == "json":
            errs.append(f"NOTE {side} is JSON: path check not implemented yet (manual check needed)")
    return errs


XSD_NS = "http://www.w3.org/2001/XMLSchema"


def schema_ref_errors(data: bytes, imported: list[bytes] | None = None) -> list[str]:
    """Every type=/ref=/base= QName in the file's schemas must resolve, with its prefix bound in scope, to a
    definition of that namespace in the same file (or to the XSD namespace).
    Catches lost prefix declarations, e.g. 'tns' re-bound when schemas were inlined into a WSDL
    (NShift v1.0.0: CPI showed an empty Consignment). Path checks match by local name only and miss this."""
    def schemas_of(b):
        r = etree.fromstring(b)
        return [r] if r.tag == f"{{{XSD_NS}}}schema" else list(r.iter(f"{{{XSD_NS}}}schema"))
    schemas = schemas_of(data)
    pool = schemas + [s for b in (imported or []) for s in schemas_of(b)]   # definitions from imported files
    defs: dict[str | None, set[tuple[str, str]]] = {}
    for s in pool:
        tns = s.get("targetNamespace")
        for kind in ("complexType", "simpleType", "element", "group", "attributeGroup", "attribute"):
            for d in s.findall(f"{{{XSD_NS}}}{kind}"):
                cat = "type" if kind in ("complexType", "simpleType") else kind
                defs.setdefault(tns, set()).add((cat, d.get("name")))
    errs, seen = [], set()
    for s in schemas:
        for e in s.iter(f"{{{XSD_NS}}}*"):
            for attr in ("type", "ref", "base"):
                v = e.get(attr)
                if not v:
                    continue
                prefix, _, local = v.rpartition(":")
                ns = e.nsmap.get(prefix or None)
                if ns == XSD_NS:
                    continue
                if attr == "ref":
                    cat = {"element": "element", "attribute": "attribute", "group": "group",
                           "attributeGroup": "attributeGroup"}.get(etree.QName(e).localname, "element")
                else:
                    cat = "type"
                if (cat, local) not in defs.get(ns, set()):
                    key = (attr, v, ns)
                    if key not in seen:
                        seen.add(key)
                        errs.append(f"unresolved {attr}='{v}' (prefix bound to {ns}) in schema {s.get('targetNamespace')}")
    return errs


def layout_overlaps(m: Mapping) -> list[str]:
    """No two bricks on one editor canvas (a group of targets, or a single target) at the same x/y
    (user feedback ORDRSP 2026-11-15: overlapping bricks make the mapping unreadable)."""
    canvases: dict[str, list] = {}
    for i, t in enumerate(m.targets):
        canvases.setdefault(t.group or f"#{i}", []).append(t)
    errs = []
    for name, ts in canvases.items():
        seen: dict[tuple, str] = {}
        for t in ts:
            bricks = [(t.xy, f"target {t.path}")] if t.expr is not None else []
            if t.expr is not None:
                bricks += [(n.xy, f"{getattr(n, 'fname', None) or n.path} in {t.path}")
                           for n in walk(t.expr) if isinstance(n, (Func, Src)) and n.xy]
            for xy, what in bricks:
                if xy in seen:
                    errs.append(f"layout overlap at {xy}: {what} / {seen[xy]}")
                else:
                    seen[xy] = what
    return errs


def check_build(zip_path: Path, name: str) -> list[str]:
    """Zip structure like the standalone references + well-formed XML + no forbidden strings."""
    errs = []
    with zipfile.ZipFile(zip_path) as z:
        names = z.namelist()
        for i in z.infolist():
            if i.is_dir():
                errs.append(f"directory entry in zip: {i.filename}")
            if i.compress_type != zipfile.ZIP_DEFLATED:
                errs.append(f"not deflated: {i.filename}")
            top = i.filename.split("/")[0]
            if top not in ("mapping", "script", "xsd", "wsdl", "json") or i.filename.count("/") != 1:
                errs.append(f"unexpected zip entry: {i.filename}")
        mm = [n for n in names if n.startswith("mapping/")]
        if mm != [f"mapping/{name}.mmap"]:
            errs.append(f"mapping/ must hold exactly {name}.mmap, found {mm}")
            return errs
        raw = z.read(mm[0])
        try:
            m = read_mmap(raw.decode("utf-8"), name)          # also proves the envelope is standard
        except Exception as e:                                # noqa: BLE001
            errs.append(f".mmap not readable/standard: {e}")
            return errs
        errs += layout_overlaps(m)
        for s in m.udfs:
            if f"script/{s}" not in names:
                errs.append(f"declared UDF script missing: script/{s}")
        for lk in (m.source, m.target):
            want = f"{FOLDER[lk.elems[1]]}/{lk.elems[0]}"
            if want not in names:
                errs.append(f"schema missing in zip: {want}")
        for n in names:
            data = z.read(n)
            if FORBIDDEN.search(data):
                errs.append(f"forbidden string (claude/anthropic) in {n}")
            if n.endswith((".xsd", ".wsdl", ".WSDL", ".mmap")):
                try:
                    etree.fromstring(data)
                except etree.XMLSyntaxError as e:
                    errs.append(f"not well-formed: {n}: {e}")
                    continue
            if n.endswith((".xsd", ".wsdl", ".WSDL")):
                imported = []
                for loc in relative_imports(etree.fromstring(data)):
                    target = posixpath.normpath(posixpath.join(posixpath.dirname(n), loc))
                    if target in names:
                        imported.append(z.read(target))
                    else:
                        errs.append(f"{n}: imports {loc} -> {target}, not in the zip")
                errs += [f"{n}: {e}" for e in schema_ref_errors(data, imported)]
        if raw.startswith(b"\xef\xbb\xbf") or b"\n" in raw or raw.startswith(b"<?"):
            errs.append(".mmap must be one line, no BOM, no prolog")
    return errs
