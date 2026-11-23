# CHANGELOG — I2049_MaterialBOM_MSAP_SmarTeam_PDToHTTP

## 1.0.2 — 2026-11-15 21:00 CET
Added Send to SmarTeam (ExternalCall/HTTP POST to smarteam-test.ssab.com), Set AttachmentName = SmartTeamResponse, and Log Payload (response) steps after the existing output-payload log. Confirmed working in CPI.

## 1.0.1 — baseline (user)
Initial iFlow: JMS receiver → mapping (MaterialBOM_Mapping.mmap) → Set AttachmentName(OutputPayload) → Log Payload → End.
