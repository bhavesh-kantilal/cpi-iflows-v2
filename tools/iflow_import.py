"""Import iFlow exports dropped into _reference/iflows/ (CLAUDE.md "learn new references").

    py -I tools/iflow_import.py

For every zip in _reference/iflows/ that is not yet extracted:
  * the iFlow name is taken from INSIDE the zip: a single top folder (package export "<Package>_artifacts (n).zip")
    or, for an export without a wrapper folder, the zip name without " (n)";
  * a new iFlow is stored as _reference/iflows/<iFlowName>.zip (entries at the root, like the existing exports)
    and extracted to _reference/iflows/<iFlowName>/;
  * a duplicate of an iFlow we already have: files that differ are taken over (newer export), the zip is removed,
    and the change is reported.
Windows paths longer than 260 characters (e.g. OData .edmx file names) are written with the long-path prefix.
"""
from __future__ import annotations

import os
import re
import sys
import zipfile
from pathlib import Path

sys.stdout.reconfigure(encoding="utf-8")
DIR = Path(__file__).resolve().parent.parent / "_reference" / "iflows"
LONG = "\\\\?\\"


def lp(p: Path) -> str:
    s = str(p.resolve())
    return LONG + s if os.name == "nt" and not s.startswith(LONG) else s


def main() -> int:
    known = {d.name for d in DIR.iterdir() if d.is_dir()}
    done: dict[str, str] = {}
    for z in sorted(DIR.glob("*.zip")):
        if z.stem in known:
            continue
        with zipfile.ZipFile(z) as zf:
            names = [n for n in zf.namelist() if not n.endswith("/")]
            tops = {n.split("/")[0] for n in names}
            wrapped = len(tops) == 1 and all("/" in n for n in names) and next(iter(tops)) not in ("src", "META-INF")
            name = next(iter(tops)) if wrapped else re.sub(r" \(\d+\)$", "", z.stem)
            files = {(n.split("/", 1)[1] if wrapped else n): zf.read(n) for n in names}
        target = DIR / name
        if target.is_dir() or name in done:
            changed = []
            for rel, data in files.items():
                p = lp(target / rel)
                if not os.path.exists(p) or open(p, "rb").read() != data:
                    changed.append(rel)
                    os.makedirs(os.path.dirname(p), exist_ok=True)
                    with open(p, "wb") as fh:
                        fh.write(data)
            os.remove(lp(z))
            print(f"DUP  {z.name} -> {name}: took over {changed or 'nothing (identical)'}; zip removed")
            continue
        out = DIR / f"{name}.zip"
        with zipfile.ZipFile(lp(out), "w", zipfile.ZIP_DEFLATED) as w:
            for rel, data in files.items():
                w.writestr(rel, data)
        for rel, data in files.items():
            p = lp(target / rel)
            os.makedirs(os.path.dirname(p), exist_ok=True)
            with open(p, "wb") as fh:
                fh.write(data)
        if out.name != z.name:
            os.remove(lp(z))
        done[name] = z.name
        print(f"NEW  {z.name} -> {name}.zip | mappings: {[r.split('/')[-1] for r in files if r.endswith('.mmap')]}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
