import com.sap.it.api.mapping.*

def void splitStringOTV(String[] is, Output Name, Output City, Output PostalCode, Output Country, Output BankType, Output SWIFT, MappingContext context) {

    if (is == null || is.length == 0 || is[0].trim().isEmpty()) {
        
    }else{

    // Split the input string on semicolon
    def parts = is[0].split(';')

    // Use safe access in case some fields are missing
    if (parts.size() > 0) Name.addValue(parts[0].trim())
    if (parts.size() > 1) City.addValue(parts[1].trim())
    if (parts.size() > 2) PostalCode.addValue(parts[2].trim())
    if (parts.size() > 3) Country.addValue(parts[3].trim())
    if (parts.size() > 4) BankType.addValue(parts[4].trim())
    if (parts.size() > 5) SWIFT.addValue(parts[5].trim())
    }
}
