import com.sap.gateway.ip.core.customdev.util.Message

/*
 * Receiver determination for IXXXX_P_PurchaseOrder_ORDERS_ORDERS02_TibnorS4_IDocToJMS
 * Reads EDI_DC40/RCVPRN of the ORDERS02 IDoc. Leading zeros are ignored (0000025200 = 25200).
 * No receiver found: the lists stay empty, arr_receiversLastIndex = -1 and the
 * "Receivers Exist?" router sends the message to the Error End.
 */
def Message processData(Message message) {

    def arr_receiversQueueList = []
    def arr_receiversIFlowList = []

    def idoc = new XmlSlurper().parseText(message.getBody(String) as String)
    def rcvprn = idoc.IDOC.EDI_DC40.RCVPRN.text().trim().replaceFirst(/^0+(?!$)/, '')

    if (rcvprn == "25200") {
        arr_receiversQueueList.add("I0707_FinMessageHub")
        arr_receiversIFlowList.add("IXXXX_PurchaseOrder_ORDERS_ORDERS02_TibnorS4_FinMessageHub_HameenlinnaMetocs_JMSToMQ")
    }

    message.setProperty("arr_receiversQueueList", arr_receiversQueueList)
    message.setProperty("arr_receiversIFlowList", arr_receiversIFlowList)
    message.setProperty("arr_receiversLastIndex", arr_receiversQueueList.size() - 1)

    return message
}
