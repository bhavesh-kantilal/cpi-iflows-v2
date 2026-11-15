import com.sap.gateway.ip.core.customdev.util.Message
import com.sap.it.api.ITApiFactory
import com.sap.it.api.mapping.ValueMappingApi
import groovy.util.XmlSlurper

def Message processData(Message message) {
    def body = message.getBody(String.class)
    def root = new XmlSlurper().parseText(body)
    
    // Get Value Mapping Service
    def valueMappingApi = ITApiFactory.getApi(ValueMappingApi.class, null)
    if (valueMappingApi == null) return message

    // 1. Get Country Code (first 2 chars of COMP_CODE)
    // Example: "TR20" becomes "TR". "TR99" becomes "TR".
    def compCode = root.HEADERDATA.COMP_CODE.text()
    def countryCode = compCode?.length() >= 2 ? compCode.substring(0, 2) : ""
    
    // 2. Find all unique Tax Codes in the document
    def taxCodes = root.TAXDATA.item.TAX_CODE.collect { it.text() }.unique()
    
    // Map to store results: [TaxCode : Percentage]
    def percentageMap = [:]

    // 3. Lookup Percentage for each Tax Code
    taxCodes.each { taxCode ->
        // Construct Key: "TR_X4"
        def sourceValue = "${countryCode}_${taxCode}" 
        
        // Lookup in Value Mapping
        // Name: VM_CompletelyDeductible_TaxCode_To_TaxPercentage
        // Source: TR_X4
        String percentage = valueMappingApi.getMappedValue(
            "GSAP_TaxCode", "TaxCode", sourceValue, 
            "GSAP_TaxPercentage", "TaxPecentage"
        )
        
        if (percentage != null && !percentage.isEmpty()) {
            percentageMap[taxCode] = percentage
        }
    }

    // 4. Store as string property: "|X4=0.20|"
    def mapString = ""
    percentageMap.each { k, v -> mapString += "|${k}=${v}|" }
    
    message.setProperty("taxPercentageMap", mapString)
    
    return message
}