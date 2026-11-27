# CPI iFlows: working rules

This repo builds SAP CPI **iFlows** as importable zips, for several customers.
- **How iFlows are built is generic.** Diagram rules, checks, Groovy, XPath, externalizing and the workflow are in this file.
- **How a customer organizes and names its iFlows is customer-specific.** Each customer has a **skill** in `.claude/skills/<customer>/SKILL.md`.
  - The only one so far: **`ssab-tibnor`**, SSAB and Tibnor, one CPI tenant.
- **Mapping development lives in the mapping repo**, included here as the git submodule `cpi-mappings-v2/`. See "Mapping work from this repo" below.

The ground truth for iFlows:
- `_reference/iflows/`: the user's iFlow exports (L1, SSAB)
- `_reference/IFLOW_CONVENTIONS.md`: patterns and naming observed at SSAB
- `_reference/README.md`: what each reference export shows

## Working style (user, 2026-11-27)
- **Answer in small, separate parts, one topic per reply.** When the user asks many questions at once, split them into steps. Answer the first one briefly, report, and wait before the next.

## Which customer? (user, 2026-11-27)
- **Before building or changing an iFlow, know which customer it is for.** If the chat or the iFlow folder doesn't make it clear, ask.
  - **SSAB or Tibnor** (same tenant): use the skill `ssab-tibnor`.
  - **Another customer:** ask whether to reuse the SSAB answers or go through the customer checklist below. Write the answers into a new skill `.claude/skills/<customer>/SKILL.md`, with the same sections as `ssab-tibnor`. Mark each point "[Generic pattern, <customer> value]" or "[<customer> only]".
- **Customer checklist:** ask before the first iFlow for a customer. The answers go into the customer skill.
  1. **Monitoring identifiers:** usually yes, see below. Which values do `SAP_Sender`, `SAP_Receiver` and `SAP_MessageType` take?
  2. **JMS organization:** queues, queue names, retention, retries, dead-letter queue, transaction handling.
  3. **Naming:** iFlows, steps, participants, parameters, mappings, versions.
  4. **JMS dispatcher:** one per sender/receiver pair, or shared dispatchers like SSAB's Simplified Pipeline?
  5. **Payload logging:** which script or collection, which switch properties?
  6. **Custom header logging:** which script, which prefix?
  7. **Sender role, Allowed Headers, shared helper flows** (IDoc/XI receivers, mail, lookups).
  8. **Anything else customer-specific:** the customer's own best-practice guide, structure (main process, retrigger), transport, operations.
- The builders in `tools/` still hold SSAB values (see the skill, "Where the code enforces SSAB values"). For another customer, don't run them unchanged. Ask first.

## Folder layout
```
_reference/                 README, IFLOW_CONVENTIONS
  iflows/                   whole iFlow exports (<iFlowName>.zip + extracted)
.claude/skills/<customer>/  customer conventions (SKILL.md)
tools/                      iFlow builders and checks (iflow_lib.py, iflow_build_*.py, check_*.py)
udf_library/iflow/          reusable iFlow Groovy scripts
docs/explained/             plain-language explanations of lessons learned
iflowdevelopment/           the user's single drop folder for iFlow exports (any package); Claude copies from here
iflows/<Package>/           one folder = one CPI package (e.g. SmarTeam)
  source/                   copies of the user's exports and CPI downloads (zip / jar / package zip), unchanged
  <IFlowName>/              one folder = one iFlow we build
    spec.md                 purpose, parameters, "Decisions" section
    build/<IFlowName>.zip + extracted <IFlowName>/
    CHANGELOG.md
iflows/<IFlowName>/         older flat layout (FSAP flows), moves into iflows/<Package>/ later
cpi-mappings-v2/            git submodule: the mapping repo (its own CLAUDE.md, tools/, mappings/)
```
- `_reference/`: never modify anything except README.md (typos and heading formatting only) and IFLOW_CONVENTIONS.md, the latter only with approval.

## Mapping work from this repo (user, 2026-11-27)
- During iFlow work the user may ask for a mapping as well. All mapping work happens in **`cpi-mappings-v2/`** and follows **its** `CLAUDE.md`: the mapping rules, the self-test and the 7 build checks.
- The user may point to input files anywhere ("the mapping Excel / XMLs are in folder xyz"). **Copy them unchanged** into the mapping folder, in the layout of the mapping repo:
  - `cpi-mappings-v2/mappings/<NN_Name>/` with the sheet, `schemas/`, `samples/`, `scripts/`
  - a new folder gets the next free number

  The layout gets improved later.
- **Commit order:**
  1. Commit and push the mapping change **inside `cpi-mappings-v2/`**, to its own remote.
  2. Then commit the new submodule pointer here (`git add cpi-mappings-v2`) and push.

  Never leave the pointer at a commit that is not pushed.
- iFlows that embed a mapping read the zip from `cpi-mappings-v2/mappings/<Folder>/build/` (e.g. `MAP_ZIP` in `tools/iflow_build_tibnor.py`).

## Building an iFlow (generic rules; user rules, 2026-11-16 onwards)
- iFlows are built by scripts in `tools/` (e.g. `tools/iflow_build_fsap_dispatcher.py --only <IFlowName>`), which use `tools/iflow_lib.py`. The script is the single source of truth. Feedback is taken over into the script, as with mappings.
- **No overlapping pools or steps on the iFlow canvas** (user, 2026-11-23, I2024): when a step is inserted and a pool gets wider, move every pool to its right (same height) with its steps. Build check `layout_errors`: pools don't overlap, every step lies inside its own pool.
- **A change to the process flow must also update the BPMN diagram.** Drop the shapes and edges of removed steps, give every flow an edge whose ends match its source and target, and give every step a shape. Close gaps left by removed steps. `iflow_lib.fix_diagram` (with `shift=`) and `iflow_lib.sync_flow_refs` do this. (I0539 v1.0.0: "Main Process connection missing"; I0539_P 2.0.0: gap and no arrows, L2.)
- For a quick visual check without CPI, `py -I tools/iflow_render.py <zip> <out.svg>` draws the diagram.
- **No payload parsing in Groovy for values one XPath can read** (user, 2026-11-24): set them as a property by XPath in a Content Modifier (usually "Set Monitoring Identifiers"), and the script reads `message.getProperty(...)`. E.g. receiver determination on RCVPRN or ApplicationId. Parse the payload only for complex logic.
- **Groovy XML parsing streams the body** (user, 2026-11-23, CPI script editor "High" warning on IXXXX_P ReceiverDetermination):
  - write `new XmlSlurper().parse(message.getBody(java.io.Reader))` (same for `XmlParser`)
  - never `parseText(message.getBody(String))` or any other body String
  - build check `iflow_lib.script_parse_errors`: fails our builds, FLAG in `check_all_iflows.py`
- **Partner / logical system values** (RCVPRN, SNDPRN…) can be numbers with leading zeros or alphanumeric logical system names: strip leading zeros only when the value is all digits, and compare other values as they are (user, 2026-11-23).
- **XPath in Content Modifiers and routers: no `local-name()`** unless the user asks for it or a source needs it for a logical reason (user, 2026-11-23). Write plain paths that match the real message, checked against a sample or the mapping source XSD/WSDL. When only the root element is namespaced (SAP ESR messages, unqualified children), use `/*/child/…`.
- **Message monitoring identifiers: generic, at almost every customer** (user's blog "SAP CPI Message Monitoring: standard out-of-the-box features", sprintegrate.com, 2023; L2, 2026-11-23 and 2026-11-27):
  - Standard headers are set in the **first Content Modifier** as **headers**: `SAP_Sender` = `{{SAP_Sender}}`, `SAP_Receiver` = `{{SAP_Receiver}}`, `SAP_MessageType` = `{{SAP_MessageType}}` (parameter name = header name, always this casing; build check `monitor_param_names`). The step name comes from the customer skill (SSAB: "Set Monitoring Identifiers").
  - For IDoc senders `SAP_MessageType` may come from XPath `concat(//MESTYP, '.',//IDOCTYP,if (//CIMTYP) then concat('.', //CIMTYP) else ())`.
  - `SAP_ApplicationID` = XPath to the business key (payload search), e.g. `//DOCNUM` for IDocs.
  - Allowed-value lists for SAP_Sender / SAP_Receiver / SAP_MessageType: ask the user, don't invent values. Known values are in the customer skill.
  - **Parent iFlows (receiver determination, several receivers) never set `SAP_Receiver`**; only point-to-point flows and children do (user, 2026-11-23). Build check `monitor_header_errors`.
- **Sender role: never CPI's default role `ESBMessaging.send`** (user, 2026-11-27). For every customer, ask which role a sender uses. The values are in the customer skill. CSRF protection: always ask.
- **Participant names are unique in an iFlow**: CPI does not allow a sender and a receiver (or a local process) with the same name (user, 2026-11-23). **Ask before renaming** when the plain system name is taken.
  - A receiver is the **plain system name**. Add a purpose suffix (e.g. `<System>_BOM`, `<System>_MAIL`) **only when that name is already taken** by another participant in the same iFlow. Never `Receiver`, `Receiver1`, `Sender`…
  - Keep names simple, the receiver system name, not leftovers like `MSAP_PO`.
  - Build check `participant_name_errors` fails on duplicates and generic names. A suffixed name whose plain name is free is reported.
  - **Always flag participant names that are not the system name** (`Receiver1`, `MSAP_Lookup`, `MSAP_PO`…) to the user. Generic names fail the build; other unknown names are printed as FLAG. The known names per customer are in its skill.
- **Allowed Headers: never `*`** in a sender's Allowed Headers or a receiver's request headers. List the expected ones and externalize them. The values are in the customer skill.
- **Externalize every adapter setting someone may tune** (IFLOW_CONVENTIONS §1.4, §2.4), e.g. `HTTP_<Setting>` / `<System>_<Setting>`; the naming comes from the customer skill. Channels to the same system share one set. Fix misspelt parameter names and tell the user that the tenant value must be set again.
  - **Location ID always with Proxy Type** (HTTP `locationID`, OData `scc_location_id`), even when empty, e.g. `SmarTeam_LocationID` (user, 2026-11-23). Build check `location_not_externalized`.
  - **Check every adapter of every iFlow in each round, not only the ones being changed** (SmarTeam, 2026-11-23: the SmarTeam receiver stayed fixed for 3 rounds). List every non-empty fixed value per channel, and externalize it or ask. Never leave it as an "open point".
- Every iFlow folder gets a `spec.md` with a Decisions table (user, 2026-11-16).
- **Checks for every iFlow build** (`iflow_lib.check_iflow`, run in the build and in `tools/check_all_iflows.py`):
  - well-formed XML
  - no orphan diagram elements; every flow has an edge with matching ends; every step has a shape
  - every step's `<incoming>`/`<outgoing>` match the sequence flows (I0539_P 2.0.0: Log Payload still pointed to a removed flow, and CPI showed a gap)
  - every `{{param}}` is in parameters.prop and propdef, and no unused parameters
  - no `claude`/`anthropic` strings
  - MANIFEST name equals the iFlow name
- **Best-practice FLAGs** (`iflow_lib.best_practice_flags`, `tools/check_best_practices.py`, also printed by `check_all_iflows.py`). They are reported, not failed: fix them in the flow you touch, or confirm with the user. Today they follow the SSAB guide (see the `ssab-tibnor` skill).

## CHANGELOG
- Each iFlow folder has a `CHANGELOG.md`. Add an entry for **every** build:
  `## <x.y.z> — <YYYY-MM-DD HH:MM> CET` (time of the build commit, Central European Time: CET in winter, CEST in summer) followed by what changed in plain words. (User, 2026-11-15: a date alone is not enough when several versions are made on one day.)
- Versions start at `1.0.0`. The customer skill says how versions count (SSAB: major per project, minor per CR/SR/fix, micro per development change).

## Git
- Track everything: `_reference/`, docs, `tools/`, iFlow sources and `build/` zips. The repo is the backup of all knowledge. Nothing project-specific lives only in Claude's memory.
- After each build, commit (`<IFlowName> v<x.y.z>: <change>`) and tag `<IFlowName>-v<x.y.z>`.
- **Line endings**: never remove or weaken `.gitattributes` (`* -text`). Git on this PC has `core.autocrlf=true` set system-wide, so without that file it rewrites CRLF and LF. Every reference export and every build output must stay byte-identical to the original. After committing, spot-check with `git show HEAD:<file> | cmp - <file>`.
  - Don't edit files with `sed -i` in Git Bash: it rewrites CRLF files to LF (2026-11-27). Use the Edit tool or a byte-level Python replace.
- **Long paths:** SmarTeam names exceed 260 characters. This clone has `core.longpaths true`; set it in every new clone (`git -c core.longpaths=true clone …`).
- Commits are authored by the user's git identity. **Do not add `Co-Authored-By` or any Claude/AI attribution** to commits or files.
- **This PC and GitHub stay in sync** (user, 2026-11-25): the remote is `origin` = `github.com/bhavesh-kantilal/cpi-iflows-v2` (private). **After every commit, push `master` and the tags** (`git push origin master` + `git push origin --tags`). Clone with `git clone --recurse-submodules` to get the mapping repo too. Before ending a task, `git status -sb` must show no `ahead`, here and in `cpi-mappings-v2/`. Commit only as part of a task the user asked for.
- **The old repo `C:\work\cpi-mappings` is frozen** (user, 2026-11-27): it is the fallback from before the split. Never edit, commit or push there.
- **Claude's memory folder is mirrored in the repo**: `docs/claude_memory/` holds a copy of every note in Claude's own memory folder. When Claude writes or changes such a note, it updates the copy in the same commit.

## Learning loop
Claude keeps no private memory for this project: what is not written in this repo is not known.
- **Evidence levels.** L1 = the user's original export; L2 = the user's CPI download or explicit statement;
  L3 = Claude's build that the user tested in CPI; L4 = Claude's analysis (UNVERIFIED). Every rule here and in a customer skill names its source and level.
- **Loop for every new lesson:** capture it in the iFlow's `spec.md` with its evidence → propose it in
  `REVIEW.md` → only after the user's approval write it into CLAUDE.md (generic rule), the customer skill (customer rule) or IFLOW_CONVENTIONS.
  When proposing, say whether the lesson is generic or customer-specific.
- **UDF / script call-out:** whenever Claude writes a Groovy script or proposes an iFlow step such as an XSLT, the `spec.md` Decisions and the chat message say: "Bhavesh, I built `<name>` because `<requirement>`; standard alternative: `<…>`; why not: `<…>`." (R2)
- **Question format:** every question names `iFlow › step › setting` (or `iFlow › mapping › target field`) and the full expression, so it can be opened in CPI. (R2)
- **New iFlow references**: the user drops exports into `iflowdevelopment/` or `_reference/iflows/`. `tools/iflow_import.py` extracts them into `_reference/iflows/`.
- **Feedback** (after the user tests in CPI): the user downloads the iFlow from CPI into the package's `source/`. Take over the changes in the builder script, rebuild as the next version, and record each difference in spec.md (Decisions) and CHANGELOG. **Don't blindly copy** a change that contradicts the spec: flag it and ask.
- Before committing, check `git status` for files changed by the user and mention them; don't commit them silently.
- **At the end of each task**, propose any new convention or correction you learned as an update to `CLAUDE.md`, the customer skill or `_reference/IFLOW_CONVENTIONS.md`. **Wait for the user's approval before changing them.**

## Environment
- Windows 11 with Git Bash and PowerShell.
- Python 3.12 (with `openpyxl` and `lxml`) runs `tools/`. Always use `py -I` (isolated mode).
  - In a shell that started before the install, use the full path `C:\Users\BhaveshKantilal\AppData\Local\Programs\Python\Python312\python.exe`.
  - Windows console output needs `sys.stdout.reconfigure(encoding="utf-8")`, which the tools already do.
- Node.js is installed (fallback). A SAP JVM 8 is present, but nothing uses it.
