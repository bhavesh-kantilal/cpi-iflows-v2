import com.sap.gateway.ip.core.customdev.util.Message

def Message processData(Message message) {

    def arr_receiversQueueList = []
    def arr_receiversIFlowList = [];
    def counter = 0

    arr_receiversQueueList.add("I2023_FSAP")
    arr_receiversIFlowList.add("I2023_FSAP")
    counter++
    arr_receiversQueueList.add("I0700_SmarTeam")
    arr_receiversIFlowList.add("I2023_Equipment_COD_EQUIPMENT_SAVE_COD_EQUIPMENT_SAVE01_MSAP_SmarTeam_JMSToHTTP")
    counter++

    message.setProperty("arr_receiversQueueList", arr_receiversQueueList)
    message.setProperty("arr_receiversIFlowList", arr_receiversIFlowList);
    message.setProperty("arr_receiversLastIndex", counter - 1)

    return message
}