import com.sap.it.api.mapping.*

/*
 * substringSafe(value, from, to)
 *
 * Substring that never fails on a short value. Positions are 0-based; 'to' is exclusive (as Java substring).
 *
 * WHEN TO USE
 *   Prefer the standard CPI function 'substring' (params start, count). It works when the value is always long
 *   enough. Use this UDF only when the value may be shorter than 'to' (or than 'from'): the standard function
 *   then throws an error and stops the mapping.
 *
 * RULES
 *   length >= to          -> characters from..to-1
 *   from <= length < to   -> the rest from 'from' to the end
 *   length < from         -> '' (empty)
 *
 * EXAMPLES
 *   substringSafe("20261207-20261220", "9", "17")  -> "20261220"   (end date of a format-718 date range)
 *   substringSafe("ABCDEFGH", "2", "4")             -> "CD"
 *   substringSafe("ABC", "0", "5")                  -> "ABC"        (shorter than 'to': the rest)
 *   substringSafe("ABC", "5", "8")                  -> ""           (shorter than 'from')
 *
 * ORIGIN
 *   User's reference UDF (ORDRSP feedback, 2026-11-15; also used in SAP PO). Same behaviour, readable names.
 *   Library copy: udf_library/substringSafe.groovy. A mapping uses an unchanged copy in its scripts/ folder.
 */
def String substringSafe(String value, String from, String to) {
    int start = Integer.parseInt(from.trim())
    int end = Integer.parseInt(to.trim())
    if (value.length() >= end) {
        return value.substring(start, end)
    } else if (value.length() < start) {
        return ""
    } else {
        return value.substring(start, value.length())
    }
}
