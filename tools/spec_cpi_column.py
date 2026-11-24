"""
tools/spec_cpi_column.py
Write a new version of a mapping-spec workbook with a "Current CPI mapping" column, filled only on
rows where the CPI mapping differs from the spec. Those cells and the row's rule cell are highlighted.
The input workbook is never changed.

Usage:
  py -I tools/spec_cpi_column.py <in.xlsx> <out.xlsx> <notes.json>

notes.json:
  {"sheet": "Mapping", "key_col": 1, "rule_col": 5, "header_row": 1,
   "version": "v2 · 24 Nov 2026", "overview_note": "...",
   "rows": {"14": "CPI text", ...}}       # keys = values of key_col (the spec's row number #)
"""
import copy
import json
import sys

import openpyxl
from openpyxl.styles import PatternFill

sys.stdout.reconfigure(encoding="utf-8")
FILL = PatternFill("solid", fgColor="FFF4B183")     # orange: CPI differs from the spec
HEADER = "Current CPI mapping"


def main(src: str, dst: str, notes_path: str) -> None:
    with open(notes_path, encoding="utf-8") as f:
        notes = json.load(f)
    wb = openpyxl.load_workbook(src)
    ws = wb[notes.get("sheet", "Mapping")]
    key_col, rule_col, hr = notes.get("key_col", 1), notes.get("rule_col", 5), notes.get("header_row", 1)
    col = ws.max_column + 1
    if ws.cell(hr, col - 1).value == HEADER:
        col -= 1
    head = ws.cell(hr, col)
    head.value = HEADER
    head._style = copy.copy(ws.cell(hr, col - 1)._style)
    ws.column_dimensions[openpyxl.utils.get_column_letter(col)].width = 55
    rows = {str(k): v for k, v in notes["rows"].items()}
    done = set()
    for r in range(hr + 1, ws.max_row + 1):
        key = ws.cell(r, key_col).value
        ref = ws.cell(r, rule_col)
        c = ws.cell(r, col)
        c._style = copy.copy(ref._style)
        if key is not None and str(key) in rows:
            c.value = rows[str(key)]
            c.fill = FILL
            ref.fill = FILL
            done.add(str(key))
    missing = set(rows) - done
    if missing:
        sys.exit(f"rows not found in {ws.title}: {sorted(missing)}")
    if "Overview" in wb.sheetnames and notes.get("version"):
        ov = wb["Overview"]
        ov.cell(2, 1).value = notes["version"]
        if notes.get("overview_note"):
            r = ov.max_row + 2
            ov.cell(r, 1).value = "Version note"
            ov.cell(r, 2).value = notes["overview_note"]
            ov.cell(r, 1)._style = copy.copy(ov.cell(4, 1)._style)
            ov.cell(r, 2)._style = copy.copy(ov.cell(4, 2)._style)
    wb.save(dst)
    print(f"wrote {dst}: {len(done)} rows marked")


if __name__ == "__main__":
    main(*sys.argv[1:4])
