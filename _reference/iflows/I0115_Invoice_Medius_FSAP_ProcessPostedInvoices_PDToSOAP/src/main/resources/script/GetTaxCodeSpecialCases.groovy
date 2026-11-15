import com.sap.gateway.ip.core.customdev.util.Message
import com.sap.it.api.ITApiFactory
import com.sap.it.api.mapping.ValueMappingApi
import groovy.util.XmlSlurper

def Message processData(Message message) {
    def body = message.getBody(String.class)
    def root = new XmlSlurper().parseText(body)
    
    // Get the Value Mapping API service
    def valueMappingApi = ITApiFactory.getApi(ValueMappingApi.class, null)
    if (valueMappingApi == null) return message

    // 1. Get Country Code (first 2 chars of COMP_CODE)
    def compCode = root.DOCUMENTHEADER.COMP_CODE.text()
    // def countryCode = compCode?.length() >= 2 ? compCode.substring(0, 2) : ""
    
    // 2. Find all unique Tax Codes in the document
    def taxCodes = root.ACCOUNTTAX.item.TAX_CODE.collect { it.text() }.unique()
    
    // Map to store results: [TaxCode : LogicType]
    def taxLogicMap = [:]

    // 3. Check Value Mapping for each Tax Code
    taxCodes.each { taxCode ->
        // Construct Source Value: Country_TaxCode (e.g., "TR_X2")
        def sourceValue = "${compCode}_${taxCode}"
        
        // Perform Lookup
        // Source Agency: "Country_TaxCode" (from your description)
        // Target Agency: "TaxLogicType" (from your description)
        // Value Mapping Name: "VM_TaxCode_To_SpecialTaxLogicType"
        String logicType = valueMappingApi.getMappedValue(
            "GSAP_SpecialTaxCode", "SpecialTaxCode", sourceValue, 
            "GSAP_SpecialTaxLogicType", "SpecialTaxLogicType"
        )
        
        if (logicType != null && !logicType.isEmpty()) {
            taxLogicMap[taxCode] = logicType
        }
    }

    // 4. Store the map in an Exchange Property for the XSLT to use
    // We will convert the map to a simple string format, e.g., "|X2=ReverseCharge_PartiallyDeductible|A1=SomeOtherLogic|"
    // This makes it easy to parse in XSLT.
    def logicString = ""
    taxLogicMap.each { k, v -> logicString += "|${k}=${v}|" }
    
    message.setProperty("taxLogicMap", logicString)
    
    return message
}