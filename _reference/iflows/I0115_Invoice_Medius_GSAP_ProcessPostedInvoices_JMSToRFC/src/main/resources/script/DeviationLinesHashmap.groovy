import com.sap.gateway.ip.core.customdev.util.Message
//import groovy.xml.XmlSlurper

def Message processData(Message message) {
    // Get XML payload
    def body = message.getBody(String)
    
    // Parse XML
    def xml = new XmlSlurper().parseText(body)
    
    // Initialize hashmap
    def deviationMap = [:]  // key: codingLineNumbers, value: count of poConnectionLineNumbers
    
    // Iterate over all deviationLines
    xml.invoice.deviationLines.each { deviationLine ->
        def codingLineNumber = deviationLine.codingLineNumbers.text()
        def poCount = deviationLine.poConnectionLineNumbers.size()
        
        // Put in hashmap
        deviationMap[codingLineNumber] = poCount
    }
    
    // Set hashmap as property for further use
    message.setProperty("deviationMap", deviationMap)
    
    return message
}
