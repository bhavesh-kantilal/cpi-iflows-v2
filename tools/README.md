# tools/: iFlow builders and checks

Python 3.12 with `lxml`. Always run with `py -I` (isolated mode), from the repo root.
The mapping toolkit (`cpimm`, `mm.py`, `catalog.py`, …) is in the mapping repo: `cpi-mappings-v2/tools/`.

| File | What it does |
|---|---|
| `iflow_lib.py` | Shared library: parse/serialize, `fix_diagram`, `sync_flow_refs`, `externalize`, `Params` (parameters.prop + propdef), `check_iflow`, `script_parse_errors`, `best_practice_flags` |
| `iflow_build_fsap_dispatcher.py` | FSAP Controlling iFlows and the Medius / StreamServe dispatchers. `--only <IFlowName> …` |
| `iflow_build_smarteam.py` | SmarTeam parents and children. `--all`, `--only <IFlowName> …`, `--selftest` (jar → design-time conversion) |
| `iflow_build_tibnor.py` | Tibnor ORDERS parent + child. `--only parent\|child`. Reads the mapping zip from `cpi-mappings-v2/mappings/…/build/` |
| `iflow_build_tibnor_inbound.py` | Tibnor ORDRSP / DESADV / INVOIC parents + mill children. `--flow ORDRSP\|DESADV\|INVOIC [--only …]`. Reads the mapping zips from `cpi-mappings-v2/mappings/` |
| `iflow_add_request_reply.py` | One-off: inserted the Request-Reply block into a SmarTeam iFlow |
| `iflow_import.py` | Extracts new iFlow exports in `_reference/iflows/` |
| `iflow_render.py` | `py -I tools/iflow_render.py <zip> <out.svg>`: draws the diagram for a quick visual check |
| `check_all_iflows.py` | Checks every built iFlow zip: well-formed XML, diagram and wiring, parameters, no AI strings, MANIFEST name, Groovy streaming, best-practice FLAGs. Must say `All OK` |
| `check_best_practices.py` | Best-practice FLAGs only |
| `spot_check_iflows.py` | One-time spot checks of the FSAP dispatcher migration |

**Customer values:** the builders still contain SSAB values (roles, queue names, participant names, step names). The list is in `.claude/skills/ssab-tibnor/SKILL.md`, "Where the code enforces SSAB values". For another customer, don't run them unchanged (CLAUDE.md "Which customer?").
