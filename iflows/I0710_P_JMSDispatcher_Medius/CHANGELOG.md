# CHANGELOG — I0710_P_JMSDispatcher_Medius

## 1.0.1 — 2026-11-16 11:40 CET
DLQ JMS receiver renamed from `Receiver1` to `MediusDispatcher_DLQ` (user rule: <sender>_DLQ; already applied by the user on the tenant). JMS sender channel system set to `MediusDispatcher`, matching its participant; it had the template's `SmarTeamJMSDispatcher`. No logic changes.

## 1.0.0 — 2026-11-15
New Medius JMS dispatcher for FSAP→Medius interfaces. Cloned from I0701_P_JMSDispatcher_MSAP_PlantMaintenance. Queue: I0710_Medius, DLQ: I0710_Medius_D. Routes via ProcessDirect to child iFlow named in SSAB_Dispatcher_ReceiverIFlow header.

