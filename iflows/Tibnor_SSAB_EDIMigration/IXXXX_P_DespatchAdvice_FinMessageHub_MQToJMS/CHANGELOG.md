# CHANGELOG — IXXXX_P_DespatchAdvice_FinMessageHub_MQToJMS

## 1.0.0 — 2026-11-24 19:40 CET
- First build, same shape as the ORDRSP parent (IBM MQ sender of I2017, queue `IXXXX_TibnorS4`).
- Receiver determination as the PO conditions: recipient GLN in `FinMessageHub_AllowedRecipients`; SourceSystem METOCS* → Metocs; else InterchangeSender → Hämeenlinna / Raahe Tilkku; no match → Error End.
- All build checks passed.
