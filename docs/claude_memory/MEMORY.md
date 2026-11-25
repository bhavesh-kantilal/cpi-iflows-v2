# Memory index

- [iFlow folder structure](feedback_iflow_folder_structure.md) — one folder per iFlow under `iflows/<IFlowName>/`, not a flat shared folder
- [iFlow version comment](project_iflow_version_comment.md) — CPI version history comment is server-side only; ZIP can only set `Bundle-Version` in MANIFEST.MF
- [JMS dispatcher architecture](../../../work/cpi-mappings/docs/explained/jms_dispatcher_architecture.md) — one queue per receiver, parent→dispatcher→child pattern; see also iflow_scan_findings.md
- [BPMN rfind bug](feedback_bpmn_rfind_bug.md) — when regex match starts at element opening tag, use `m.start()` directly — rfind with end=`m.start()+1` always returns -1 and corrupts the XML by doubling content
- [SSAB Smart Switch + writing style](project_ssab_smart_switch.md) — MSAP AQ1/AP1 switch: PD sender check outbound, I2004 Additional inbound, Atlas; SSAB doc style
- [iFlow spec.md per folder](project_iflow_spec_pending.md) — answered yes (2026-11-16); create spec.md with each iFlow feedback round
