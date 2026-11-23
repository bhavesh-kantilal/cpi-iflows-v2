import com.sap.gateway.ip.core.customdev.util.Message

def Message processData(Message message) {

    def arr_receiversQueueList = []
    def arr_receiversIFlowList = [];
    def counter = 0

    // Only one receiver queue
    arr_receiversQueueList.add("I2024_FSAP")
    arr_receiversIFlowList.add("I2024_FSAP")
    counter++
    
    arr_receiversQueueList.add("I0700_SmarTeam")
    arr_receiversIFlowList.add("I2024_FunctionLocation_COD_FUNCTIONAL_LOCATION_SAVE_COD_FUNCTIONAL_LOCATION_SAVE01_MSAP_SmarTeam_JMSToHTTP")
    counter++

    message.setProperty("arr_receiversQueueList", arr_receiversQueueList)
    message.setProperty("arr_receiversIFlowList", arr_receiversIFlowList);
    message.setProperty("arr_receiversLastIndex", counter - 1)

    return message
}