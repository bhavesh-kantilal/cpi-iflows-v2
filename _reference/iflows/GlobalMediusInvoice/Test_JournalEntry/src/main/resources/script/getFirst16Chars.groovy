import com.sap.it.api.mapping.*

def String getFirst16Chars(String input) {
    if (input == null) {
        return ""
    }

    return input.length() > 16 ? input.substring(0, 16) : input
}