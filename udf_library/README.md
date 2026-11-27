# Script library: reusable iFlow Groovy scripts

Groovy script steps for iFlows. The mapping UDFs (e.g. `substringSafe`) are in the mapping repo: `cpi-mappings-v2/udf_library/`.

## iFlow scripts (`iflow/`)
**Customer-specific: SSAB / Tibnor** (header and property names `SSAB_Dispatcher_…`). For another customer, ask before reusing them.

| Script | Where in the iFlow | What | Origin |
|---|---|---|---|
| `iflow/PropertiesToHeader.groovy` | Parent, just before the JMS Receiver (SSAB Simplified Pipeline); or before the ProcessDirect call when the parent calls the child directly | If property `SSAB_Dispatcher_CopyPropertiesToHeader` = `Yes` (any case), copies **all** non-null properties as Base64(`java.util.Properties` text) into header `SSAB_Dispatcher_Properties`. Otherwise does nothing. | User, 2026-11-18 (step 1, simplest version) |
| `iflow/HeaderToProperties.groovy` | Child, first step after the ProcessDirect sender | Unpacks `SSAB_Dispatcher_Properties` back into properties, then deletes the header. Does nothing if the header is missing. | User, 2026-11-18 |

Limits (step 1): every value comes back as a String; null properties are skipped. If the header also passes a JMS queue, JMS header size limits apply (exact limit UNVERIFIED).

Why `java.util.Properties` and not JSON (user, 2026-11-18): CPI's design-time General Script Check flags any `JsonSlurper` use as "parsing the message body without streaming", even when it parses a header. `java.util.Properties` `store`/`load` needs no JSON parser, so the check stays clean. Old JSON headers cannot be read by the new child script: update parent and child together.
