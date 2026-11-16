# I0544_BusinessPartner_FSAP_StreamServeDDS_PDToJDBC

Receives one BP from I0711 (ProcessDirect `/I0544_BusinessPartner_FSAP_StreamServeDDS_PDToJDBC`), removes `xsi:nil` (XSLT), maps it to the DDS table and writes it over JDBC (`JDBC_Alias=StreamServeDDS`).

- Source: `iflows/FSAPControllingMasterData_artifacts.zip` (user's package export, 2026-11-16) → `I0544_BusinessPartner_FSAP_StreamServeDDS_JMSToJDBC`
- Build: `py -I tools/iflow_build_fsap_dispatcher.py --only I0544_BusinessPartner_FSAP_StreamServeDDS_PDToJDBC` (`build_i0544_streamserve_child`, `_bp_streamserve_specific`)

## Decisions
| Date | Question | Answer | Impact |
|---|---|---|---|
| 2026-11-16 | Name | `I0544_BusinessPartner_FSAP_StreamServeDDS_PDToJDBC` (user confirmed) | New iFlow |
| 2026-11-16 | JDBC parameter names | No preference, so the recommended option: `JDBC_*`, typo fixed | Renamed parameters |
| 2026-11-16 | Partner group filter is a hard-coded XPath (Z001/Z002/Z003/Z005), not `{{PartnerGroupCodes}}` as in the Medius child | Left unchanged (logic). To decide later | Open |
