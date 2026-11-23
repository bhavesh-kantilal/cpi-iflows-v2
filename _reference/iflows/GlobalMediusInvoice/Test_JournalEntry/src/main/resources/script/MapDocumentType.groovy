import com.sap.it.api.mapping.*;

def String MapDocumentType(String totalAmount, MappingContext context) {
    // Return KR if null/empty; otherwise, check if negative
    if (totalAmount?.isNumber()) {
        return totalAmount.toDouble() < 0 ? "KG" : "KR"
    }
    
    return "KR"
}