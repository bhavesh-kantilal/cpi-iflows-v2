import com.sap.it.api.mapping.MappingContext

def String getTaxID(String longTaxID, String partyTaxID, MappingContext context) {

    if (longTaxID != null && !longTaxID.trim().isEmpty() && 
        !longTaxID.equalsIgnoreCase("null") && !longTaxID.equals("__NIL__")) {
        return longTaxID.trim();
    }
    
    if (partyTaxID != null && !partyTaxID.trim().isEmpty() && 
        !partyTaxID.equalsIgnoreCase("null") && !partyTaxID.equals("__NIL__")) {
        return partyTaxID.trim();
    }
    
    return ""; 
}