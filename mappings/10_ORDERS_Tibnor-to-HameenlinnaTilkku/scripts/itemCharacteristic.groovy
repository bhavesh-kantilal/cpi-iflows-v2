import com.sap.it.api.mapping.*

/*
 * itemCharacteristic(itemPosex[], cfgPosex[], charc[], value[], valueTxt[], name[]) -> value, valueTxt
 *
 * ORDERS02: the characteristics of an item (E1CUCFG / E1CUVAL) are NOT under its E1EDP01. They sit beside the
 * items at IDOC level and point to their item through E1CUCFG-POSEX = E1EDP01-POSEX. An item can have several
 * E1CUCFG segments (1 to 3 in the samples), so the n-th E1CUCFG is not the n-th item.
 * This UDF does that join: for every E1EDP01 it looks up the characteristic 'name' in that item's configurations.
 *
 * INPUTS (all values of the context; the mapping puts each input in ONE context)
 *   itemPosex  E1EDP01-POSEX, one value per item, in item order                (context IDOC)
 *   cfgPosex   E1CUCFG-POSEX repeated for each of its E1CUVAL                  (one value per E1CUVAL)
 *   charc      E1CUVAL-CHARC                                                    (one value per E1CUVAL)
 *   value      E1CUVAL-VALUE      (mapWithDefault '' in its own context)        (one value per E1CUVAL)
 *   valueTxt   E1CUVAL-VALUE_TXT  (mapWithDefault '' in its own context)        (one value per E1CUVAL)
 *   name       the characteristic name (constant), e.g. 'FORM'
 *
 * OUTPUTS: one value per item, in item order (empty string when the item does not have the characteristic)
 *   0 value      E1CUVAL-VALUE of the first matching E1CUVAL
 *   1 valueTxt   E1CUVAL-VALUE_TXT of the same E1CUVAL
 *   The mapping splits them per item (SplitByValue Each Value) and creates the target only for non-empty values.
 *
 * POSEX values are compared without leading zeros ('00010' = '10'), CHARC without surrounding spaces.
 * VALUE / VALUE_TXT are returned as sent (not trimmed): today's output keeps e.g. the leading space of
 * KVALITET ' S355G10+M MDS-Y20' (PO 46540713 item 20).
 */
def void itemCharacteristic(String[] itemPosex, String[] cfgPosex, String[] charc, String[] value,
                            String[] valueTxt, String[] name, Output outValue, Output outValueTxt,
                            MappingContext context) {
    int n = charc.length
    if (cfgPosex.length != n || value.length != n || valueTxt.length != n) {
        throw new RuntimeException("itemCharacteristic: expected one value per E1CUVAL (" + n + "), got POSEX "
                + cfgPosex.length + ", VALUE " + value.length + ", VALUE_TXT " + valueTxt.length)
    }
    String wanted = (name.length > 0 && name[0] != null) ? name[0].trim() : ""

    for (int i = 0; i < itemPosex.length; i++) {
        String item = cfgNoZeros(itemPosex[i])
        String v = ""
        String t = ""
        for (int j = 0; j < n; j++) {
            if (wanted.equals(cfgTrim(charc[j])) && item.equals(cfgNoZeros(cfgPosex[j]))) {
                v = (value[j] == null) ? "" : value[j]          // as sent, e.g. ' S355G10+M MDS-Y20'
                t = (valueTxt[j] == null) ? "" : valueTxt[j]
                break
            }
        }
        outValue.addValue(v)
        outValueTxt.addValue(t)
    }
}

/* null-safe trim */
def String cfgTrim(String s) {
    return (s == null) ? "" : s.trim()
}

/* '00010' -> '10'; '0' and '' stay as they are */
def String cfgNoZeros(String s) {
    String t = cfgTrim(s)
    String r = t.replaceFirst("^0+", "")
    return (r.isEmpty() && !t.isEmpty()) ? "0" : r
}
