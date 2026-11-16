# CHANGELOG — I0541_InternalOrder_FSAP_Medius_PDToREST

## 1.0.0 — 2026-11-15
New Medius child. ProcessDirect entry replacing JMS consumer (I0541_MEDIUS queue). Internal Order Splitter moved to I0541_P parent; child processes one order at a time. All REST/mapping logic carried over unchanged from I0541 (JMSToREST). Bhavesh, no UDFs were added; ReplaceWithVirtualCompany.groovy copied unchanged.

