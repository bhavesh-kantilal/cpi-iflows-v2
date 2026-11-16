# I0544_BusinessPartner_FSAP_Medius_PDToREST

Receives one BP from I0710 (ProcessDirect `/I0544_BusinessPartner_FSAP_Medius_PDToREST`), filters by `PartnerGroupCodes` and `CompanyCodeScope`, splits by account information, maps it to Medius suppliers and POSTs to `supplierImportBatches`.

- Source: `iflows/FSAPControllingMasterData_artifacts.zip` (user's package export, 2026-11-16) → `I0544_BusinessPartner_FSAP_Medius_JMSToREST`
- Build: `py -I tools/iflow_build_fsap_dispatcher.py --only I0544_BusinessPartner_FSAP_Medius_PDToREST` (`build_i0544_medius_child`, `_bp_medius_specific`)

## Decisions
| Date | Question | Answer | Impact |
|---|---|---|---|
| 2026-11-16 | Name | `I0544_BusinessPartner_FSAP_Medius_PDToREST` (user confirmed) | New iFlow |
| 2026-11-16 | `{{ssabQA}}` vs `{{tenantName}}` | Use `tenantName`, like the other Medius children (user) | Renamed parameter |
| 2026-11-16 | ErpSourceId | Already externalized here as `externalSystemId` (kept, no `Medius_ErpSourceId`) | — |
