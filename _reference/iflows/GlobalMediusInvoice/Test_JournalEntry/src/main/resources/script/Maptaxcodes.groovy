import com.sap.it.api.mapping.*;

def String mapTaxIndicator(String taxindicator1) {
    // Handle null or empty inputs to prevent errors
    if (taxindicator1 == null) {
        return "VST";
    }

    switch (taxindicator1.trim()) {
        case "WD":
            return "MWS";
        case "AW":
            return "NAV";
        default:
            return "VST";
    }
}