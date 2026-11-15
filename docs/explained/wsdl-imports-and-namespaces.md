# How we made it work: namespaces (ORDRSP) and URL-imported XSDs (NShift)

Plain-language explanation with before/after comparisons, taken from the real files in this repo.
Rules that came out of it: CLAUDE.md ("Building a mapping", checks 6–7) and FORMAT_NOTES §1.1, §2.2.

---

## Part 1 — Namespaces in the ORDRSP mapping

### 1.1 The payload has a namespace even though you don't see a prefix
The hub sends:
```xml
<OrdrspInterchange xmlns="http://www.ruukki.com/schemas/eai/internal/production/eruukki" …>
  <OrderResponseMessage>
    <Item>
      <LineNo>010</LineNo>
```
`xmlns="…/eruukki"` on the root is a **default namespace**: it applies to the root **and every element below it**. So `LineNo` is really `{…/eruukki}LineNo`, even though no `ns0:` is written in the XML. The XSD says the same thing: `targetNamespace="…/eruukki"`, `elementFormDefault="qualified"`.

Inside a CPI message mapping, every namespaced element is written with a short **prefix** (`ns0:`), and the mapping file declares what `ns0` means:
```xml
<namespaces><properties><property name="http://www.ruukki.com/schemas/eai/internal/production/eruukki">ns0</property></properties></namespaces>
```
The prefix exists **only inside the mapping**. The XML on the wire never needs to contain `ns0:`.

### 1.2 Which steps get the prefix? We tested two variants (v1.0.0)
| | Variant A: `NsAllSteps` | Variant B: `NsRootOnly` |
|---|---|---|
| Source path in the `.mmap` | `/ns0:OrdrspInterchange/ns0:OrderResponseMessage/ns0:Item/ns0:LineNo` | `/ns0:OrdrspInterchange/OrderResponseMessage/Item/LineNo` |
| Why it was a candidate | Every element is qualified in the XSD | The pattern seen in our older references (MAT, CCM), whose children are *unqualified* |
| Your result in CPI | **Worked**: the tree shows `ns0:` on every node | **Failed**: `OrderResponseMessage` shown in orange as "not found" |

**Lesson:** when the XSD says `elementFormDefault="qualified"`, every element step gets the prefix; attributes (`@Type`) never do. Where the XSD is unqualified (MAT, the S/4 WSDL in NShift), only the root does.

### 1.3 Why you had to "Add source message" by hand (v1.0.1 → v1.0.2)
The mapping links to its source XSD with a few `<elem>` values. Compare my build with your CPI download:

| My v1.0.1 build | Your CPI download (and v1.0.2 onwards) |
|---|---|
| `<elem>Ordrsp_1_0_0.xsd</elem>`<br>`<elem>src/main/resources/xsd</elem>`<br>`<elem>OrdrspInterchange</elem>` | `<elem>Ordrsp_1_0_0.xsd</elem>`<br>`<elem>src/main/resources/xsd</elem>`<br>`<elem>OrdrspInterchange</elem>`<br>**`<elem>http://www.ruukki.com/…/eruukki</elem>`** |

The root `OrdrspInterchange` lives in a namespace, so CPI needs the namespace to find it: "the element `OrdrspInterchange` **in** namespace `…/eruukki`". Without the 4th `<elem>`, CPI looked for `OrdrspInterchange` with no namespace, found nothing, and asked you to add the source message. When you re-added it, CPI wrote the 4th `<elem>`. Your download showed that, and the toolkit has written it ever since.

### 1.4 The simulator error `prefix "ns6" … not bound` (separate issue)
The hub root also carries `xmlns:xsi="…" xsi:schemaLocation="…"`. The mapping **simulator** turns those root attributes into editable fields and loses the `xsi` declaration on the way. That's a simulator limitation, not a mapping problem. Fix for testing: `tools/sim_copy.py` makes a `*_sim.xml` copy without those two attributes.

---

## Part 2 — NShift: a WSDL whose types live on the internet

### 2.1 The problem: `Target.wsdl` only *points* to its types
```
Target.wsdl
  <types>
    <schema targetNamespace=".../consignment/types">           ← defines 'book', 'save' …
      <import namespace=".../consignment/types/v1_0"
              schemaLocation="https://service.web-ta.net/ws/services/ConsignmentWS?xsd=1"/>   ← Consignment, Part, GoodsItem …
      <import namespace=".../common/webservice/types/v1_0"
              schemaLocation="https://service.web-ta.net/ws/services/ConsignmentWS?xsd=2"/>   ← AuthenticationToken
      <complexType name="book">
        <element name="Consignment" type="ns2:Consignment"/>   ← defined only in xsd=1, on the internet
```
CPI does **not** download `schemaLocation` URLs. So `book` was there but empty: no `Consignment`, no `Part`. That's why loading the WSDL by hand did not work either.

### 2.2 The fix: put the downloaded types inside the WSDL
With your approval I downloaded `?xsd=1` and `?xsd=2` (kept unchanged in `schemas/downloaded/`). `tools/wsdl_inline.py` then builds `NShift_ConsignmentWS.wsdl` the way SAP's own WSDLs look (CostCentre, JournalEntry, BusinessPartner in `_reference/`): several schemas side by side inside `<types>`, connected by imports **without** a URL.

| Before (`Target.wsdl`) | After (`NShift_ConsignmentWS.wsdl`) |
|---|---|
| 1 schema in `<types>` | 3 schemas in `<types>` |
| `<import namespace="…/v1_0" schemaLocation="https://…?xsd=1"/>` | `<import namespace="…/v1_0"/>` (no URL: "it's right here") |
| types `Consignment`, `Part` … **missing** | `<xsd:schema targetNamespace="…/v1_0">` with `Consignment`, `Part`, `GoodsItem` … |
| `AuthenticationToken` **missing** | `<xsd:schema targetNamespace="…/common/webservice/types/v1_0">` with `AuthenticationToken` |

Your original `Target.wsdl` is unchanged. The zip uses the self-contained copy.

### 2.3 Why the first attempt (v1.0.0) was still empty in CPI: a lost "tns"
Inside the downloaded XSD, types refer to each other with a short name, e.g. `type="tns:Part"`. What `tns` means is declared once, on the schema's first line. Compare that first line:

| v1.0.0 (broken) | v1.0.1 (fixed) |
|---|---|
| `<xsd:schema xmlns:xsd="…XMLSchema" targetNamespace="…/consignment/types/v1_0">` | `<xsd:schema xmlns:xsd="…XMLSchema" `**`xmlns:tns="…/consignment/types/v1_0"`**` targetNamespace="…/consignment/types/v1_0">` |

When I moved the schema into the WSDL, the library I used dropped `xmlns:tns`, because `tns` only appears inside text values like `type="tns:Part"`. The WSDL's own first line also defines `tns`, as a different namespace: `xmlns:tns="http://www.spedpoint.com/consignment"`. So `tns:Part` suddenly meant "Part in `…/consignment`", where no Part exists. **151 references pointed nowhere** and CPI showed an empty Consignment.

**Fix:** the tool now copies each schema as text, keeping its own first line intact. It also test-compiles the result before writing. And every build now runs check 6: every `type=` / `ref=` in a zip's XSD/WSDL must resolve (the v1.0.0 zip fails it with 151 errors).

### 2.4 Which name the mapping uses for the target message
A WSDL has a *message* (`ConsignmentEndpoint_book`) that contains an *element* (`book`). In all our references both names are the same, so we couldn't tell which one CPI wants. I used the element name `book`, and your import of v1.0.1 loaded the full structure, so it's **confirmed**: the element name (FORMAT_NOTES §2.2).

---

## Summary
| Problem | Visible symptom | Cause | Fix | Guard now |
|---|---|---|---|---|
| Namespaced source, root-only prefix | Fields orange / "not found" | Every element is qualified | `ns0:` on every element step | FORMAT_NOTES §2.2 |
| Source link without namespace | "Add source message" | CPI looks up the root by name **and** namespace | 4th `<elem>` = namespace | Toolkit writes it |
| `xsi:` attributes on the root | Simulator `prefix "ns6" not bound` | Simulator limitation | `*_sim.xml` copies | `tools/sim_copy.py` |
| WSDL imports XSDs by URL | Empty `book` / Consignment | CPI doesn't fetch URLs | Inline the downloaded XSDs | CLAUDE.md rule, `tools/wsdl_inline.py` |
| Lost `xmlns:tns` when inlining | Still empty | Library dropped an "unused" declaration | Copy as text + test-compile | Build check 6 |
