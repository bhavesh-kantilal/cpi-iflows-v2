---
name: ssab-smart-switch-msap
description: "SSAB Smart Switch concept (MSAP AQ1/AP1 switching on IS TEST) and Bhavesh's SSAB documentation writing style"
metadata:
  node_type: memory
  type: project
  originSessionId: 05286f0f-aa69-490c-8cda-bbec9703918f
  modified: 2026-11-19T04:45:44.296Z
---

**Concept (2026-11-19).** On IS TEST, MSAP interfaces switch per interface between AQ1 (AQ1CLNT100) and AP1 (AP1CLNT100). External systems stay fixed on IS TEST.

**Outbound (MSAP → IS):**
- I2001_P_IDocDispatcher_MSAP_IDocToPD and I2005_P_SOAPDispatcher_MSAP_SOAPToPD have a Router "Sender System Filtering?" with condition `${property.SenderSystemFiltering}='true'`.
- SenderSystemFiltering is an externalized parameter and is true only on TEST. PROD always takes the default route.
- Groovy (IdocDispatcher / SOAPDispatcher) reads Partner Directory partner MSAP_OutboundInterfaces:
  - ID = VM_Key without "/"
  - value = `LS(s)|IF names`, eg: `AQ1CLNT100-AP1CLNT100` allows both
  - fallback is DefaultSystem
- The script sets CH_ProcessFurther.
- Sender LS:
  - IDoc: SNDPRN
  - SOAP: SapAuthenticatedUserName matched via partner MSAP_UserAccounts. LogicalSystems list + one entry per LS holding the technical user. A BTP client ID can't be the PD key because it contains `!` and `|`.

**Inbound (IS → MSAP):**
- IDoc: switch the ProcessDirect between I2004_P_IDocReceiver_MSAP_PDToIdoc (AQ1) and I2004_P_IDocReceiver_MSAP_Additional_PDToIdoc (AP1). The Additional iFlow never goes to PROD.
- SOAP/OData: the address is switched in the iFlow's receiver channel.

**SSAB Atlas** (https://atlas-test.ssab.com) shows the project where each interface points. Atlas uses the IS view: its "Outbound Endpoints" means IS → MSAP.

**Deliverables:** made outside the repo, in OneDrive Downloads/SSAB_SmartSwitch_MSAP/ (pptx, docx, drawio). The user said: nothing goes into the repo, and no iFlows change.

**Writing style for SSAB docs:**
- Match SSAB_IntegrationSuite_Best Practises.docx / SSAB_Simplified_Pipeline_Draft.docx: Heading3/4/5, short factual sentences, "eg:", "Things to note:" bullet lists.
- Capitalised Interface / IFlow / Partner.
- Groovy shown as grey-shaded Courier snippets, GridTable1Light-Accent1 tables.
- No AI filler, precise and concise.
- Decks use the navy/teal/amber theme of Interface_Connectivity_And_Switching_Between_AQ1_AP1.pptx: kicker + title, few slides, draw.io diagrams.

**Why:** the user asked to remember the concept and the writing style for later documentation.
**How to apply:** reuse this for any SSAB doc or deck about MSAP switching. Don't change iFlows for it.
