import com.sap.it.api.mapping.*

def void getItemAmount(String[] poConnectionLines_lineNumber,
                       String[] poConnectionLines_connectedAmount,
                       String[] deviation_deviationAmount,
                       String[] deviation_poConnectionLineNumbers,
                       String[] deviation_codingLineNumbers,
                       String[] codingLine_dimension1,
                       String[] codingLine_codingLineNumber,
                       String[] codingLine_codingLineAmount,
                       String[] deviation_deviationType,
                       String[] poConnectionLines_deliveredUnitPrice,
                       String[] poConnectionLines_deliveredQuantity,
                       Output output,
                       MappingContext context) {

    // Read deviationMap property from previous Groovy
    def deviationMap = context.getProperty("deviationMap") ?: [:]

    // keep track of processed deviation_codingLineNumbers
    def processed = [:]  // key = codingLineNumber, value = number of times already processed

    for (int i = 0; i < poConnectionLines_lineNumber.length; i++) {
        String finalOutputAmount = poConnectionLines_connectedAmount[i]

        for (int j = 0; j < deviation_poConnectionLineNumbers.length; j++) {

            if (poConnectionLines_lineNumber[i].equals(deviation_poConnectionLineNumbers[j])) {
                for (int k = 0; k < codingLine_codingLineNumber.length; k++) {

                    if (codingLine_codingLineNumber[k].equals(deviation_codingLineNumbers[j])) {
                        if (codingLine_dimension1[k].equals("PO Coding")) {

                            if (deviation_deviationType[j].equals("UnitPriceDeviation")) {
                                double amount1 = poConnectionLines_deliveredUnitPrice[i]?.toDouble() ?: 0.0
                                double amount2 = deviation_deviationAmount[j]?.toDouble() ?: 0.0
                                double amount3 = poConnectionLines_deliveredQuantity[i]?.toDouble() ?: 0.0
                                double outputPrice = (amount1 + amount2)
                                finalOutputAmount = (outputPrice * amount3).toString()

                            } else if (deviation_deviationType[j].equals("InvoiceLineAmountDeviation")) {

                                // get how many times this coding line occurs in the deviationMap
                                int totalOccurrences = deviationMap[deviation_codingLineNumbers[j]] ?: 1

                                // get how many times we've already processed this coding line
                                int alreadyProcessed = processed[deviation_codingLineNumbers[j]] ?: 0

                                 def amount1 = new BigDecimal(poConnectionLines_connectedAmount[i] ?: "0")
                                def amount2 = new BigDecimal(codingLine_codingLineAmount[k] ?: "0")

                                def baseSplit = (amount2.divide(new BigDecimal(totalOccurrences), 2, BigDecimal.ROUND_HALF_UP))
                                def remainder = amount2.subtract(baseSplit.multiply(new BigDecimal(totalOccurrences)))

                                def splitAmount
                                if (alreadyProcessed == 0) {
                                    splitAmount = baseSplit.add(remainder)
                                } else {
                                     splitAmount = baseSplit
                                    }

                                finalOutputAmount = amount1.add(splitAmount).toString()
                                
                                // increment processed count
                                processed[deviation_codingLineNumbers[j]] = alreadyProcessed + 1
                            }
                            break
                        }
                    }
                }
                break
            }
        }

        output.addValue(finalOutputAmount)
    }
}
