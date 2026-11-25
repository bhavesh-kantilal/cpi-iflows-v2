---
name: feedback_iflow_folder_structure
description: iFlow dev folder layout — one folder per iFlow with input/ and build/ subfolders
metadata: 
  node_type: memory
  type: feedback
  originSessionId: 01ea7e07-de20-45b3-a5cd-f7cca422ff8b
---

Each iFlow under development gets its own folder under `iflows/<IFlowName>/` with two subfolders:
- `input/` — the user drops original/baseline ZIPs here
- `build/` — Claude writes the modified output ZIP here (versioned)
- `CHANGELOG.md` — one entry per version built

Example:
```
iflows/
  I2049_MaterialBOM_MSAP_SmarTeam_PDToHTTP/
    input/   I2049_MaterialBOM_MSAP_SmarTeam_PDToHTTP.zip
    build/   I2049_MaterialBOM_MSAP_SmarTeam_PDToHTTP.zip
    CHANGELOG.md
```

**Why:** user corrected flat `iflowdevelopment/` layout — input and output were mixed in one folder with no separation. Confirmed 2026-11-15.

**How to apply:** whenever starting an iFlow task, create `iflows/<IFlowName>/input/` and `iflows/<IFlowName>/build/`. Never write output into the same folder as the user's input drop.
