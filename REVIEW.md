# Review list: iFlows

The waiting room: proposals that are not rules yet, and open points. Nothing in **Open** is applied until the user approves it.
Status: `Open` = not reviewed yet · `OK` = reviewed and accepted · `Changed` = reviewed and changed · `Rejected`.
When proposing, say whether a lesson is **generic** (→ CLAUDE.md) or **customer-specific** (→ the customer skill, e.g. `ssab-tibnor`).

Cleaned up 2026-11-27 at the repo split: open items first, applied items as a short history. The full earlier text is in git (`git show 8d10234:REVIEW.md`). The mapping items moved to `cpi-mappings-v2/REVIEW.md`.

## Open
| # | Proposal or point | Where | Evidence | Status |
|---|---|---|---|---|
| F4 | Apply I0539 v1.1.0 to the FSAP parents: externalization, role and CSRF are not done yet (diagram and model refs fixed in 2.0.1) | iflows | `check_all_iflows.py` | Open (user is testing) |
| F5 | Typo `AlowedCompanies` → `AllowedCompanies`: check the FSAP parents (children done) | iflows | L2 (user, 2026-11-16) | Open |
| S1 | **Custom header logging:** calling `logCustomHeaders.groovy` again later in the flow is safe. CPI does not duplicate a CH_ value already logged; a changed value is added as a new line. So log a new CH_ property where its value becomes known (e.g. the response WorkId) | skill `ssab-tibnor` §6 (generic pattern) | L2 (user, 2026-11-23) | Open |
| S2 | **Child naming in the Simplified Pipeline:** `…_JMSToHTTP` although the child starts with ProcessDirect. Update `docs/explained/jms_dispatcher_architecture.md`, which still says `_PDToHTTP` | skill `ssab-tibnor` §3 (applied there) + docs | L2 (user, 2026-11-23) + L1 | Open (docs) |
| S3 | **iflw file name = iFlow name.** Copy leftovers such as `I0579_CostCentre…JMSToSOAP.iflw` are renamed in every build | CLAUDE.md (generic) | L2 (user, 2026-11-23) | Open |
| S4 | **Runtime `.jar` as input:** the build turns it into a design-time zip. Proven byte for byte on the I2049 jar/zip pair (`iflow_build_smarteam.py --selftest`). Import of a converted build in CPI is UNVERIFIED until the I2050 1.0.4 test | tools/README | L2 (I2049 pair), L4 until tested | Open |
| S5 | **OData GET receivers:** CSRF off, and externalize Delete Idle Connection (`<System>_DeleteIdleConnection`, default true) and Idle Timeout (`<System>_IdleTimeout`, default 300) | CLAUDE.md (generic) | L2 (I2050_P 1.0.5, 2026-11-23) | Open (applied to I2049_P, I2023, I2024) |
| S7 | **Logging parameters in every flow:** `LogPayload` and `LogPayloadSize` (default 512 kB) always externalized in "Set Monitoring Identifiers". Build check `empty_logpayload_rows` rejects an empty row | skill `ssab-tibnor` §5 | L2 (user, 2026-11-23) | Open |
| S11 | **No fixed adapter values** (build check `fixed_adapter_values`). Not seen in a tested reference (UNVERIFIED until a CPI test): `SmarTeam_RetryOnException`, `SmarTeam_IdleTimeout`, OData `maxRetryIterations` / `retryIntervalSec` / `whitelist*Headers` | CLAUDE.md (rule applied) | L2 (user, 2026-11-23) | Open (the UNVERIFIED names) |
| S14b | Monitoring headers: gaps in the SmarTeam flows | iflows | L2 (user's blog) | Open |
| C14 | I0544 BP Medius `CleanNamespace.groovy`: read as "namespace-free copy for the splitter XPath, original restored before the mapping" (L4). Please confirm | iflows | L4 | Open |
| C15 | I0544 JDBC vs BP Medius: why `removeXSINil` exists only before `MapBPToDDSJDBC` (user doesn't know) | iflows | L1 | Open (later) |
| P2 | **The builders hold SSAB values** (`iflow_build_smarteam.py` and others; list in the skill). Split them into customer settings in the iFlow code cleanup, after the SmarTeam explanation | tools | L4 (2026-11-27) | Open (later) |

## Applied (history)
| # | Lesson or change | Where now | Applied |
|---|---|---|---|
| F1 | HTTPS sender role and CSRF: always ask | CLAUDE.md (generic: never `ESBMessaging.send`, ask) + skill §7 (SSAB values) | 2026-11-16, generic part 2026-11-27 |
| F2 | Externalize every adapter setting someone may tune | CLAUDE.md + IFLOW_CONVENTIONS §1.4, §2.4 | 2026-11-16 |
| F3 | Diagram rule + checks in `check_iflow` | CLAUDE.md | 2026-11-16 |
| F6 | I0541 empty Allowed Request Headers: ignore; `FD1_110` is right | iflows | 2026-11-16 |
| S6 | XPath: no `local-name()` | CLAUDE.md | 2026-11-23 |
| S8 | Child `AllowedHeaders` = `SSAB.*\|SAP.*`, externalized | skill §7 (covers the open IFLOW_CONVENTIONS update) | 2026-11-23 / 2026-11-27 |
| S9 | Step name `LogCustomHeaders` | skill §3 | 2026-11-23 / 2026-11-27 |
| S10 | Step name "Send To JMS" | skill §3 | 2026-11-23 / 2026-11-27 |
| S12 | Sender roles: children always `SSAB_MessagingSend_InternalOperations`; parents unchanged except retrigger-only HTTPS | skill §7 | 2026-11-23 / 2026-11-27 |
| S13 | Location ID always externalized with Proxy Type | CLAUDE.md | 2026-11-23 |
| S14 | Monitoring headers per the user's blog: **generic** (user, 2026-11-27) | CLAUDE.md | 2026-11-23 / 2026-11-27 |
| S15 | Canvas and naming: no overlaps, unique participant names, plain system name | CLAUDE.md (generic) + skill §3 (SSAB names) | 2026-11-23 / 2026-11-27 |
| T1 | Toolkit I0539 v1.1.0: `iflow_lib.py` (`fix_diagram`, `externalize`, `Params`, `check_iflow`), `--only`, `iflow_render.py`, `sync_flow_refs`, parents 2.0.1 | tools | 2026-11-16 |
| T2 | Toolkit SmarTeam: `iflow_build_smarteam.py` (jar → design time, MANIFEST, `insert_step_after`, unused params), `Params.keys()` unescape, package folder layout | tools | 2026-11-23 |
| T3 | Repo split: `cpi-mappings-v2` as submodule, Tibnor builders read mapping zips from it; skill `ssab-tibnor`; customer checklist | CLAUDE.md, skill | 2026-11-27 |
