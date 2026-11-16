import com.sap.it.api.mapping.*

/*
 * getBuyerOrderId(orderId)
 *
 * The Tibnor order number from the hub's BuyersOrderId: the part before the first '-'.
 * Without a '-' the whole value is returned.
 *
 * EXAMPLES
 *   getBuyerOrderId("46536694-90")  -> "46536694"
 *   getBuyerOrderId("46536694")     -> "46536694"
 *
 * WHY A UDF
 *   No standard function cuts a value at a variable position: 'substring' has a fixed start and count.
 *
 * ORIGIN
 *   Same logic as the local PO UDF getBuyerOrderId of mapping FIN_DeliveryBatch_to_DESADV93A_TIBNOR
 *   (reference/PO-UDF_FIN_DeliveryBatch_to_DESADV93A_TIBNOR_getBuyerOrderId.txt), rewritten in Groovy.
 */
def String getBuyerOrderId(String orderId) {
    if (orderId == null) {
        return orderId
    }
    int pos = orderId.indexOf("-")
    return (pos >= 0) ? orderId.substring(0, pos) : orderId
}
