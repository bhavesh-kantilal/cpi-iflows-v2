import com.sap.it.api.mapping.*;

def String extractInvoiceSuffix(String invNumber) {
    
    if (invNumber == null || invNumber.length() <= 16) {
        return ""; 
    }
    
    String suffix = invNumber.substring(16);
    
    return suffix;
}