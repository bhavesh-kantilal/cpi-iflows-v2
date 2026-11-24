import com.sap.gateway.ip.core.customdev.util.Message

/*
 * Receiver determination for IXXXX_P_OrderResponse_FinMessageHub_MQToJMS
 * The mill comes from Header/ApplicationId, read by XPath into property CH_FinMessageHubApplicationId in
 * "Set Monitoring Identifiers": no payload parsing here (user, 2026-11-24).
 *   METOCS*  -> Hameenlinna Metocs, TILKKUHA -> Hameenlinna Tilkku, TILKKURA -> Raahe Tilkku
 * No receiver found: the lists stay empty, arr_receiversLastIndex = -1 and the
 * "Receivers Exist?" router sends the message to the Error End.
 */
def Message processData(Message message) {

    def arr_receiversQueueList = []
    def arr_receiversIFlowList = []

    def appId = (message.getProperty("CH_FinMessageHubApplicationId") ?: "").toString().trim()

    if (appId.startsWith("METOCS")) {
        arr_receiversQueueList.add("IXXXX_TibnorS4")
        arr_receiversIFlowList.add("IXXXX_OrderResponse_FinMessageHub_HameenlinnaMetocs_TibnorS4_JMSToIDoc")
    }
    else if (appId == "TILKKUHA") {
        arr_receiversQueueList.add("IXXXX_TibnorS4")
        arr_receiversIFlowList.add("IXXXX_OrderResponse_FinMessageHub_HameenlinnaTilkku_TibnorS4_JMSToIDoc")
    }
    else if (appId == "TILKKURA") {
        arr_receiversQueueList.add("IXXXX_TibnorS4")
        arr_receiversIFlowList.add("IXXXX_OrderResponse_FinMessageHub_RaaheTilkku_TibnorS4_JMSToIDoc")
    }

    message.setProperty("arr_receiversQueueList", arr_receiversQueueList)
    message.setProperty("arr_receiversIFlowList", arr_receiversIFlowList)
    message.setProperty("arr_receiversLastIndex", arr_receiversQueueList.size() - 1)

    return message
}
