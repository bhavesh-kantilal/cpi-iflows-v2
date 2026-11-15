# UDF library — reusable Groovy UDFs

**Standard functions first.** A UDF from this library is used only where no standard function does the job safely (CLAUDE.md "Standard functions before UDFs"). A mapping copies the file **unchanged** into its own `scripts/` folder; `build_mapping.py` calls it with `b.udf("<file>", "<function>", …)`.

Each file has a header comment: when to use it, the rules, examples and its origin.

## Entries
| UDF | Signature | Use when | Example | Origin |
|---|---|---|---|---|
| `substringSafe.groovy` | `String substringSafe(String value, String from, String to)` (single value, 0-based, `to` exclusive) | The value may be **shorter** than `to` / `from`, where the standard `substring` fails. Otherwise use the standard `substring`. | `("20261207-20261220","9","17")` → `20261220`; `("ABC","0","5")` → `ABC`; `("ABC","5","8")` → `` | User's reference UDF, ORDRSP feedback 2026-11-15 (also used in SAP PO) |

## Candidates (in mappings; not moved here yet)
| UDF | Where | What |
|---|---|---|
| `removezeros.groovy` | reference CostCentertoMedius, used in ORDERS | Leading zeros off for values that may contain letters (numeric values: `formatNumber '#'`) |
| `toLocalDate.groovy` | NShift (`mappings/5_…/scripts`) | UTC date-time + SAP time zone code → local `yyyy-MM-dd` |
| `groupByHeat.groovy` | DESADV | Interface-specific grouping; probably not reusable as is |
