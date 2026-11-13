"""CPI mapping toolkit CLI.

  py -I tools/mm.py selftest              round-trip + path check on every reference mapping
  py -I tools/mm.py check <zip> <Name>    structure checks on a built zip
  py -I tools/mm.py paths <mmap> <folder> path checks of an .mmap against <folder>/xsd|wsdl
"""
from __future__ import annotations

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
sys.stdout.reconfigure(encoding="utf-8")

from cpimm.check import check_build, check_paths          # noqa: E402
from cpimm.model import FormatError, load                 # noqa: E402

REPO = Path(__file__).resolve().parent.parent
KNOWN_LEGACY = {"MapSpecialTaxCases.mmap"}   # older envelope, orphan in I0115 (FORMAT_NOTES §2.1)


def selftest() -> int:
    seen, fails = set(), 0
    for p in sorted((REPO / "_reference").rglob("*.mmap")):
        data = p.read_bytes()
        if data in seen:
            continue
        seen.add(data)
        try:
            m = load(p)
        except FormatError as e:
            if p.name in KNOWN_LEGACY:
                print(f"SKIP {p.name}: known legacy envelope")
                continue
            fails += 1
            print(f"FAIL {p.name}: {e}")
            continue
        # schemas live next to mapping/ (standalone export) or in src/main/resources (iFlow export)
        folder = p.parent.parent
        errs = [e for e in check_paths(m, folder) if not e.startswith("NOTE")]
        status = "OK  " if not errs else "PATH"
        print(f"{status} {p.name}: byte-identical round-trip, {len(m.targets)} targets"
              + (f", {len(errs)} path issues" if errs else ""))
        for e in errs[:5]:
            print("      ", e)
    print("selftest:", "PASSED" if not fails else f"{fails} FAILED")
    return 1 if fails else 0


def main(argv):
    if argv[:1] == ["selftest"]:
        return selftest()
    if argv[:1] == ["check"] and len(argv) == 3:
        errs = check_build(Path(argv[1]), argv[2])
        print("\n".join(errs) or "build checks PASSED")
        return 1 if errs else 0
    if argv[:1] == ["paths"] and len(argv) == 3:
        errs = check_paths(load(argv[1]), Path(argv[2]))
        print("\n".join(errs) or "path checks PASSED")
        return 1 if [e for e in errs if not e.startswith("NOTE")] else 0
    print(__doc__)
    return 2


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
