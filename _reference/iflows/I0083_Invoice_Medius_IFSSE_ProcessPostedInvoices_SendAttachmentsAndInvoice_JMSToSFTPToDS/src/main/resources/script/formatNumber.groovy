import com.sap.it.api.mapping.*;

def String formatNumber( String input) {
    try {
        BigDecimal number = new BigDecimal(input)
        //return number.setScale(4, BigDecimal.ROUND_HALF_UP).stripTrailingZeros().toPlainString()
        return number.setScale(4, BigDecimal.ROUND_HALF_UP).toString()
        // return number.stripTrailingZeros().toPlainString() + (number.scale() == 0 ? ".0" : "")
    } catch (Exception e) {
        return "Invalid number"
    }
}