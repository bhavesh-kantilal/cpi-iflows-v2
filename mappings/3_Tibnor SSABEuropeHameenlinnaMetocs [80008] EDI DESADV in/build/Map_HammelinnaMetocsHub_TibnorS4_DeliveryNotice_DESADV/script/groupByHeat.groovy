import com.sap.it.api.mapping.*

/*
 * DESADV: one delivery item (E1EDL24) per DeliveryBatchLine + heat number.
 *
 * All inputs hold one value per SinglePart (bundle), in document order, in ONE context
 * (the mapping flattens them with removeContexts):
 *   line    DeliveryBatchLineId of the bundle's line
 *   article CustomersArticleId of the bundle's line
 *   heat    MaterialBatchId of the MaterialBatch with type 'Heat'
 *   weight  DespatchedQuantity 'Weight' value
 *   pieces  DespatchedQuantity 'Pieces' value
 *   meters  DespatchedQuantity 'Meters' value
 *   unit    DespatchedQuantity 'Meters' unit
 *
 * Groups: by line, then by heat, in order of first appearance.
 * Outputs: one value per group, in group order.
 *   0 posnr, 1 matnr, 2 sernr (heat), 3 lfimg, 4 usr01 (bundle count), 5 usr03, 6 vrkme
 * Number format (spec rows 16, 20): one bundle -> value as sent ('108.0'),
 * several bundles -> sum without trailing decimals ('216').
 */
def void groupByHeat(String[] line, String[] article, String[] heat, String[] weight, String[] pieces,
                     String[] meters, String[] unit,
                     Output posnr, Output matnr, Output sernr, Output lfimg, Output usr01, Output usr03,
                     Output vrkme, MappingContext context) {
    int n = line.length
    [article, heat, weight, pieces, meters, unit].each { String[] a ->
        if (a.length != n) {
            throw new RuntimeException("groupByHeat: expected one value per SinglePart (" + n + "), got " + a.length
                    + ". Check that every bundle has one Heat batch and one Weight/Pieces/Meters quantity.")
        }
    }

    Map<String, Map> groups = new LinkedHashMap<String, Map>()
    for (int i = 0; i < n; i++) {
        String key = line[i] + "\u0000" + heat[i]
        Map g = groups.get(key)
        if (g == null) {
            g = [line: line[i], article: article[i], heat: heat[i], unit: unit[i],
                 weight: [], pieces: [], meters: []]
            groups.put(key, g)
        }
        g.weight << weight[i]
        g.pieces << pieces[i]
        g.meters << meters[i]
    }

    groups.values().each { Map g ->
        String m = total(g.meters)
        posnr.addValue(g.line)
        matnr.addValue(g.article)
        sernr.addValue(g.heat)
        lfimg.addValue(m)
        usr01.addValue(String.valueOf(g.meters.size()))
        usr03.addValue(total(g.weight) + ";KGM;" + total(g.pieces) + ";PCE;" + m + ";MTR;")
        vrkme.addValue(g.unit)
    }
}

/* One value: as sent. Several: sum, trailing zero decimals removed ('9590.000' + ... -> '9590'). */
private String total(List values) {
    if (values.size() == 1) {
        return values[0]
    }
    BigDecimal sum = BigDecimal.ZERO
    values.each { sum = sum.add(new BigDecimal(it.toString().trim())) }
    return sum.stripTrailingZeros().toPlainString()
}
