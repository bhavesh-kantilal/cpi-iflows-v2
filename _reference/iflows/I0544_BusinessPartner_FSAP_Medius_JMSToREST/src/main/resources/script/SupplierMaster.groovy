import com.sap.it.api.mapping.*;

def String paymentTerm(String co, String term, MappingContext ctx) { return "company[" + co + "_S4H];" + term }
def String companyId(String co, MappingContext ctx) { return "company[" + co + "_S4H]" }
def String externalSystemId(String co, String supp, MappingContext ctx) { return "company[" + co + "];" + supp }
def String externalSystemIdPayment(String co, String supp, String bankId, MappingContext ctx) { return "company[" + co + "_S4H];" + supp + ";" + bankId }

def void paymentIdentifierType(String[] bankAccountText,String[]  ibanText,Output identifierValue,Output identifierType, MappingContext context) {
    
        for(int i=0;i<bankAccountText.length;i++){
            
            if(!bankAccountText[i].equals("")){
             identifierValue.addValue(bankAccountText[i]);
             identifierType.addValue("BANK_ACCOUNT")
            }
             if(!ibanText[i].equals("")){
             identifierValue.addValue(ibanText[i]);
             identifierType.addValue("IBAN_NUMBER")
            }
            identifierType.addContextChange()
        }
        
         
        
}

def void identifierCombined(String[] bankid, String[] iban, String[] taxid, Output identifierValue, Output identifierType, MappingContext context) {
    
    bankid.each { val ->
        if (val && !val.trim().isEmpty()) {
            identifierValue.addValue(val.trim())
            identifierType.addValue("BANK_ACCOUNT")
        }
    }
    iban.each { val ->
        if (val && !val.trim().isEmpty()) {
            identifierValue.addValue(val.trim())
            identifierType.addValue("IBAN_NUMBER")
        }
    }
    taxid.each { val ->
        if (val && !val.trim().isEmpty()) {
            identifierValue.addValue(val.trim())
            identifierType.addValue("VAT_REGISTRATION_NUMBER")
        }
    }
}

/**
 * PAYMENT DETAILS
 */
def void paymentValueSimple(String[] bankId, String[] iban, Output output, MappingContext ctx) {
    
    for (int i=0; i<bankId.length; i++) {
        if (bankId[i] != null && !bankId[i].trim().isEmpty() )
            output.addValue(bankId[i].trim())
        if (iban[i] != null && !iban[i].trim().isEmpty() )
            output.addValue(iban[i].trim())            
            
    }
}