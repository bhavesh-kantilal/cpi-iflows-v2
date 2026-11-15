"""Write build output: <build>/<Name>.zip + extracted <build>/<Name>/ (FORMAT_NOTES §1.1)."""
from __future__ import annotations

import shutil
import zipfile
from pathlib import Path

import posixpath

from lxml import etree

from .check import FOLDER, relative_imports
from .model import Mapping, render_mmap


def package(m: Mapping, mapping_dir: Path, build_dir: Path) -> Path:
    """mapping_dir holds schemas/ (xsd, wsdl, json files) and scripts/ (groovy) for this mapping."""
    files: list[tuple[str, bytes]] = [(f"mapping/{m.name}.mmap", render_mmap(m).encode("utf-8"))]
    for s in m.udfs:
        files.append((f"script/{s}", _find(mapping_dir, "scripts", s).read_bytes()))
    for lk in (m.source, m.target):
        arc = f"{FOLDER[lk.elems[1]]}/{lk.elems[0]}"
        if arc not in [a for a, _ in files]:
            data = _find(mapping_dir, "schemas", lk.elems[0]).read_bytes()
            files.append((arc, data))
            _add_imports(arc, data, mapping_dir, files)
    build_dir.mkdir(parents=True, exist_ok=True)
    zpath = build_dir / f"{m.name}.zip"
    with zipfile.ZipFile(zpath, "w", zipfile.ZIP_DEFLATED) as z:
        for arc, data in files:
            z.writestr(arc, data)
    out = build_dir / m.name
    if out.exists():
        shutil.rmtree(out)
    for arc, data in files:
        p = out / arc
        p.parent.mkdir(parents=True, exist_ok=True)
        p.write_bytes(data)
    return zpath


def _add_imports(arc: str, data: bytes, mapping_dir: Path, files: list):
    """Pack the files a schema imports by relative schemaLocation, at the path it points to (e.g. a WSDL in wsdl/
    importing ../xsd/X.xsd -> xsd/X.xsd). CPI resolves these from the importing file's folder (FORMAT_NOTES 1.1).
    Source: mapping_dir/schemas/<file> or schemas/downloaded/<file>."""
    for loc in relative_imports(etree.fromstring(data)):
        target = posixpath.normpath(posixpath.join(posixpath.dirname(arc), loc))
        if target.split("/")[0] not in ("xsd", "wsdl") or target.count("/") != 1:
            raise ValueError(f"{arc} imports {loc}: resolves to {target}, outside xsd/ or wsdl/")
        if target in [a for a, _ in files]:
            continue
        name = posixpath.basename(target)
        src = mapping_dir / "schemas" / name
        if not src.exists():
            src = _find(mapping_dir, "schemas/downloaded", name)
        sub = src.read_bytes()
        files.append((target, sub))
        _add_imports(target, sub, mapping_dir, files)


def _find(base: Path, sub: str, name: str) -> Path:
    p = base / sub / name
    if not p.exists():
        raise FileNotFoundError(f"{p} not found (put it in {base / sub})")
    return p
