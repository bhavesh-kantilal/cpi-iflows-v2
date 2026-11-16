# CHANGELOG — I0711_P_JMSDispatcher_StreamServe

## 1.0.1 — 2026-11-16 11:40 CET
DLQ JMS receiver renamed from `Receiver1` to `StreamServeDispatcher_DLQ` (user rule: <sender>_DLQ; already applied by the user on the tenant). JMS sender channel system set to `StreamServeDispatcher`, matching its participant; it had the template's `SmarTeamJMSDispatcher`. No logic changes.

## 1.0.0 — 2026-11-16 11:55 CET
New StreamServe JMS dispatcher (user: next number in the series, 711). It is cloned from I0701_P_JMSDispatcher_MSAP_PlantMaintenance in the same way as I0710_P_JMSDispatcher_Medius.
- Queue `I0711_StreamServe`, DLQ `I0711_StreamServe_D`. It calls the child named in the header `SSAB_Dispatcher_ReceiverIFlow` over ProcessDirect.
- `SAP_Sender=FD1_110`. I0710 has `DR1_350` from its v1.0.0 build.
