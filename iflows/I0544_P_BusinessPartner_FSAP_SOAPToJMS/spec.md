# I0544_P_BusinessPartner_FSAP_SOAPToJMS

Receives the FSAP BusinessPartnerSUITEBulkReplicateRequest and sends one JMS message per receiver: Medius via `I0710_Medius`, StreamServe DDS via `I0711_StreamServe`, and MSAP via its own queue `I0544_MSAP`.

- Source: `iflows/FSAPControllingMasterData_artifacts.zip` (user's package export, 2026-11-16) → `I0544_P_BusinessPartner_FSAP_SOAPToJMS` (its .iflw was named `I0502_P_BusinessPartner_…`, now renamed)
- Build: `py -I tools/iflow_build_fsap_dispatcher.py --only I0544_P_BusinessPartner_FSAP_SOAPToJMS` (`build_i0544_parent`)

## Decisions
| Date | Question | Answer | Impact |
|---|---|---|---|
| 2026-11-16 | Adopt BP to the Medius and StreamServe dispatchers | Yes (user). Same pattern and parameters as the cost center parents | 2.0.0 |
| 2026-11-16 | MSAP receiver (old `I0544_MSAP` queue) | Keep the dedicated queue `I0544_MSAP` with a dummy iFlow name (user) | ReceiverDetermination |
| 2026-11-16 | SAP_Sender | `FD1_110` (user's answer for the FSAP flows) | parameters.prop |
