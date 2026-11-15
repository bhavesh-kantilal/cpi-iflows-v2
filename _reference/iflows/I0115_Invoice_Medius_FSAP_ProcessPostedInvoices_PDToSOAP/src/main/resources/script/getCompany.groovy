import com.sap.it.api.mapping.*;

def String getCompany(String company, Container container) {
    if (company == null) return ""
    return company.length() > 4 ? company.substring(0, 4) : company
}