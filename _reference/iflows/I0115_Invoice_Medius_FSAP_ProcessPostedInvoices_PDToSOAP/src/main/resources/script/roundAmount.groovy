import com.sap.it.api.mapping.*
import java.math.RoundingMode

def String roundAmount(String value, String scale) {
    if (!value?.trim()) return value          // keep empty/null as-is
    try {
        int s = scale?.trim() ? scale.trim().toInteger() : 2
        return new BigDecimal(value.trim())
                   .setScale(s, RoundingMode.HALF_UP)
                   .toPlainString()
    } catch (NumberFormatException e) {
        return value                          // don't break the mapping on odd input
    }
}