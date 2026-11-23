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

def String splitString(String inputString, int index,String separator){
    def parts = inputString.split(separator)
    return (index > 0 && index <= parts.size()) ? parts[index - 1] : null
}


def void getConnectedValue(String[] sourceValue, String[] relatedValue, String[] requiredValue, Output output, MappingContext context) {
    for (int i = 0; i < sourceValue.length; i++) {
        for (int j = 0; j < relatedValue.length; j++) {
            if (relatedValue[j].equals(sourceValue[i])) {
                // 1. Safely extract the value if the index exists, otherwise default to an empty string
                def targetValue = (requiredValue?.size() > j) ? requiredValue[j] : ""
                output.addValue(targetValue)
                
               /* // 2. Check if the value is null, empty, or just whitespace
                if (!targetValue?.trim()) {
                    output.addSuppress()
                } else {
                    output.addValue(targetValue)
                }
                */
                
                break
            }
        }
    }
}

//Vikas Singh: add argument for start position
def String cropString(String str, int startPosition, int endPosition, MappingContext context) {
    if (!str) return ""
    
    // Ensure we don't go past the end of the actual string
    int safeEnd = Math.min(endPosition, str.length())
    
    if (startPosition >= safeEnd) return ""
    
    return str.substring(startPosition, safeEnd)
}