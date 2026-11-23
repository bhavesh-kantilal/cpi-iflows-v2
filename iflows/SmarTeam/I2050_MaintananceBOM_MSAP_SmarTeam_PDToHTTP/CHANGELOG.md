# CHANGELOG — I2050_MaintananceBOM_MSAP_SmarTeam_PDToHTTP

> Continued as `iflows/SmarTeam/I2050_MaintenanceBOM_MSAP_SmarTeam_JMSToHTTP/` from v1.0.4 (2026-11-23: typo fixed, new _JMSToHTTP naming).

## 1.0.2 — 2026-11-15 21:00 CET
Added Send to SmarTeam (ExternalCall/HTTP POST to smarteam-test.ssab.com), Set AttachmentName = SmartTeamResponse, and Log Payload (response) steps after the existing output-payload log. Confirmed working in CPI.

## 1.0.1 — baseline (user)
Initial iFlow: JMS receiver → mapping (MaintBOM_Mapping.mmap) → Set AttachmentName(OutputPayload) → Log Payload → End.
