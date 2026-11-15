import com.sap.gateway.ip.core.customdev.util.Message
import com.sap.it.api.mapping.ValueMappingApi
import com.sap.it.api.ITApiFactory
import groovy.xml.XmlUtil
import groovy.util.XmlSlurper
import java.math.BigDecimal
import java.math.RoundingMode

/**
 * ================================================================================
 * Groovy Script for Handling Non-Deductible Tax (Rounding on First Item)
 * ================================================================================
 * Purpose:
 * This script transforms a BAPI_ACC_DOCUMENT_POST payload. If a tax code is
 * found in the configured Value Mapping, its total tax amount is proportionally
 * distributed across all corresponding G/L lines, applying any rounding
 * difference to the first G/L line item.
 *
 * Value Mapping Configuration Assumption:
 * - Source Value Example: "EE_RP"
 * - Target Value Example: "NVV_MWVZ"
 * ================================================================================
 */
def Message processData(Message message) {

    // 1. Initialization
    def originalBody = message.getBody(String.class)
    def root = new XmlSlurper().parseText(originalBody)
    
    def valueMappingApi = ITApiFactory.getApi(ValueMappingApi.class, null)
    
    if (valueMappingApi == null) {
        return message 
    }

    boolean transformationNeeded = false
    def companyCode = root.DOCUMENTHEADER.COMP_CODE.text()
    def countryCode = companyCode.length() >= 2 ? companyCode.substring(0, 2) : companyCode
    def currencyAmountMap = root.CURRENCYAMOUNT.item.collectEntries { [(it.ITEMNO_ACC.text()), it] }

    // 2. Main Logic: Iterate through all tax items
    root.ACCOUNTTAX.item.each { taxItem ->
        String currentTaxCode = taxItem.TAX_CODE.text()
        String sourceLookupValue = "${countryCode}_${currentTaxCode}"
        
        String mappedValue = valueMappingApi.getMappedValue("GSAP_NonDeductibleTaxCode", "NonDeductibleTaxCode", sourceLookupValue, "GSAP_NonDeductibleAcctKeyCondKey", "NonDeductibleAcctKeyCondKey")

        if (mappedValue) {
            transformationNeeded = true
            def mappedParts = mappedValue.split('_')
            def newAcctKey = mappedParts.size() > 0 ? mappedParts[0] : null
            def newCondKey = mappedParts.size() > 1 ? mappedParts[1] : null

            // Rule 1: Modify the ACCOUNTTAX item
            if (newAcctKey) taxItem.ACCT_KEY.replaceBody(newAcctKey)
            if (newCondKey) {
                if (taxItem.COND_KEY.isEmpty()) {
                    taxItem.appendNode { COND_KEY(newCondKey) }
                } else {
                    taxItem.COND_KEY.replaceBody(newCondKey)
                }
            }

            def taxItemNo = taxItem.ITEMNO_ACC.text()
            def currencyTaxItem = currencyAmountMap[taxItemNo]
            
            if (!currencyTaxItem || currencyTaxItem.AMT_BASE.text().isEmpty() || new BigDecimal(currencyTaxItem.AMT_BASE.text()) == BigDecimal.ZERO) {
                return 
            }

            def totalTaxAmount = new BigDecimal(currencyTaxItem.AMT_DOCCUR.text())
            def totalBaseAmount = new BigDecimal(currencyTaxItem.AMT_BASE.text())
            
            def matchingGlItems = root.ACCOUNTGL.item.findAll { it.TAX_CODE.text() == currentTaxCode }

            // --- HIGHLIGHT: Start of First Item Rounding Correction Logic ---
            if (matchingGlItems.size() > 0) {
                // First, calculate all the rounded tax portions
                def taxPortions = matchingGlItems.collect { glItem ->
                    def glAmount = new BigDecimal(currencyAmountMap[glItem.ITEMNO_ACC.text()].AMT_DOCCUR.text())
                    return (glAmount / totalBaseAmount * totalTaxAmount).setScale(2, RoundingMode.HALF_UP)
                }
                
                // Then, find the difference caused by rounding
                def sumOfRoundedPortions = taxPortions.sum()
                def roundingDifference = totalTaxAmount - sumOfRoundedPortions
                
                // Add the rounding difference to the first item's portion
                taxPortions[0] += roundingDifference
                
                // Now, loop through the items and apply the final, corrected tax portions
                matchingGlItems.eachWithIndex { glItem, index ->
                    def taxPortion = taxPortions[index]
                    def glItemNo = glItem.ITEMNO_ACC.text()
                    def currencyGlItem = currencyAmountMap[glItemNo]
                    def glAmount = new BigDecimal(currencyGlItem.AMT_DOCCUR.text())
                    def newGlAmount = glAmount + taxPortion

                    // Update the CURRENCYAMOUNT item for this G/L line
                    currencyGlItem.AMT_DOCCUR.replaceBody(newGlAmount.toPlainString())

                    if (currencyGlItem.TAX_AMT.isEmpty()) {
                         currencyGlItem.appendNode { TAX_AMT(taxPortion.toPlainString()) }
                    } else {
                        currencyGlItem.TAX_AMT.replaceBody(taxPortion.toPlainString())
                    }
                }
            }
            // --- HIGHLIGHT: End of First Item Rounding Correction Logic ---
        }
    }

    // 3. Finalize
    if (transformationNeeded) {
        message.setBody(XmlUtil.serialize(root))
    } else {
        message.setBody(originalBody)
    }
    
    return message
}

