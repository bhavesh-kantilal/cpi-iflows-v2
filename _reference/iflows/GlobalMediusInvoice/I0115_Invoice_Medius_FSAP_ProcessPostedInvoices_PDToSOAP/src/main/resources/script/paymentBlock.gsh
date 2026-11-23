import com.sap.gateway.ip.core.customdev.util.Message


def Message processData(Message message) {

    // Initialize PaymentBlock
    String paymentBlock = ""
    
    //Get Properties
    String supplierCustomField_Text1 = message.getProperty("supplierCustomField_Text1")
    String customField_List1 = message.getProperty("customField_List1")
    String isPaymentBlocked = message.getProperty("isPaymentBlocked")
    

    // Check if supplierCustomField_Text1 is not null or empty
    if (supplierCustomField_Text1?.trim()) {
        if (supplierCustomField_Text1 in ["A", "B"]) {
            paymentBlock = supplierCustomField_Text1
        } else {
            paymentBlock = ""
        }
    }

    // Check if customField_List1 is not null or empty
    if (customField_List1?.trim()) {
        if (customField_List1 in ["A", "B"]) {
            if (isPaymentBlocked?.equalsIgnoreCase("true")) {
                paymentBlock = customField_List1
            } else {
                paymentBlock = "E"
            }
        } else if (isPaymentBlocked?.equalsIgnoreCase("true")) { 
            paymentBlock = "E"
        }
    }
    
    //Check with paymentBlock
     if (isPaymentBlocked?.equalsIgnoreCase("true")) {
        if (customField_List1?.trim()) {
            if (customField_List1 in ["A", "B"]) {
                 paymentBlock = customField_List1
            
            }else{
                paymentBlock = "E"
            }
                
        }
        else{
             paymentBlock = "E"
        }
     }

    // Check if paymentBlock is blank and set context property accordingly
    if (paymentBlock == "E") {
        message.setProperty("PaymentBlock", "Error")
    } else {
        message.setProperty("PaymentBlock", paymentBlock)
    }
    
   return message
}
