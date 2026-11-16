# I0711_P_JMSDispatcher_StreamServe

Consumes queue `I0711_StreamServe` and calls the StreamServe child named in `SSAB_Dispatcher_ReceiverIFlow` over ProcessDirect (`/${header.SSAB_Dispatcher_ReceiverIFlow}`). After `MaxRetries` tries the message goes to the DLQ `I0711_StreamServe_D`.

- Source: `_reference/iflows/I0701_P_JMSDispatcher_MSAP_PlantMaintenance.zip`
- Build: `py -I tools/iflow_build_fsap_dispatcher.py --only I0711_P_JMSDispatcher_StreamServe` (`build_dispatcher`, shared with I0710)
- Senders today: `I0544_P_BusinessPartner_FSAP_SOAPToJMS` → child `I0544_BusinessPartner_FSAP_StreamServeDDS_PDToJDBC`
- **Create the queue `I0711_StreamServe` in CPI before you deploy.**

## Decisions
| Date | Question | Answer | Impact |
|---|---|---|---|
| 2026-11-16 | Number and names for the StreamServe dispatcher | User: next number 711. Name `I0711_P_JMSDispatcher_StreamServe`, queue `I0711_StreamServe`, DLQ `I0711_StreamServe_D` (confirmed) | New dispatcher |
| 2026-11-16 | Template parameters not used by the flow (IDoc_Authorization, Sender/Receiver_Agency, UserRole=SSAB_MessagingSend_StripSAP, …) | Kept as in I0710 (same template). Clean both dispatchers together later | Open |
| 2026-11-16 | DLQ receiver name | `<Sender>_DLQ` → `StreamServeDispatcher_DLQ` (user rule) | 1.0.1 |
