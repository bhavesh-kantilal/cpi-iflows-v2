"""Report SSAB best-practice FLAGs (iflow_lib.best_practice_flags) for built iFlow zips.

Usage: py -I tools/check_best_practices.py [zip ...]   (default: every iflows/**/build/*.zip)
FLAGs are not failures: existing flows are reported, not changed. Rules: CLAUDE.md
"SSAB Best Practises" and the PDF sections named in each flag.
"""
import glob
import os
import sys
import zipfile

sys.stdout.reconfigure(encoding="utf-8")
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import iflow_lib  # noqa: E402

PROP = "src/main/resources/parameters.prop"


def long_path(p: str) -> str:
    """Windows paths over 260 characters need the extended-length prefix (I2023/I2024 names)."""
    p = os.path.abspath(p)
    return "\\\\?\\" + p if os.name == "nt" else p


def main() -> None:
    zips = sys.argv[1:] or sorted(glob.glob(os.path.join("iflows", "**", "build", "*.zip"), recursive=True))
    total = 0
    for zp in zips:
        with zipfile.ZipFile(long_path(zp)) as z:
            names = z.namelist()
            iflw = next((n for n in names if n.endswith(".iflw")), None)
            if not iflw:
                continue
            prop = z.read(PROP).decode("utf-8") if PROP in names else None
            flags = iflow_lib.best_practice_flags(z.read(iflw).decode("utf-8"), prop)
        total += len(flags)
        print(f"{'OK  ' if not flags else 'FLAG'}  {os.path.splitext(os.path.basename(zp))[0]}")
        for f in flags:
            print(f"      {f}")
    print(f"\n{total} flag(s)")


if __name__ == "__main__":
    main()
