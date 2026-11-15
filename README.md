# CPI Mappings (SSAB / Tibnor)

SAP Cloud Integration **message mappings**, built as importable zips from a written spec, tested in CPI by the user, and improved from the user's feedback. Every version is a git tag, and every mapping has a CHANGELOG.

## Where things live
**Claude keeps no private memory for this project.** Every session starts from these files. If something isn't written here, it isn't known.

| File / folder | What it holds | Changed by |
|---|---|---|
| [`CLAUDE.md`](CLAUDE.md) | **The rules**: conventions, workflow, the 7 build checks. Loaded at the start of every session. | Only with the user's approval |
| [`_reference/FORMAT_NOTES.md`](_reference/FORMAT_NOTES.md) | **Facts about CPI**: how a mapping file is built and how functions behave. Each fact has a source and a status (CONFIRMED / UNVERIFIED / NOT COVERED). | Only with the user's approval |
| [`_reference/`](_reference/README.md) | **The evidence**: the user's original exports (L1) and the tested generated mappings (L3) | The user (README); Claude adds files on request |
| [`_reference/CATALOG.md`](_reference/CATALOG.md) | Inventory of every function and pattern in the references, **generated** by `tools/catalog.py` | Script only |
| [`REVIEW.md`](REVIEW.md) | **Waiting room**: proposals that are not rules yet, and open business assumptions | The user decides |
| [`mappings/<folder>/`](mappings) | One mapping each: `spec.md` (spec + every decision and feedback), `CHANGELOG.md`, `build_mapping.py` (the mapping as code), `build/` (the zip) | Claude, from the user's answers |
| [`tools/`](tools/README.md) | The toolkit: writes only structures FORMAT_NOTES describes, packages, and runs the checks; plus `catalog.py`, `sim_copy.py`, `wsdl_inline.py` | Claude, listed in REVIEW.md |
| [`udf_library/`](udf_library/README.md) | Reusable Groovy UDFs (e.g. `substringSafe`) | Claude, from the user's code |
| [`docs/explained/`](docs/explained) | Plain-language explanations with before/after comparisons | Claude |

## How Claude learns (and how the user keeps control)
1. **Capture:** every lesson from a build, feedback or test goes into that mapping's `spec.md`, with its evidence.
2. **Propose:** it goes to `REVIEW.md` with an evidence level:
   - **L1** the user's original export
   - **L2** the user's CPI download or statement
   - **L3** Claude's build that the user tested in CPI
   - **L4** Claude's analysis, unverified
3. **Approve:** only approved lessons become rules (CLAUDE.md) or facts (FORMAT_NOTES), each with its source.
4. **Re-learn:** after a new lesson or reference, `tools/catalog.py` regenerates the catalog from the actual files, and every rule is checked against **all** references: supported, contradicted, or not seen. Questions go to the user. Latest: [`docs/explained/relearn-2026-11-15.md`](docs/explained/relearn-2026-11-15.md).
5. **Guard:** the self-test (`py -I tools/mm.py selftest`) re-reads every reference and must write it back byte for byte, and the build checks enforce the rules on every build.

## Mappings
| Mapping | Current | From → to |
|---|---|---|
| [ORDERS](mappings/1_ORDERS_Tibnor-to-HameenlinnaMetocs/CHANGELOG.md) | 1.1.1 | Tibnor S/4 IDoc ORDERS02 → Metocs hub OrdersMessage |
| [ORDRSP](mappings/2_ORDRSP_HameenlinnaMetocs-to-Tibnor/CHANGELOG.md) | 1.0.5 | Metocs hub OrdrspInterchange → Tibnor IDoc ORDERS01 |
| [DESADV](mappings/3_Tibnor%20SSABEuropeHameenlinnaMetocs%20%5B80008%5D%20EDI%20DESADV%20in/CHANGELOG.md) | 1.0.1 | Metocs hub DeliveryBatch → Tibnor IDoc DELVRY01 |
| [INVOIC](mappings/4_Tibnor%20SSABEuropeHameenlinnaMetocs%20%5B80008%5D%20EDI%20INVOIC%20in/CHANGELOG.md) | 1.0.1 | Metocs hub Invoice → Tibnor IDoc INVOIC01 |
| [NShift](mappings/5_Tibnor_S4TransportOrder_NShift_OrderCreation/CHANGELOG.md) | 1.0.3 | S/4 TM freight order → nShift ConsignmentWS `book` |

## Lessons learned, in order
Each lesson links to where it now lives. The level shows how strong the evidence is.

**ORDERS (first mapping, 13 Nov)**
- Containers come from an empty constant, optional ones from `createIf`; elements with their own value (Reference, PartyId) keep it. → CLAUDE.md conventions (L2)
- Leading zeros: `formatNumber '#'` for numeric values, the `removezeros` UDF only for values that may contain letters. `count` instead of a counting UDF. → CLAUDE.md, FORMAT_NOTES §3.4 (L2)
- CPI re-serialises XSDs on download; compare by paths, not bytes. → FORMAT_NOTES §3.12 (L2)
- Sample files without an encoding declaration must be UTF-8 for the simulator. → CLAUDE.md (L2)

**ORDRSP (13–15 Nov)**
- A namespaced, qualified source gets `ns0:` on **every** element step, and the namespace as the 4th `<elem>` of the source link; otherwise "Add source message". → FORMAT_NOTES §2.2 (L2), [explained](docs/explained/wsdl-imports-and-namespaces.md)
- `xsi:schemaLocation` on the root breaks the simulator: use `*_sim.xml` copies (`tools/sim_copy.py`). → CLAUDE.md (L2)
- The user's PO pattern for qualifier filters; never `mapWithDefault` after a context change; functions run on all values, so put a `substring` *after* the filter. → FORMAT_NOTES §3.6 (L2; one nuance open, re-learn Q4)
- FixValues **Use Key** = `vmstrategy 2`. → FORMAT_NOTES §3.11 (L1 usage, L2 meaning)
- Optional item segments come from the filtered value chain, not from `createIf` on a per-child condition (SUPPRESS hid other items). `createIf` on a repeating condition needs one context (`removeContexts`; SAP style: `context=`), with straight fields below it. → CLAUDE.md, FORMAT_NOTES §3.5 (L2; L1 supports in substance)
- **Attribute context:** an attribute compared with its own element's value needs the parent's context. A segment and its fields use the same aligned chain: a segment only counts values, a field writes them. → FORMAT_NOTES §3.6 (L2, L1 DIR)
- Header value on every item: `CopyValue(value, 0)`. → CLAUDE.md (L2, strongly L1: 84 uses)
- `substringSafe` only when the length isn't certain; standard `substring` first. → `udf_library/` (L2)
- Layout: share logic only where the canvas stays clean, no overlaps. → CLAUDE.md, check 7 (L2, L1: SAP itself has 0 overlaps)

**DESADV / INVOIC (13 Nov)**
- Grouping per line + heat with a multi-output UDF. Output 0 is a plain `<arg>`, not `from="0"`. → FORMAT_NOTES §3.10 (L1). Open: a standard-function alternative from ACC (re-learn Q1–Q2)

**NShift (13–15 Nov)**
- No spec: best-guess rules with listed assumptions, in the user's spec workbook layout. → `mappings/5_…/spec.md`
- A WSDL that imports XSDs by URL: CPI doesn't fetch them and resolves `schemaLocation` only as a path from the WSDL's folder. Default: `../xsd/<file>.xsd` with the XSDs in `xsd/` (tests A–D). → CLAUDE.md, FORMAT_NOTES §1.1 (L2), [explained](docs/explained/wsdl-imports-and-namespaces.md)
- When inlining schemas, keep each schema's own `xmlns:tns`; every type reference must resolve (check 6). → FORMAT_NOTES §1.1 (L2)
- The WSDL link uses the message **element** name (`book`). → FORMAT_NOTES §2.2 (L2)
- S/4 sends UTC; nShift wants the local calendar day (`toLocalDate` UDF). → `mappings/5_…/spec.md` (L4, the user's test pending)

**Re-learn with the iFlows (15 Nov)**: [report 1](docs/explained/relearn-2026-11-15.md), [report 2](docs/explained/relearn-2026-11-15-iflows.md)
- SplitByValue "value change" groups only adjacent values: **always ask** whether to sort first (XSLT in the iFlow) or not. → CLAUDE.md, FORMAT_NOTES §3.6 (L1 I0115 `SortByTaxLines` + L2)
- Lift a field with `context=` (preferred), `removeContexts` when all contexts must go; `mapWithDefault` after a context change only with at most one occurrence per context. → CLAUDE.md, FORMAT_NOTES §3.6 (L1 + L2)
- Line numbers: case by case; `counter` only when the source has none. `exists` where it reads more clearly. → CLAUDE.md, FORMAT_NOTES §3.4 (L1 + L2)
- Check per interface whether a step belongs in the iFlow (sort, split per object, XSLT filter/grouping, remove `xsi:nil`); otherwise prefer a UDF. Every UDF and iFlow step is called out to the user, and every question names iFlow › mapping › target. → CLAUDE.md (L1, 14 iFlows + L2)

## Open
- Re-learn questions Q1–Q6 → [`docs/explained/relearn-2026-11-15.md`](docs/explained/relearn-2026-11-15.md)
- Business assumptions per mapping (INVOIC ZEILE, NShift booking design …) → [`REVIEW.md`](REVIEW.md) section C
