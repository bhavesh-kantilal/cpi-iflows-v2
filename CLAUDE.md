# CPI Mappings — working rules

This repo builds SAP CPI Message Mappings (and later iFlows) for the SSAB landscape as **importable zips**.
The ground truth lives in `_reference/`:
- `_reference/FORMAT_NOTES.md`: how a mapping export is built. It is the **only** source for XML structure.
- `_reference/IFLOW_CONVENTIONS.md`: iFlow patterns and naming.
- `_reference/README.md`: what each reference export shows.

## Folder layout
```
_reference/                 reference exports (<Name>.zip + extracted <Name>/), README, FORMAT_NOTES, IFLOW_CONVENTIONS, CATALOG
  iflows/                   whole iFlow exports (<iFlowName>.zip + extracted), the context of the mappings
tools/                      reusable generator / validation scripts
udf_library/                reusable Groovy UDFs (README: when to use each one)
docs/explained/             plain-language explanations of lessons learned
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
iflowdevelopment/           the user's single drop folder for iFlow exports (any package); Claude copies from here
iflows/<Package>/           one folder = one CPI package (e.g. SmarTeam)
  source/                   copies of the user's exports and CPI downloads (zip / jar / package zip), unchanged
  <IFlowName>/              one folder = one iFlow we build
    spec.md                 purpose, parameters, "Decisions" section
    build/<IFlowName>.zip + extracted <IFlowName>/
    CHANGELOG.md
iflows/<IFlowName>/         older flat layout (FSAP flows), moves into iflows/<Package>/ later
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
- **WSDLs that import XSDs by URL:** CPI does not fetch them. Ask before downloading, and keep the XSDs unchanged in `schemas/downloaded/`. **Default (user, 2026-11-15):** a copy of the WSDL with only the `schemaLocation` values changed to `../xsd/<file>.xsd`. The build packs the XSDs into the zip's `xsd/` (FORMAT_NOTES §1.1, NShift TestD). Inlining with `tools/wsdl_inline.py` is the alternative. The original WSDL stays unchanged.
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
  - A root with `xmlns:xsi` + `xsi:schemaLocation` breaks the mapping simulator (`prefix "ns6" … is not bound`). Make a copy without those attributes with `py -I tools/sim_copy.py <file>` (`*_sim.xml`) for simulation (ORDRSP, 2026-11-13). Runtime behaviour in the iFlow is not tested yet.
- **Qualifier filters on repeating source children** (e.g. `Quantity[@Type='21']`, `Property[@Type='12']`): follow the user's PO pattern (FORMAT_NOTES §3.6). No UDF. Put value transforms that can fail (e.g. `substring`) after the filter. (User rule, 2026-11-13.)
  - **Context settings only for attributes compared with their own element's value** (`Date/@Type` vs `Date` → context = Item). An attribute compared with a child element (`Quantity/@Type` + `QuantityValue`) gets no context. Never `mapWithDefault` after a context change. (FORMAT_NOTES §3.6, user's fix ORDRSP v1.0.4, 2026-11-15.)
  - **A segment and its fields use the same aligned chain.** A misaligned chain can give the right segment count with wrong field values (ORDRSP E1EDP03 v1.0.5).
- **`createIf`** (user rule 2026-11-15, FORMAT_NOTES §3.5):
  - On a repeating condition, follow it with `removeContexts`. The segment's fields are then **straight maps**.
  - Never `createIf` on a segment together with `ifWithoutElse` on its fields. Instead feed the segment and its fields from one filtered chain (`ifWithoutElse` → `removeContexts` → `SplitByValue`).
  - Optional **item** segments (one per item, e.g. E1EDP03, E1EDP19) always come from that filtered chain, never from `createIf` on a per-child condition.
- **Header value on every item:** `CopyValue(value, 0)`, not `useOneAsMany` (user rule 2026-11-15).
- **SplitByValue "Value change"** groups only *consecutive* equal values. **Whenever a mapping uses it, ask the user** whether the input must be sorted first, and how: the source may already be sorted, sorting may not be needed, or the user may want it without sorting. If sorting is wanted, it's an XSLT sort step in the iFlow before the mapping (L1: iFlow I0115 XSLT `SortByTaxLines` before `MapToRFC_BAPI_ACC_DOCUMENT_POST`). A sum per group is `sum(formatByExample(value, SplitByValue[value change](removeContexts(key))))` (L1 ACC `CURRENCYAMOUNT/item[2]/AMT_DOCCUR`, confirmed by the user). (R1, 2026-11-15)
- **Lifting a field to a higher level:** prefer a `context=` setting on the source (JournalEntry style, shown in italics in the editor). Use `removeContexts` when *all* contexts must go. Not a hard rule. (R3, user 2026-11-15)
- **`mapWithDefault` after a context change** only when the business context guarantees at most one occurrence per new context (e.g. an invoice header field). Otherwise apply `mapWithDefault` in the field's own context first, then `removeContexts` / `formatByExample`. (R4, FORMAT_NOTES §3.6)
- **Line numbers:** case by case. Only when the source does **not** provide line numbers, consider the standard `counter` (e.g. `ini=2`, `inc=2` when line 1 is reserved for the vendor line, as in ACC). A UDF only if `counter` can't do it. (R5, user 2026-11-15)
- **iFlow steps around the mapping: a check, not a rule.** Before building, ask whether something belongs in the iFlow, and decide per interface with the user. Candidates seen in the user's iFlows:
  - a sort step (see "Value change" above)
  - a splitter when the **target expects one message per object** (I0541, I0544: Medius wants one message per supplier / company code)
  - XSLT for grouping, filtering, or moving a whole segment to another level (I0161 `LowestLevel`, I0544 `AccountingInformationAllowed`)
  - removing `xsi:nil` fields that clutter the mapping (I0544 JDBC `removeXSINil`)

  Otherwise a UDF is preferred over XSLT. Every such step is named in the mapping's `spec.md` and called out to the user. (R6, user 2026-11-15)
- **Value tables:** FixValues "Use Key" (`vmstrategy 2`, empty default) passes unknown values through, e.g. unit M → MTR. Use it instead of if-then-else.
- **Layout (user rule 2026-11-15):** share logic between targets only when the editor canvas stays clean: no overlapping bricks, and a shared brick in the same column for all its targets (like E1EDK03 + DATUM). Otherwise split. The toolkit does this (`Builder`), and the build checks reject overlaps.
- **UDF library:** reusable UDFs live in `udf_library/` (see its README). A mapping copies the file **unchanged** into its `scripts/`. Prefer the standard function, e.g. `substring`; use a library UDF such as `substringSafe` only when the standard one may fail (value length not certain).
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
6. Every `type=` / `ref=` / `base=` reference in the zip's XSD and WSDL files resolves (NShift v1.0.0: unresolved types gave an empty structure in CPI).
7. No overlapping bricks on any editor canvas.

Checks 1–7 run automatically in every `build_mapping.py` (`check_build`, `check_paths`).

## Building an iFlow (user rules, 2026-11-16, I0539 feedback)
- iFlows are built by scripts in `tools/` (e.g. `tools/iflow_build_fsap_dispatcher.py --only <IFlowName>`), which use `tools/iflow_lib.py`. The script is the single source of truth. Feedback is taken over into the script, as with mappings.
- **A change to the process flow must also update the BPMN diagram.** Drop the shapes and edges of removed steps, give every flow an edge whose ends match its source and target, and give every step a shape. Close gaps left by removed steps. `iflow_lib.fix_diagram` (with `shift=`) and `iflow_lib.sync_flow_refs` do this. (I0539 v1.0.0: "Main Process connection missing"; I0539_P 2.0.0: gap and no arrows, L2.)
- For a quick visual check without CPI, `py -I tools/iflow_render.py <zip> <out.svg>` draws the diagram.
- **XPath in Content Modifiers and routers: no `local-name()`** unless the user asks for it or a source needs it for a logical reason (user, 2026-11-23). Write plain paths that match the real message, checked against a sample or the mapping source XSD/WSDL. When only the root element is namespaced (SAP ESR messages, unqualified children), use `/*/child/…`.
- **Child iFlows (`…_JMSToHTTP`): Allowed Headers externalized as `{{AllowedHeaders}}` = `SSAB.*|SAP.*`** (user, 2026-11-23). `iflow_build_smarteam.py` sets it for every child and fails if it is not externalized.
- **HTTPS sender role and CSRF: always ask.** SSAB default: `SSAB_MessagingSend_InternalOperations`, CSRF off.
- **Externalize every adapter setting someone may tune**, with `HTTP_<Setting>` / `<System>_<Setting>` names (IFLOW_CONVENTIONS §1.4, §2.4). Channels to the same system share one set. Fix misspelt parameter names and tell the user that the tenant value must be set again.
- Every iFlow folder gets a `spec.md` with a Decisions table (user, 2026-11-16).
- **Checks for every iFlow build** (`iflow_lib.check_iflow`, run in the build and in `tools/check_all_iflows.py`):
  - well-formed XML
  - no orphan diagram elements; every flow has an edge with matching ends; every step has a shape
  - every step's `<incoming>`/`<outgoing>` match the sequence flows (I0539_P 2.0.0: Log Payload still pointed to a removed flow, and CPI showed a gap)
  - every `{{param}}` is in parameters.prop and propdef, and no unused parameters
  - no `claude`/`anthropic` strings
  - MANIFEST name equals the iFlow name

## CHANGELOG
- Each mapping folder has a `CHANGELOG.md`. Add an entry for **every** build:
  `## <x.y.z> — <YYYY-MM-DD HH:MM> CET` (time of the build commit, Central European Time: CET in winter, CEST in summer) followed by what changed in plain words. (User, 2026-11-15: a date alone is not enough when several versions are made on one day.)
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
Claude keeps no private memory for this project: what is not written in this repo is not known.
- **Evidence levels.** L1 = the user's original export; L2 = the user's CPI download or explicit statement;
  L3 = Claude's build that the user tested in CPI; L4 = Claude's analysis (UNVERIFIED). Every fact in
  FORMAT_NOTES and every rule here names its source and level.
- **Loop for every new lesson:** capture it in the mapping's `spec.md` with its evidence → propose it in
  `REVIEW.md` → only after the user's approval write it into CLAUDE.md (rule) or FORMAT_NOTES (fact).
- **Re-learn after every approved lesson or new reference:** run `py -I tools/catalog.py`, then check every
  rule against all references (supported / contradicted / not seen, with files) in a report under
  `docs/explained/`. Contradictions and anything not understood go to the user as numbered questions
  (mapping, target field, brick). Generated mappings are not changed unless an approved rule changes.
- **Generated references** go into `_reference/` marked L3 in its README; they show what works, not how
  SAP itself writes a mapping.
- **UDF call-out:** whenever Claude writes a UDF (or proposes an iFlow step such as an XSLT), the mapping's
  `spec.md` Decisions and the chat message say: "Bhavesh, I built `<name>` because `<requirement>`; standard
  alternative: `<…>`; why not: `<…>`." (R2)
- **Question format:** every question names `iFlow › mapping › target field (full path)` and the full
  expression (sources, functions, context settings), so it can be opened in CPI. If the iFlow is not known,
  say "no iFlow known". (R2)
- **Re-learn includes the iFlow:** a mapping pattern is always read with the iFlow steps before and after it
  (`_reference/CATALOG.md` §4; `tools/iflow_import.py` for new iFlow zips). Mappings without an iFlow are
  listed, and the user is asked for the export. (R2)
- **New references**: the user drops `<Name>.zip` into `_reference/` and adds a README entry. On "learn new references":
  - extract the zip into `_reference/<Name>/`
  - regenerate `_reference/CATALOG.md` with `py -I tools/catalog.py` (functions, params and patterns, with sources; never edit it by hand)
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
