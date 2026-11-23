import com.sap.it.api.mapping.*;

def void sumTaxes(String[] amounts, Output output, MappingContext context) {
    Double total = 0.0;
    
    for (int i = 0; i < amounts.length; i++) {
        // Basic check to ensure the value is a number
        if (amounts[i] != null && amounts[i].trim() != "" && amounts[i] != "Result.SUPPRESS") {
            total += Double.parseDouble(amounts[i]);
        }
    }
    
    // Add the final result to the output queue
    output.addValue(String.format("%.2f", total));
}