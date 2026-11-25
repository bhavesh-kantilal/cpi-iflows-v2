---
name: bpmn-rfind-bug
description: "rfind bug when removing BPMN elements whose regex match starts at the element opening — always use match.start() directly, not rfind"
metadata: 
  node_type: memory
  type: feedback
  originSessionId: 01ea7e07-de20-45b3-a5cd-f7cca422ff8b
---

When removing a `bpmn2:messageFlow` (or any BPMN element) by regex, if the regex pattern starts with the element's opening tag (e.g. `<bpmn2:messageFlow id="..."`), `mf_m.start()` already points to the element start. Using `xml.rfind("<bpmn2:messageFlow", 0, mf_m.start() + 1)` ALWAYS returns -1 because the 18-char pattern can't fit in the 1-char window ending at `mf_m.start() + 1`.

**Why:** `rfind(sub, 0, end)` requires the entire substring to fit in `s[0:end]`. A match of `<bpmn2:messageFlow` (18 chars) starting at position `P` only fits in `s[0:end]` if `P + 18 <= end`. With `end = P + 1`, that's `P + 18 <= P + 1`, which is never true.

**How to apply:** Always use `mf_start = mf_m.start()` directly. Same applies to participant removal: use `pid_m.start()` not `rfind`. When `rfind` returns -1, `mf_end = -1 + len(closing_tag)` becomes a small positive number, so `xml[:mf_start] + xml[mf_end:]` = `xml[:-1] + xml[19:]` — this doubles the entire file content. The corruption manifests as two concatenated XML documents, caught by lxml as "expected '>', line N, column 21".

**Fixed in:** `tools/iflow_build_fsap_dispatcher.py` → `_remove_participant_and_mf()` (commit 851ffdf).
