import com.sap.gateway.ip.core.customdev.util.Message;
//import java.util.HashMap;

def Message processData(Message message) {
    // Begin: 20260929 - Streaming optimization to clear XMLSlurper warning
    // def body = message.getBody(java.lang.String);
    // def root = new XmlSlurper().parseText(body);
    def reader = message.getBody(java.io.Reader.class);
    def root = new XmlSlurper().parse(reader);
    // End: 20260929 - Streaming optimization to clear XMLSlurper warning
    
    root.declareNamespace('n0': 'http://sap.com/xi/SAPGlobal20/Global')
    
    def arr_receiversQueueList = [];
    def arr_receiversIFlowList = [];
    def counter = 0
    
    def map = message.getProperties();

    def productTypeCode = root.'ProductMDMReplicateRequestMessage'
                               .'Product'
                               .'ProductTypeCode'
                               ?.text()?.trim()

    def allowedCodes = ["ZFER", "ZDIR", "ZPAC", "ZBYP", "ZSER", "ZCON"]

    // Always send to I2018_FSAP
    arr_receiversQueueList.add("I2018_FSAP")
    arr_receiversIFlowList.add("I2018_FSAP")
    counter++

    // Only send to I2018_PSI if ProductTypeCode matches
    if (allowedCodes.contains(productTypeCode)) {
        arr_receiversQueueList.add("I2018_PSI")
        arr_receiversIFlowList.add("I2018_PSI")
        counter++
    }
    
// Begin: 20260929 USR500241 - Additional receiver criteria	
    def allowedPaternosterCodes = ["ZCON", "ZSPA"]
    def allowedPaternosterWarehouses = ["2910", "2913"]
    def allowedPaternosterStorageType = "PA00"
	
    // Locate EWMWarehouse nodes
    def ewmWarehouseNodes = root.'ProductMDMReplicateRequestMessage'.'Product'.'EWMWarehouse'

    // Check if any EWMWarehouse block matches the warehouse criteria AND has the storage strategy value in either field
    def hasMatchingEwmCriteria = ewmWarehouseNodes.any { wh ->
        def whNumber = wh.'EWMWarehouseNumber'?.text()?.trim()
        def ptwyStrat = wh.'EWMPtwyControlStrategy'?.text()?.trim()
        def removalStrat = wh.'EWMStockRemovalControlStrategy'?.text()?.trim()

        def isAllowedWarehouse = allowedPaternosterWarehouses.contains(whNumber)
        def isAllowedStorageType = (ptwyStrat == allowedPaternosterStorageType || removalStrat == allowedPaternosterStorageType)

        return isAllowedWarehouse && isAllowedStorageType
    }

    // Send to I0257_PATER if ProductTypeCode and EWM warehouse criteria matches
    if (allowedPaternosterCodes.contains(productTypeCode) && hasMatchingEwmCriteria) {
        arr_receiversQueueList.add("I0257_PATER")
        arr_receiversIFlowList.add("I0257_PATER")
        counter++
    }
// End: 20260929 USR500241 - Additional receiver criteria


// Start 20261005 - USR375821 - criteria for SmartTeam*

/*  ZSPA Spare Part 
    ZNST Non-Stock Purchase parts 
    ZCON Consumables 
    ZSER Service
*/

  def allowedSmartTeamMateriarTypes = ["ZSPA", "ZNST","ZCON", "ZSER"]
  // Send to I0257_PATER if ProductTypeCode and EWM warehouse criteria matches
    if (allowedSmartTeamMateriarTypes.contains(productTypeCode) ) {
        arr_receiversQueueList.add("I0700_SmarTeam")
        arr_receiversIFlowList.add("I2018_Material_MSAP_SmarTeam_JMSToHTTP")
        counter++
    }

// End 20261005 - USR375821 - criteria for SmartTeam


    message.setProperty("arr_receiversQueueList", arr_receiversQueueList);
    message.setProperty("arr_receiversIFlowList", arr_receiversIFlowList);
    message.setProperty("arr_receiversLastIndex", counter - 1);
    return message;
}