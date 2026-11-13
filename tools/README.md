# tools/ — CPI Message Mapping toolkit

Python 3.12 with `lxml` and `openpyxl`. Always run with `py -I` (isolated mode).

| File | What it does |
|---|---|
| `mm.py` | CLI: `selftest`, `check <zip> <Name>`, `paths <mmap> <folder>` |
| `cpimm/xmltree.py` | Lossless XML reader/writer. Keeps `<a/>` vs `<a></a>` and attribute order. |
| `cpimm/model.py` | `.mmap` ⇄ mapping model (`read_mmap`, `render_mmap`). Rejects any structure FORMAT_NOTES doesn't cover. |
| `cpimm/build.py` | `Builder`: write a mapping as Python expressions. Handles shared nodes, groups and layout. |
| `cpimm/check.py` | Schema path index (XSD, IDoc XSD, WSDL) and build checks (zip layout, well-formed, no forbidden strings) |
| `sim_copy.py` | `py -I tools/sim_copy.py <file.xml> …` writes `<name>_sim.xml` without the root's `xmlns:xsi` / `xsi:*` attributes, for the CPI mapping simulator (CLAUDE.md) |
| `wsdl_inline.py` | `py -I tools/wsdl_inline.py <in.wsdl> <out.wsdl> <ns>=<file.xsd> …` makes a self-contained WSDL: copies XSDs the WSDL imports by URL into `<types>` (namespace-only imports, as the reference WSDLs) |
| `cpimm/package.py` | Writes `build/<Name>.zip` and the extracted `build/<Name>/`, in the standalone-export layout |

## Self-test (run before trusting any change to the toolkit)
```
py -I tools/mm.py selftest
```
For every distinct reference `.mmap`, the self-test does three things:
1. reads it into the model
2. renders it back and requires **byte-identical** output
3. checks every source and target path against the mapping's own schemas

`MapSpecialTaxCases.mmap` is skipped as a known legacy envelope. It is an orphan in I0115.

## A mapping build
Each mapping folder has a `build_mapping.py` that uses `Builder`, then calls `package()`, `check_build()` and `check_paths()`. It expects:
- `mappings/<Folder>/schemas/` with the source and target XSD/WSDL/JSON
- `mappings/<Folder>/scripts/` with any Groovy UDFs

## Not implemented yet
- Path check for JSON (Swagger) schemas. It is reported as NOTE, so check those paths manually.
- iFlow generation.
