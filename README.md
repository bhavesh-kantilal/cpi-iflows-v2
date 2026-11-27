# CPI iFlows

SAP Cloud Integration **iFlows**, built as importable zips by scripts, tested in CPI by the user, and improved from the user's feedback. Every version is a git tag, and every iFlow has a `spec.md` and a CHANGELOG.

- **How iFlows are built is generic** (CLAUDE.md). **How a customer organizes and names them** is in a customer skill.
  - So far: SSAB / Tibnor, one CPI tenant.
- The mapping repo **`cpi-mappings-v2`** is included as the git submodule `cpi-mappings-v2/`, so mapping work is always possible from here.
- Split from the old repo `cpi-mappings` on 2026-11-27, with the full history.

## What to read, in this order
| # | File | What it holds | Changed by |
|---|---|---|---|
| 1 | [`CLAUDE.md`](CLAUDE.md) | **The generic rules**: how to work, the customer checklist, how iFlows are built and checked. Loaded at the start of every session. | Only with the user's approval |
| 2 | [`.claude/skills/ssab-tibnor/SKILL.md`](.claude/skills/ssab-tibnor/SKILL.md) | **SSAB / Tibnor conventions**: the answers to the customer checklist, each marked "generic pattern, SSAB value" or "SSAB only". Claude loads it only for SSAB / Tibnor work. | Only with the user's approval |
| 3 | [`REVIEW.md`](REVIEW.md) | **Waiting room**: open proposals, plus the history of applied lessons | The user decides |
| 4 | [`_reference/IFLOW_CONVENTIONS.md`](_reference/IFLOW_CONVENTIONS.md) | SSAB patterns and naming in detail, with sources | Only with the user's approval |
| 5 | [`docs/explained/`](docs/explained) | Background: [SSAB Best Practises guide summary](docs/explained/ssab_best_practices_guide.md), [JMS dispatcher architecture](docs/explained/jms_dispatcher_architecture.md), [reference iFlow scan](docs/explained/iflow_scan_findings.md), [diagram and externalization](docs/explained/iflow_diagram_and_externalization.md) | Claude |
| 6 | `iflows/<Package>/<IFlowName>/spec.md` | Per iFlow: purpose, parameters, every decision | Claude, from the user's answers |

The rest of the repo:
- [`_reference/iflows/`](_reference/README.md): the user's iFlow exports (L1, SSAB).
- [`tools/`](tools/README.md): the iFlow builders and checks.
- [`udf_library/iflow/`](udf_library/README.md): reusable iFlow Groovy scripts.
- [`docs/claude_memory/`](docs/claude_memory/README.md): a copy of Claude's short working notes.
- `iflowdevelopment/`: your drop folder for iFlow exports.

**On GitHub**, click any `.md` file to read it formatted. **Locally**, open it in VS Code with Markdown preview (Ctrl+Shift+V).

**Skill vs CLAUDE.md:**
- **CLAUDE.md** is read in every session.
- **A skill** is read only when the task matches its description, here "an iFlow for SSAB or Tibnor". A session must be opened in this folder for Claude Code to find the skill.

## iFlows
| Package | iFlows | Builder |
|---|---|---|
| FSAP Controlling master data (`iflows/I05xx_…`, `I0710`, `I0711`) | I0539, I0541, I0545 (CostCenter, InternalOrder, WBSElement → Medius): parent 2.1.0, child 1.1.0 · I0544 BusinessPartner → Medius + StreamServe DDS: parent 2.0.0, children 1.0.0 · dispatchers I0710 Medius, I0711 StreamServe 1.0.1 | `tools/iflow_build_fsap_dispatcher.py` |
| [SmarTeam](iflows/SmarTeam) | I2018 Material, I2023 Equipment, I2024 FunctionLocation, I2049 MaterialBOM, I2050 MaintenanceBOM: parent + `…_JMSToHTTP` child each | `tools/iflow_build_smarteam.py` |
| [Tibnor_SSAB_EDIMigration](iflows/Tibnor_SSAB_EDIMigration/README.md) | ORDERS out (parent 1.0.2, child 1.0.1); ORDRSP, DESADV, INVOIC in (parent 1.0.0, 3 mill children 1.0.1 each), with the mappings from `cpi-mappings-v2` | `tools/iflow_build_tibnor.py`, `tools/iflow_build_tibnor_inbound.py` |

The current version of each iFlow is the top entry of its `CHANGELOG.md`.

## Start on another PC
```
git -c core.longpaths=true clone --recurse-submodules https://github.com/bhavesh-kantilal/cpi-iflows-v2.git
```
Then `py -I tools/check_all_iflows.py`, which must say `All OK`.
