import com.sap.it.api.mapping.*;
import java.time.LocalDate
import java.time.temporal.ChronoUnit
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

def String getDateDiff(String invoiceDateStr, String dueDateStr){
	// Convert Strings to LocalDate
LocalDate invoiceDate = LocalDate.parse(invoiceDateStr)
LocalDate dueDate = LocalDate.parse(dueDateStr)

// Calculate difference in days
long daysBetween = ChronoUnit.DAYS.between(invoiceDate, dueDate)
	return daysBetween 
}

def void getTaxReporting(String[] input, String[] invoiceNumber, String[] metadata_Name, String[] metadata_Value,String[] vatDate, Output output) {
    // Handle case where input[0] is null, empty, or less than 2 characters
	String result=""
	if (!input[0] || input[0].length() < 2) {
        result = (invoiceNumber[0]?.length() > 16) ? " ".padRight(23) + invoiceNumber[0] : input[0]
        
    }else{

    // Remove logic to take 1st 2 characters, use static prefix
    def prefix = "  "
    result = prefix + " " + input[0]  // Concatenate and return

    if (invoiceNumber[0]?.length() > 16) {
        result = result.take(23).padRight(23) + invoiceNumber[0]  // Ensure 23 positions before appending
    }
	}

    // Iterate over metadata arrays
    for (int i = 0; i < metadata_Name.length; i++) {
        if (metadata_Name[i] == "GSAP_POPULATE_INVOICE_ACC") {
            result = result.padRight(58) + metadata_Value[i]
            break;
        }
    }
    
    if(vatDate[0].equals("")){
	    
	}else{
	    
	    result = result.padRight(59, ' ') + vatDate[0]
	}
    
    output.addValue(result)
}


