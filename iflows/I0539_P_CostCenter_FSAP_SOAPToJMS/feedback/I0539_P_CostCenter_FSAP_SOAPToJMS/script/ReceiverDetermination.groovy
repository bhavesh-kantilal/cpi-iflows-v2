import com.sap.gateway.ip.core.customdev.util.Message

def Message processData(Message message) {
    def arr_receiversQueueList = []
    def arr_receiversIFlowList = []
    def counter = 0

    // Medius -> I0702 common dispatcher queue
    arr_receiversQueueList.add("I0710_Medius")
    arr_receiversIFlowList.add("I0539_CostCenter_FSAP_Medius_PDToREST")
    counter++

    // Oracle -> dedicated queue (dummy: iFlow name = queue name)
    arr_receiversQueueList.add("I0539_ORACLE")
    arr_receiversIFlowList.add("I0539_ORACLE")
    counter++
    
     // MSAP -> dedicated queue (dummy: iFlow name = queue name)
    arr_receiversQueueList.add("I0540_MSAP")
    arr_receiversIFlowList.add("I0540_MSAP")
    counter++

    message.setProperty("arr_receiversQueueList", arr_receiversQueueList)
    message.setProperty("arr_receiversIFlowList", arr_receiversIFlowList)
    message.setProperty("arr_receiversLastIndex", counter - 1)
    return message
}
