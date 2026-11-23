import com.sap.gateway.ip.core.customdev.util.Message
import org.apache.commons.lang3.exception.ExceptionUtils

def Message processData(Message message) {
    Exception ex = message.getProperty("CamelExceptionCaught") as Exception
    if (ex) {
        // Get root cause message
        def rootMsg = ExceptionUtils.getRootCauseMessage(ex)

        // Remove all double quotes to make it JSON-safe
        rootMsg = rootMsg.replaceAll('"', '')

        // Set it as a property for later JSON construction
       message.setBody(rootMsg)   
    }
    return message
}
