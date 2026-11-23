import com.sap.it.api.mapping.Output;
import com.sap.it.api.mapping.MappingContext;
import java.util.regex.Pattern;

def void splitMultiAccountAssignment(String[] distributionValue, Output output, MappingContext context) {
    // Ensure the input array is not null, has elements, and the first element is not null/empty
    if (distributionValue != null && distributionValue.length > 0 && distributionValue[0] != null && !distributionValue[0].isEmpty()) {
        
        // Split the string at index 0 using the literal pipe character '|'
        // Pattern.quote is used because '|' is a special regex character
        String[] splitValues = distributionValue[0].split(Pattern.quote("|"));
        
        // Output each separated value individually to generate target context queues
        for (String val : splitValues) {
            output.addValue(val.trim());
        }
    } else {
        // Optional: Handle empty input context gracefully if needed
        output.addSuppress();
    }
}