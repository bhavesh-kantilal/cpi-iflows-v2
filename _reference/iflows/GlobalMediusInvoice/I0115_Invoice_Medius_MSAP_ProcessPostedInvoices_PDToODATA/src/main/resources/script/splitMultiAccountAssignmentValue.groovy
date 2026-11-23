import com.sap.it.api.mapping.Output;
import com.sap.it.api.mapping.MappingContext;
import java.util.regex.Pattern;

def void splitMultiAccountAssignmentValue(String[] distributionValue, String[] index, Output output, MappingContext context) {
    // 1. Safe guard check for both dynamic inputs
    if (distributionValue != null && distributionValue.length > 0 && distributionValue[0] != null && !distributionValue[0].isEmpty() &&
        index != null && index.length > 0 && index[0] != null && !index[0].isEmpty()) {
        
        // 2. Safely parse the dynamic index string into an integer
        int indexValue = index[0].trim().toInteger();
        
        // Split the master string at index 0 by the literal pipe character '|'
        String[] segments = distributionValue[0].split(Pattern.quote("|"));
        
        // Process each segment (e.g., "10_1_40.0" and "10_2_60.0")
        for (String segment : segments) {
            if (segment.contains("_")) {
                // Split the individual segment by the underscore character
                String[] parts = segment.split("_");
                
                // 3. Dynamic bound check: Ensure the array is large enough to contain the requested index
                if (parts.length > indexValue) {
                    output.addValue(parts[indexValue].trim());
                } else {
                    // Fallback if the requested index does not exist in this segment
                    output.addValue("");
                }
            }
        }
    } else {
        // Handle empty input context gracefully
        output.addValue("0");
    }
}