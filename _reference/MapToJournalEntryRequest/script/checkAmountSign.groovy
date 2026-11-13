import com.sap.it.api.mapping.*

def String checkAmountSign(String totalamount, MappingContext context) {
    String cleanInput = totalamount?.trim()

    // 2. Check if the string is a valid number (handles decimals and signs)
    if (cleanInput && cleanInput.isNumber()) {
        BigDecimal amount = cleanInput.toBigDecimal()
        
        // 3. Return H for positive/zero, S for negative
        return amount.signum() >= 0 ? "H" : "S"
    }

    // 4. Return default if input is not numeric or null
    return "" 
}