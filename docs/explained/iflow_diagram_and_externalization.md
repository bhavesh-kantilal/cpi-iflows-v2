# iFlow lessons from the I0539 feedback (2026-11-16)

## 1. Why "the connection was missing"
An `.iflw` file has two parts:
- **Process model** (`bpmn2:process`, `bpmn2:sequenceFlow`, …): what runs.
- **Diagram** (`bpmndi:BPMNDiagram`): where CPI draws each step (`BPMNShape`) and each arrow (`BPMNEdge`).

The v1.0.0 build rewrote "Integration Process from Source" in the model (Start → Main Process → End) but did not touch the diagram. The new flows had no `BPMNEdge`, so CPI drew no arrows. Shapes of the removed steps (Max Retries gateway, Send to DLQ, CPI_DLQ) were still there too.

**Fix:** `tools/iflow_lib.py`
- `fix_diagram` drops orphan shapes and edges, places the steps, and draws an edge for every flow.
- `check_iflow` fails the build when a flow has no edge, an edge points to the wrong shape, or a shape has no step.

`py -I tools/check_all_iflows.py` runs the same checks on every built iFlow.

## 2. Externalization
Bhavesh's rule: "the more the better". Every adapter setting someone may want to change per tenant becomes a `{{Parameter}}`:
- HTTP receivers: `HTTP_Timeout`, `HTTP_ProxyType`, `HTTP_ThrowExceptionOnFailure`, `HTTP_Authentication`, retry settings, allowed headers, and `Medius_Host` in the address.
- HTTPS sender: `HTTP_UserRole`, `HTTP_CSRFProtected`, `HTTP_MaxBodySize`.
- ProcessDirect sender: `PD_Address`. This must equal the iFlow name that the dispatcher calls.
- A value inside a Content Modifier body (`ErpSourceId`) is put into a property with a constant `{{Medius_ErpSourceId}}` row. The body then reads `${property.ErpSourceId}`.

Each parameter needs three things: the `{{…}}` in the `.iflw`, a line in `parameters.prop`, and an entry in `parameters.propdef` (plus a `param_references` entry linking it to the adapter field). `iflow_lib.Params` keeps prop and propdef in step. The check flags a parameter that is used but missing, or defined but unused.

## 3. Renaming a parameter
Renaming `AlowedCompanies` to `AllowedCompanies` creates a new parameter in CPI. A value already configured on the tenant under the old name is not carried over, so set it again after import.
