import com.sap.it.api.mapping.*;

def String formatDate(String input){
    if (input == null || input.length() < 10) return input;
    return input.substring(0, 10);
}