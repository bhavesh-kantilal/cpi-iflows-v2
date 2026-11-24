import com.sap.gateway.ip.core.customdev.util.Message

/*
 * Receiver determination for IXXXX_P_Invoice_FinMessageHub_MQToJMS
 * All values are read by XPath in "Set Monitoring Identifiers": no payload parsing here (user, 2026-11-24).
 * As the PO conditions (user, 2026-11-24): only for a recipient GLN in property AllowedRecipients, then
 *   SourceSystem METOCS*  -> Hameenlinna Metocs
 *   else by mill GLN (InterchangeSender): 00372389445751 -> Hameenlinna Tilkku, 00372389445741 -> Raahe Tilkku
 * No receiver found: the lists stay empty, arr_receiversLastIndex = -1 and the
 * "Receivers Exist?" router sends the message to the Error End.
 */
def Message processData(Message message) {

    def arr_receiversQueueList = []
    def arr_receiversIFlowList = []

    def sourceSystem = (message.getProperty("CH_FinMessageHubSourceSystem") ?: "").toString().trim()
    def sender = (message.getProperty("FinMessageHubSender") ?: "").toString().trim()
    def recipient = (message.getProperty("FinMessageHubRecipient") ?: "").toString().trim()
    def allowedRecipients = (message.getProperty("AllowedRecipients") ?: "").toString().trim().split(",")*.trim()

    if (allowedRecipients.contains(recipient)) {
        if (sourceSystem.startsWith("METOCS")) {
            arr_receiversQueueList.add("IXXXX_TibnorS4")
            arr_receiversIFlowList.add("IXXXX_Invoice_FinMessageHub_HameenlinnaMetocs_TibnorS4_JMSToIDoc")
        }
        else if (sender == "00372389445751") {
            arr_receiversQueueList.add("IXXXX_TibnorS4")
            arr_receiversIFlowList.add("IXXXX_Invoice_FinMessageHub_HameenlinnaTilkku_TibnorS4_JMSToIDoc")
        }
        else if (sender == "00372389445741") {
            arr_receiversQueueList.add("IXXXX_TibnorS4")
            arr_receiversIFlowList.add("IXXXX_Invoice_FinMessageHub_RaaheTilkku_TibnorS4_JMSToIDoc")
        }
    }

    message.setProperty("arr_receiversQueueList", arr_receiversQueueList)
    message.setProperty("arr_receiversIFlowList", arr_receiversIFlowList)
    message.setProperty("arr_receiversLastIndex", arr_receiversQueueList.size() - 1)

    return message
}
