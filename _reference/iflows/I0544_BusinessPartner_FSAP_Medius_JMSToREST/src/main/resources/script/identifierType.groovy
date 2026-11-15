import com.sap.it.api.mapping.*;

// Function to generate Bank identifiers (BankAccountID and BankAccountStandardID)
def void identifierType(String[] bankAccountID, String[] bankAccountStandardID, Output identifierValue, Output identifierType, MappingContext context) {
    
    // 1. BankAccountID
    for(int i = 0; i < bankAccountID.length; i++) {
        if(bankAccountID[i] != null && !bankAccountID[i].trim().isEmpty()) {
            identifierValue.addValue(bankAccountID[i]);
            identifierType.addValue("BANK_ACCOUNT");
        }
    }

    // 2. BankAccountStandardID
    for(int i = 0; i < bankAccountStandardID.length; i++) {
        if(bankAccountStandardID[i] != null && !bankAccountStandardID[i].trim().isEmpty()) {
            identifierValue.addValue(bankAccountStandardID[i]);
            identifierType.addValue("IBAN_NUMBER");
        }
    }
}

// Function to create the nodes 
def void identifiers(String[] nodes, Output output, MappingContext context) {
    // Create exactly 2 nodes according to the intial scope
    output.addValue(" ");
    output.addValue(" ");
}
