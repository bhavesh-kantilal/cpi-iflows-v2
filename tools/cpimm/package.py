"""Write build output: <build>/<Name>.zip + extracted <build>/<Name>/ (FORMAT_NOTES §1.1)."""
from __future__ import annotations

import shutil
import zipfile
from pathlib import Path

from .check import FOLDER
from .model import Mapping, render_mmap


def package(m: Mapping, mapping_dir: Path, build_dir: Path) -> Path:
    """mapping_dir holds schemas/ (xsd, wsdl, json files) and scripts/ (groovy) for this mapping."""
    files: list[tuple[str, bytes]] = [(f"mapping/{m.name}.mmap", render_mmap(m).encode("utf-8"))]
    for s in m.udfs:
        files.append((f"script/{s}", _find(mapping_dir, "scripts", s).read_bytes()))
    for lk in (m.source, m.target):
        arc = f"{FOLDER[lk.elems[1]]}/{lk.elems[0]}"
        if arc not in [a for a, _ in files]:
            files.append((arc, _find(mapping_dir, "schemas", lk.elems[0]).read_bytes()))
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


def _find(base: Path, sub: str, name: str) -> Path:
    p = base / sub / name
    if not p.exists():
        raise FileNotFoundError(f"{p} not found (put it in {base / sub})")
    return p
