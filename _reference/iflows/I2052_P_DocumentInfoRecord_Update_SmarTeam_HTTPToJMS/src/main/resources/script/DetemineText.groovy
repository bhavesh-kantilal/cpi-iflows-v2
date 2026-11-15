import com.sap.it.api.mapping.*

/**
 * determineText
 * -------------------------------------------------------------------------
 * Picks the description for one target language (EN, SV ...) from the
 * SmarTeam descriptions. If the source has no text in that language, it uses
 * the first non-empty description it does have, so that every target language
 * in SAP gets filled.
 *
 * Example: only <Description lang="SV">ABC</Description> comes in
 *   -> target EN = "ABC", target SV = "ABC"
 *
 * Use: one call per duplicated target subtree (Description[EN], Description[SV] ...)
 *
 * Inputs (all queues with the same context, e.g. per <Descriptions>):
 *   smartTeamLanguage    - Description/@lang values from the source
 *   smartTeamDescription - Description text values, same order as @lang
 *   inputLanguage        - target language for this subtree (Constant, e.g. "EN")
 *
 * Execution type: "All Values of a Context"
 * -------------------------------------------------------------------------
 */
def void determineText(String[] smartTeamLanguage, String[] smartTeamDescription, String[] inputLanguage,
                       Output output, MappingContext context) {

    // No source descriptions at all: do not create the target node
    if (smartTeamDescription == null || smartTeamDescription.length == 0) {
        output.addSuppress()
        return
    }

    // Target language for this subtree (trimmed; compared case-insensitively)
    String targetLang = (inputLanguage != null && inputLanguage.length > 0 && inputLanguage[0] != null) ?
            inputLanguage[0].trim() : ""

    String outputDescription = ""

    // 1) Look for a description in exactly the requested language
    int count = Math.min(smartTeamLanguage?.length ?: 0, smartTeamDescription.length)
    for (int i = 0; i < count; i++) {
        String lang = smartTeamLanguage[i]?.trim()
        if (lang != null && lang.equalsIgnoreCase(targetLang)) {
            outputDescription = smartTeamDescription[i] ?: ""
            break
        }
    }

    // 2) Fallback: requested language missing or empty -> first non-empty description
    if (outputDescription.trim().isEmpty()) {
        String fallback = smartTeamDescription.find { it != null && !it.trim().isEmpty() }
        outputDescription = fallback ?: ""
    }

    // 3) Write the result; suppress if nothing usable was found
    if (outputDescription.trim().isEmpty()) {
        output.addSuppress()
    } else {
        output.addValue(outputDescription)
    }
}