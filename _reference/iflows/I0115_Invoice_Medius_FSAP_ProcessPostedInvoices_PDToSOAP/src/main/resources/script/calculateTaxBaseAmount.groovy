import com.sap.it.api.mapping.*;
import com.sap.it.api.ITApiFactory;
import com.sap.it.api.mapping.ValueMappingApi;

/*Add MappingContext parameter to read or set headers and properties
def String customFunc1(String P1,String P2,MappingContext context) {
         String value1 = context.getHeader(P1);
         String value2 = context.getProperty(P2);
         return value1+value2;
}

Add Output parameter to assign the output value.
def void custFunc2(String[] is,String[] ps, Output output, MappingContext context) {
        String value1 = context.getHeader(is[0]);
        String value2 = context.getProperty(ps[0]);
        output.addValue(value1);
        output.addValue(value2);
}*/

def String calculateTaxBaseAmount(String percentageStr,String taxAmountStr ){
	// Convert both strings to BigDecimal for precision
    def percentage = new BigDecimal(percentageStr)
    def knownAmount = new BigDecimal(taxAmountStr)
    // Calculate the total amount (X = knownAmount / percentage)
    def totalAmount = knownAmount.divide(percentage, 4, BigDecimal.ROUND_HALF_UP)
    return totalAmount.toString()
}





def void checkAndCalcTaxBaseAmount(String[] companyCode, String[] taxCode,
                                   String[] taxAmount, String[] netAmount, Output output) {
    for (int i = 0; i < taxCode.length; i++) {
        String PartiallyDeductible = ""
        String CompletelyDeductible = ""

        try {
            def service = ITApiFactory.getApi(ValueMappingApi.class, null)
            String VM_Key = companyCode[0] + "_" + taxCode[i]

            if (service != null) {
                PartiallyDeductible = service.getMappedValue("GSAP_TaxCode", "TaxCode",
                                                             VM_Key, "GSAP_AccountKeyConditionKey", "AccountKeyConditionKey")
                if (PartiallyDeductible == null || PartiallyDeductible.isEmpty()) {
                    PartiallyDeductible = ""
                }

                CompletelyDeductible = service.getMappedValue("GSAP_TaxCode", "TaxCode",
                                                              VM_Key, "GSAP_TaxPercentage", "TaxPecentage")
                if (CompletelyDeductible == null || CompletelyDeductible.isEmpty()) {
                    CompletelyDeductible = ""
                }
            }
        } catch (Exception e) {
            // Optional: add logging for error visibility
        }

        if (PartiallyDeductible.equals("") && CompletelyDeductible.equals("")) {
            //output.addValue(netAmount[i])
			output.addValue((i >= 0 && i < netAmount.length) ? netAmount[i] : "")
        } else {
            if (!PartiallyDeductible.equals("")) {
                BigDecimal net = new BigDecimal(netAmount[i])
                BigDecimal tax = new BigDecimal(taxAmount[i])
                output.addValue(net.subtract(tax).toString())
            } else {
                BigDecimal percentage = new BigDecimal(CompletelyDeductible)
                BigDecimal knownAmount = new BigDecimal(taxAmount[i])
                BigDecimal totalAmount = knownAmount
                        .divide(percentage, 4, BigDecimal.ROUND_HALF_UP)
                output.addValue(totalAmount.toString())
            }
        }
    }
}
