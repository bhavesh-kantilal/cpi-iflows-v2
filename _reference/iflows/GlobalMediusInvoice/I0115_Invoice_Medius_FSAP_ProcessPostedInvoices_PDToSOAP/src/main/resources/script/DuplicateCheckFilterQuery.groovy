def processData(message) {
    def props = message.getProperties()
    
    def companyCode    = props.get("CompanyCode")
    def fiscalYear     = props.get("FiscalYear")
    def docRefId       = props.get("DocumentReferenceID")
    def reference2     = props.get("Reference2")
    def creditor       = props.get("Creditor")

    def filter = "SourceLedger eq '0L'" +
                 " and Ledger eq '0L'" +
                 " and CompanyCode eq '${companyCode}'" +
                 " and FiscalYear eq '${fiscalYear}'" +
                 " and DocumentReferenceID eq '${docRefId}'" +
                 " and Supplier eq '${creditor}'"

    // Only add Reference2 condition if it is not blank
    if (reference2 != null && !reference2.trim().isEmpty()) {
        filter += " and Reference2InDocumentHeader eq '${reference2}'"
    }

    message.setProperty("FilterQuery", filter)
    return message
}