import com.sap.it.api.mapping.*;

def String getFirstFourChars(String input, Container container) {
    if (input == null || input.isEmpty()) {
        return "";
    }
    
    if (input.length() <= 4) {
        return input;
    }
    return input.substring(0, 4);
}