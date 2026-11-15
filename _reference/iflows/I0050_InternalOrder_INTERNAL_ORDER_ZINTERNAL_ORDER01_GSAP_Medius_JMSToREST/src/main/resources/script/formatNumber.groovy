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

def String formatNumber(String input) {
    if (input == null || input.trim().isEmpty()) {
        return input
    }

    // Check if the string is numeric (only digits)
    if (input.isNumber() || input ==~ /^\d+$/) {
        // Remove leading zeros, but ensure '0' stays '0'
        return input.replaceFirst("^0+(?!\$)", "")
    } else {
        // It's alphanumeric or contains non-digit characters
        return input
    }
}