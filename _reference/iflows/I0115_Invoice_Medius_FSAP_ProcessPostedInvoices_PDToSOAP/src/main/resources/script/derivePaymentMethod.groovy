import com.sap.it.api.mapping.*

def void derivePaymentMethod(String[] names, String[] vals, Output output, MappingContext context) {
    boolean setY = false
    for (int i = 0; i < names.length; i++) {
        String n = names[i]
        String v = (i < vals.length) ? vals[i] : ""
        if (n != null && v != null) {
            if (n.trim().equals("FSAP_Supplier_PaymentMethod") && v.toUpperCase().indexOf("Y") >= 0) {
                setY = true
            }
            if (n.trim().equals("FSAP_Supplier_AlternativePayee") && v.trim().length() > 0) {
                setY = true
            }
        }
    }
    if (setY) {
        output.addValue("Y")
    } else {
        output.addSuppress()
    }
}