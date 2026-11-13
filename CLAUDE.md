# CPI Mappings — working rules

This repo builds SAP CPI Message Mappings (and later iFlows) for the SSAB landscape as **importable zips**.
The ground truth lives in `_reference/`:
- `_reference/FORMAT_NOTES.md`: how a mapping export is built. It is the **only** source for XML structure.
- `_reference/IFLOW_CONVENTIONS.md`: iFlow patterns and naming.
- `_reference/README.md`: what each reference export shows.

## Folder layout
```
_reference/                 reference exports (<Name>.zip + extracted <Name>/), README, FORMAT_NOTES, IFLOW_CONVENTIONS
tools/                      reusable generator / validation scripts
mappings/<Folder>/          one folder = one mapping
  spec.md                   spec + "Decisions" section
  <mapping sheet>           whatever sheet the user provides (xlsx/csv/…)
  schemas/                  source/target XSD, WSDL, IDoc XSD
  samples/                  sample payloads
  scripts/                  Groovy UDFs used by this mapping
  build_mapping.py          the mapping as code (tools/cpimm Builder); single source of truth
  feedback/                 user's CPI download of a build (zip + extracted folder)
  build/                    <MappingName>.zip + extracted <MappingName>/
  CHANGELOG.md
```
- Each mapping lives in its own folder under `mappings/`. Every folder there is a new mapping. Subfolders may appear later; the user will say in chat where to look.
- **The mapping name is given by the user in chat.** It can differ from the folder name. It sets the `.mmap` name and the zip name. Default pattern: `Map_<Src>_<Tgt>_<Object>_<MsgType>` (see IFLOW_CONVENTIONS §2.2). If no name was given, or the name breaks the pattern, ask.
- `_reference/`: never modify anything except README.md (typos and heading formatting only), FORMAT_NOTES.md, IFLOW_CONVENTIONS.md and CATALOG.md, and the last three only with approval.

## Reading the spec and the mapping sheet
- Mapping sheet and spec formats vary per mapping. Work out the sheet's columns yourself: which column is source path, target path, rule/logic, constant, comment and so on.
- **Ask the user if anything is ambiguous rather than assuming.** Examples: unclear column meaning, conditions, context or queue questions, cardinality, missing schema paths, value-mapping agencies.
- Record **every** Q&A decision in that mapping's `spec.md` under a `## Decisions` section, with date, question, answer and impact.

## Building a mapping
- Build strictly following `_reference/FORMAT_NOTES.md`. **Never invent XML structure that is not seen in the references.**
- If something is needed that the references don't show (anything marked NOT COVERED, or a function with no catalog entry), **stop and ask**.
- If you rely on an item marked UNVERIFIED, say so to the user.
- The mapping is written in `mappings/<Folder>/build_mapping.py` with the toolkit's `Builder` (`tools/README.md`). XML is produced only by `tools/cpimm/model.py`, which renders only the structures described in FORMAT_NOTES. Running the script builds, packages and checks.
- **Before every build, run `py -I tools/mm.py selftest`.** It must pass: every standard reference `.mmap` round-trips byte-identically and all its paths are found in its schemas. Run it again after any toolkit change.

### Mapping conventions (user rules, 2026-11-13)
- **Containers ("tags")** — nodes that only hold child elements — come from an **empty constant**. When the node is optional, use `createIf(condition)` instead.
  - Use SAP judgement for which is which, e.g. a PO item always has Quantity and Price.
  - An element that **carries its own value** (simple content, with or without attributes, e.g. `Reference`, `PartyId`, `Date`) is **not** a tag. It keeps its source value.
  - Repeating nodes keep their source occurrence (e.g. `Item` ← `E1EDP01`).
- **Leading zeros**: use standard `formatNumber` with Number Format `#` and Decimal Separator `.` when the source is always numeric (e.g. POSEX). Use a UDF (`removezeros`) only for values that may contain letters (e.g. IDTNR).
- **Standard functions before UDFs.** Use a Groovy UDF only when no standard function does the job (e.g. `count` instead of a counting UDF). Prefer reusing a reference UDF unchanged over writing a new one.
- **Sample files**: check the encoding. A file with `<?xml version="1.0"?>` and no encoding declaration must be UTF-8, or the CPI mapping simulator won't load it. Make a UTF-8 copy (`*_utf8.xml`) and never change the user's original.
  - A root with `xmlns:xsi` + `xsi:schemaLocation` breaks the mapping simulator (`prefix "ns6" … is not bound`). Make a copy without those two attributes (`*_sim.xml`) for simulation (ORDRSP, 2026-11-13). Runtime behaviour in the iFlow is not tested yet.
- **Qualifier filters on repeating source children** (e.g. `Quantity[@Type='21']`, `Property[@Type='12']`): follow the user's PO pattern (FORMAT_NOTES §3.6). No context settings on lower-level source fields and no UDF. Put value transforms that can fail (e.g. `substring`) after the filter. (User rule, 2026-11-13.)
- **Build output** goes to `mappings/<Folder>/build/` as:
  - `<MappingName>.zip`, importable, with the same layout as the standalone reference zips (FORMAT_NOTES §1.1): root `mapping/`, `script/`, `xsd/`, `wsdl/`. No MANIFEST, `.project` or `metainfo.prop`.
  - The extracted `<MappingName>/` folder next to the zip.
  - The zip name stays fixed with no version suffix. Git history holds the versions.
- Reusable generator and validation scripts go in `tools/`, never inside a mapping folder.

## Checks before finishing a build (all must pass, report results)
1. Every source and target XPath used in the `.mmap` exists in the schemas, including attributes (`@x`), duplicate indexes (`item[1]`) and `context="…"` paths. For **JSON** sources or targets, check paths against the Swagger/OpenAPI schema of the linked operation (request body, `$ref` resolved) instead of an XSD. `/__$$RoOt_ArRaY$$__` stands for a root array (FORMAT_NOTES §2.2).
2. All XML is well-formed: `.mmap`, XSD and WSDL.
3. The zip structure matches the references: entries at the root, only the allowed folders, the `.mmap` name equals the mapping name, every `UsedFuncLib` script is present in `script/`, and every schema in `lnks` is present.
4. The `.mmap` envelope matches FORMAT_NOTES §2.1: one line, no BOM, no prolog.
5. No `claude` or `anthropic` string, and no tool or AI metadata, in any file inside the zip. `modifBy` and `owner` stay empty, as in the references.

## CHANGELOG
- Each mapping folder has a `CHANGELOG.md`. Add an entry for **every** build:
  `## <x.y.z> — <YYYY-MM-DD>` followed by what changed.
- Versions start at `1.0.0`. Bump the patch for fixes and the minor for spec or scope changes.

## Naming
- Follow `_reference/IFLOW_CONVENTIONS.md` for mappings, iFlows, queues and parameters. Don't copy its "Observed deviations" table.

## Git
- Track everything: `_reference/`, docs, `tools/`, mapping sources and `build/` zips. The repo is the backup of all knowledge. Nothing project-specific lives only in Claude's memory.
- After each build, commit (`<MappingName> v<x.y.z>: <change>`) and tag `<MappingName>-v<x.y.z>`.
- **Line endings**: never remove or weaken `.gitattributes` (`* -text`). Git on this PC has `core.autocrlf=true` set system-wide, so without that file it rewrites CRLF and LF. Every reference export and every build output must stay byte-identical to the original. After committing, spot-check with `git show HEAD:<file> | cmp - <file>`.
- Commits are authored by the user's git identity. **Do not add `Co-Authored-By` or any Claude/AI attribution** to commits or files.
- Commit or push only as part of a task the user asked for. Recommended: a private remote (GitHub or Azure DevOps) so the repo survives a disk crash.

## Learning loop
- **New references**: the user drops `<Name>.zip` into `_reference/` and adds a README entry. On "learn new references":
  - extract the zip into `_reference/<Name>/`
  - update `_reference/CATALOG.md` (functions, params and patterns, with sources)
  - diff against FORMAT_NOTES and propose additions with citations
- **Feedback** (after the user tests in CPI):
  1. The user downloads the mapping from CPI: package → Artifacts → Actions (…) → **Download**. They save the zip in `mappings/<Folder>/feedback/` and say "feedback is in".
  2. Extract it into `feedback/<Name>/`. Compare it with the build using `tools/cpimm/diff.py`, which works per target and ignores layout and uid numbering. CPI re-serializes XSDs, so compare those by paths, not bytes (FORMAT_NOTES §3.12).
  3. Take over the user's changes in `build_mapping.py`, so the build script stays the single source of truth. **Don't blindly copy** a change that contradicts the spec or the samples: flag it and ask (e.g. ORDERS v1.1.0, Reference).
  4. Rebuild as the next version. Record each difference in spec.md (Decisions) and CHANGELOG. Propose any general lesson as a rule here.
- Before committing, check `git status` for files changed by the user (e.g. edited samples) and mention them; don't commit them silently.
- **At the end of each task**, propose any new convention or correction you learned as an update to `CLAUDE.md` or `_reference/FORMAT_NOTES.md`. **Wait for the user's approval before changing them.**

## Environment
- Windows 11 with Git Bash and PowerShell.
- Python 3.12 (with `openpyxl` and `lxml`) runs `tools/`. Always use `py -I` (isolated mode).
  - In a shell that started before the install, use the full path `C:\Users\BhaveshKantilal\AppData\Local\Programs\Python\Python312\python.exe`.
  - Windows console output needs `sys.stdout.reconfigure(encoding="utf-8")`, which the tools already do.
- Node.js is installed (fallback). A SAP JVM 8 is present, but nothing uses it.
