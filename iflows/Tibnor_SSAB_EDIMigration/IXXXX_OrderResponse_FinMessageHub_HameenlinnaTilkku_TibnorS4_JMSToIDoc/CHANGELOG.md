# CHANGELOG — IXXXX_OrderResponse_FinMessageHub_HameenlinnaTilkku_TibnorS4_JMSToIDoc

## 1.0.1 — 2026-11-24 20:30 CET
- Mapping `Map_HammelinnaTilkkuHub_TibnorS4_OrderConfirmation_ORDRSP` v1.0.3: no mill check in the mapping (the parent routes by mill), EDI_DC40 from an empty constant.

## 1.0.0 — 2026-11-24 18:10 CET
- First build: flow shape from our ORDERS child, ProcessDirect receiver as I2052 to `T0143_P_IDocReceiver_TibnorS4_PDToIDoc`, mapping `Map_HammelinnaTilkkuHub_TibnorS4_OrderConfirmation_ORDRSP` v1.0.2.
- IDoc control properties SNDPOR/RCVPOR/RCVPRN externalized (empty); Namespace Mapping p1 (UNVERIFIED).
- All build checks passed.
