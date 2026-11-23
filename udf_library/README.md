# UDF library — reusable Groovy UDFs

**Standard functions first.** A UDF from this library is used only where no standard function does the job safely (CLAUDE.md "Standard functions before UDFs"). A mapping copies the file **unchanged** into its own `scripts/` folder; `build_mapping.py` calls it with `b.udf("<file>", "<function>", …)`.

Each file has a header comment: when to use it, the rules, examples and its origin.

## Entries
| UDF | Signature | Use when | Example | Origin |
|---|---|---|---|---|
| `substringSafe.groovy` | `String substringSafe(String value, String from, String to)` (single value, 0-based, `to` exclusive) | The value may be **shorter** than `to` / `from`, where the standard `substring` fails. Otherwise use the standard `substring`. | `("20261207-20261220","9","17")` → `20261220`; `("ABC","0","5")` → `ABC`; `("ABC","5","8")` → `` | User's reference UDF, ORDRSP feedback 2026-11-15 (also used in SAP PO) |

## iFlow scripts (`iflow/`)
Groovy script steps for iFlows (not mapping UDFs).

| Script | Where in the iFlow | What | Origin |
|---|---|---|---|
| `iflow/PropertiesToHeader.groovy` | Parent, just before the JMS Receiver (SSAB Simplified Pipeline); or before the ProcessDirect call when the parent calls the child directly | If property `SSAB_Dispatcher_CopyPropertiesToHeader` = `Yes` (any case), copies **all** non-null properties as Base64(`java.util.Properties` text) into header `SSAB_Dispatcher_Properties`. Otherwise does nothing. | User, 2026-11-18 (step 1, simplest version) |
| `iflow/HeaderToProperties.groovy` | Child, first step after the ProcessDirect sender | Unpacks `SSAB_Dispatcher_Properties` back into properties, then deletes the header. Does nothing if the header is missing. | User, 2026-11-18 |

Limits (step 1): every value comes back as a String; null properties are skipped. If the header also passes a JMS queue, JMS header size limits apply (exact limit UNVERIFIED).

Why `java.util.Properties` and not JSON (user, 2026-11-18): CPI's design-time General Script Check flags any `JsonSlurper` use as "parsing the message body without streaming", even when it parses a header. `java.util.Properties` `store`/`load` needs no JSON parser, so the check stays clean. Old JSON headers cannot be read by the new child script: update parent and child together.

## Candidates (in mappings; not moved here yet)
| UDF | Where | What |
|---|---|---|
| `removezeros.groovy` | reference CostCentertoMedius, used in ORDERS | Leading zeros off for values that may contain letters (numeric values: `formatNumber '#'`) |
| `toLocalDate.groovy` | NShift (`mappings/5_…/scripts`) | UTC date-time + SAP time zone code → local `yyyy-MM-dd` |
| `groupByHeat.groovy` | DESADV | Interface-specific grouping; probably not reusable as is |
