import com.sap.it.api.mapping.*

def void reverseChargeCalculation(
        String[] TotalAmount,
        String[] ReverseChargeAccountKey,
        String[] Amount,
        String[] NetAmount,
        // String[] SpecialTaxLogicType,
        Output TaxItemClassification,
        Output AmountInTransactionCurrency,
        Output TaxBaseAmountInTransCrcy,
        MappingContext context) {
    
    for (int i = 0; i < ReverseChargeAccountKey.length; i++) {
        String taxClassification = null
        String taxBaseAmount = NetAmount[i]  // Default: use net amount
        
        if (ReverseChargeAccountKey[i]?.trim()) {
            // Parse amounts safely
            double totalAmount = 0.0
            double lineAmount = 0.0
            try {
                totalAmount = Double.parseDouble(TotalAmount[i]?.trim() ?: "0")
                lineAmount = Double.parseDouble(Amount[i]?.trim() ?: "0")
            } catch (NumberFormatException e) {
                totalAmount = 0.0
                lineAmount = 0.0
            }
            
            // Determine tax classification based on document type and line amount
            String[] keyParts = ReverseChargeAccountKey[i].split("_")
            int partIndex = (totalAmount < 0) ? 
                (lineAmount < 0 ? 1 : 0) : 
                (lineAmount < 0 ? 0 : 1)
            
            taxClassification = keyParts.length > partIndex ? keyParts[partIndex] : null
            
            // Apply reverse charge logic: use tax amount as base amount instead of net amount
            // if (SpecialTaxLogicType[i] == 'ReverseCharge_TaxBaseAmount' && 
            //     (taxClassification == 'ESE' || taxClassification == 'VST')) {
            //     taxBaseAmount = Amount[i]  // Override: use gross amount for reverse charge
            // }
        }
        
        // Populate output arrays
        TaxItemClassification.addValue(taxClassification)
        AmountInTransactionCurrency.addValue(Amount[i])
        TaxBaseAmountInTransCrcy.addValue(taxBaseAmount)
    }
}