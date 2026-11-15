import com.sap.it.api.mapping.*;

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

def String paymentTerm(String companyCode,String paymentTerm,MappingContext context) {
    String pterms 
         pterm = 'company[' + companyCode + ']' + ';' + paymentTerm 
         return pterm;
}

def String externalSystemId(String companyCode,String supplier,MappingContext context) {
    String supp 
         supp = 'company[' + companyCode + ']' + ';' + supplier 
         return supp;
}

def String companyId(String companyCode,MappingContext context) {
    String comp 
         comp = 'company[' + companyCode + ']'
         return comp;
}




def String externalSystemIdPayment(String companyCode,String supplier, String currencyCode, MappingContext context) {
    String value
         value = 'company[' + companyCode + ']' + ';' + supplier + ';' + currencyCode
         return value;
}

def void identifiers(String[] nodes, Output output, MappingContext context) {
    
        String value = ' ';
        output.addValue(value);
        
        String value1 = ' ';
        output.addValue(value1);
        
        String value2 = ' ';
        output.addValue(value2);
        
        String value3 = ' ';
        output.addValue(value3);
      
}

def void identifierType(String[] bankAccountText,String[] vatRegistrationText,String[]  ibanText,Output identifierValue,Output identifierType, MappingContext context) {
    
        for(int i=0;i<bankAccountText.length;i++){
            if(!bankAccountText[i].equals("")){
             identifierValue.addValue(bankAccountText[i]);
             identifierType.addValue("BANK_ACCOUNT")
            }
        }
            
        if(!vatRegistrationText[0].equals("")){
             identifierValue.addValue(vatRegistrationText[0]);
             identifierType.addValue("VAT_REGISTRATION_NUMBER")
        }
          for(int i=0;i<ibanText.length;i++){
            if(!ibanText[i].equals("")){
             identifierValue.addValue(ibanText[i]);
             identifierType.addValue("IBAN_NUMBER")
            }
        }
        
}

def void identifierValue(String[] bankAccount,String[] orgnizationNumber,String[] vatRegistration,String[]  iban, Output output, MappingContext context) {
    
        String value = bankAccount[0];
        output.addValue(value);
        
        String value1 = orgnizationNumber[0];
        output.addValue(value1);
        
        String value2 = vatRegistration[0];
        output.addValue(value2);
        
        String value3 = iban[0];
        output.addValue(value3);
        
        
}