---
name: project-repo-split-v2
description: Since 2026-11-27 work continues in C:\work\cpi-mappings-v2 and C:\work\cpi-iflows-v2; the original cpi-mappings repo is frozen as a fallback
metadata:
  node_type: memory
  type: project
  originSessionId: 7d1bc4af-002b-4526-951b-daba81a1eb55
  modified: 2026-11-27T07:39:51.193Z
---

On 2026-11-27 the repo was split (Part 1 of the approved plan):
- `C:\work\cpi-mappings-v2`: mapping development (GitHub bhavesh-kantilal/cpi-mappings-v2, private).
- `C:\work\cpi-iflows-v2`: iFlow development, with cpi-mappings-v2 as a git submodule in `cpi-mappings-v2/` (GitHub bhavesh-kantilal/cpi-iflows-v2, private).
- `C:\work\cpi-mappings` stays unchanged at 8d10234.

**Why:** The user wants to share mappings alone or both together, and keep the original untouched in case something goes wrong.

**How to apply:** Never edit, commit or push in C:\work\cpi-mappings. Next steps: Part 2 (SSAB/Tibnor customer skill, generic vs customer-specific rules, customer checklist) and Part 3 (fix out-of-date items), each only after the user's OK. Both clones need `core.longpaths true`. See [[feedback-small-modular-answers]].
