import com.sap.it.api.mapping.*;

/* Helper UDFs for Map_TibnorS4_HammelinnaMetocsHub_PurchaseOrder_ORDERS02.
   Signatures follow the reference UDFs (e.g. splitString.groovy, concatText.groovy). */

// Single value: first maxLength characters of input (spec row 46: first 35 characters of KTEXT).
def String cropText(String input, String maxLength){
    if (input == null) {
        return input
    }
    int max = Integer.parseInt(maxLength.trim())
    return (input.length() > max) ? input.substring(0, max) : input
}

// All values of a context: one "true"/"false" per context, true if any E1EDPT1-TDID of the item is 'BEST' (spec row 46).
def void hasBestText(String[] tdid, Output output, MappingContext context){
    boolean found = false
    for (int i = 0; i < tdid.length; i++) {
        if ("BEST".equals(tdid[i])) {
            found = true
            break
        }
    }
    output.addValue(found ? "true" : "false")
}

// All values of a context: number of values (spec row 52: count of E1EDP01).
def void countValues(String[] values, Output output, MappingContext context){
    output.addValue(String.valueOf(values.length))
}
