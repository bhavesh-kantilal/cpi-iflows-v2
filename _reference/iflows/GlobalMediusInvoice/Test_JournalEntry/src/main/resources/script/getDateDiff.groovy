import com.sap.it.api.mapping.*;
import java.time.LocalDate
import java.time.temporal.ChronoUnit

def String getDateDiff(String invoiceDateStr, String dueDateStr){
	// Convert Strings to LocalDate
        LocalDate invoiceDate = LocalDate.parse(invoiceDateStr)
    LocalDate dueDate = LocalDate.parse(dueDateStr)
    // Calculate difference in days
    long daysBetween = ChronoUnit.DAYS.between(invoiceDate, dueDate)
	return daysBetween 
}