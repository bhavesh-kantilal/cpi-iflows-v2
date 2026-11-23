import com.sap.it.api.mapping.*;

def String formatToTenDigits(String input) {
    if (input == null) return "0000000000";
    
    // Converts string to Long and pads with leading zeros up to 10 digits
    return String.format("%010d", Long.parseLong(input.trim()));
}