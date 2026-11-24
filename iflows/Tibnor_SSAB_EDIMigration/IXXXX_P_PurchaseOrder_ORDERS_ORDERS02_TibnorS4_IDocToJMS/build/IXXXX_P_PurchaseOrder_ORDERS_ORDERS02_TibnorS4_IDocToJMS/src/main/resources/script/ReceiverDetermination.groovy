import com.sap.gateway.ip.core.customdev.util.Message

/*
 * Receiver determination for IXXXX_P_PurchaseOrder_ORDERS_ORDERS02_TibnorS4_IDocToJMS
 * RCVPRN comes from property RCVPRN, set by XPath /ORDERS02/IDOC/EDI_DC40/RCVPRN in
 * "Set Monitoring Identifiers": no payload parsing for a value one XPath can read (user, 2026-11-24).
 * RCVPRN can be a partner number (0000025200) or a logical system / alphanumeric name
 * (e.g. TS4CLNT100): leading zeros are removed only when the value is all digits
 * (0000025200 = 25200); any other value is compared as it is (trimmed).
 * No receiver found: the lists stay empty, arr_receiversLastIndex = -1 and the
 * "Receivers Exist?" router sends the message to the Error End.
 */
def Message processData(Message message) {

    def arr_receiversQueueList = []
    def arr_receiversIFlowList = []

    def rcvprn = (message.getProperty("RCVPRN") ?: "").toString().trim()
    if (rcvprn ==~ /\d+/) {
        rcvprn = rcvprn.replaceFirst(/^0+(?!$)/, '')
    }

    if (rcvprn == "25200") {
        arr_receiversQueueList.add("I0707_FinMessageHub")
        arr_receiversIFlowList.add("IXXXX_PurchaseOrder_ORDERS_ORDERS02_TibnorS4_FinMessageHub_HameenlinnaMetocs_JMSToMQ")
    }

    message.setProperty("arr_receiversQueueList", arr_receiversQueueList)
    message.setProperty("arr_receiversIFlowList", arr_receiversIFlowList)
    message.setProperty("arr_receiversLastIndex", arr_receiversQueueList.size() - 1)

    return message
}
