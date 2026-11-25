---
name: project_iflow_version_comment
description: CPI version history comment cannot be set via ZIP — only via manual import in CPI UI
metadata: 
  node_type: memory
  type: project
  originSessionId: 01ea7e07-de20-45b3-a5cd-f7cca422ff8b
---

The version comment visible in CPI's version history list is stored server-side by CPI and is NOT written into the exported ZIP. Even after the user sets a comment and re-exports, `metainfo.prop` still has `description=` empty.

What CAN be set via ZIP:
- `META-INF/MANIFEST.MF` → `Bundle-Version:` sets the version number shown in CPI

What CANNOT be set via ZIP:
- The version history comment/description — only the user can set this when importing in CPI UI

**How to apply:** when building an iFlow ZIP, only bump `Bundle-Version`. Always tell the user what to type in the Comment field of the "Integration Flow Details" import dialog — that is the only way to set the version history comment. Format: "When importing, type in the Comment field: `<change text>`"
