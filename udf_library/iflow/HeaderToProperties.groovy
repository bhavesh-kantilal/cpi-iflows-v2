/*
 * HeaderToProperties.groovy  (Child IFlow, SSAB Simplified Pipeline)
 * Place: first step after the Process Direct Sender.
 * Unpacks Header SSAB_Dispatcher_Properties (written by PropertiesToHeader.groovy
 * in the Parent IFlow) back into Exchange Properties, then removes the Header.
 * Does nothing if the Header is missing.
 */
import com.sap.gateway.ip.core.customdev.util.Message
import java.nio.charset.StandardCharsets

def Message processData(Message message) {
    // Header is only there when the Parent IFlow set SSAB_Dispatcher_CopyPropertiesToHeader = Yes
    def encoded = message.getHeaders().get("SSAB_Dispatcher_Properties")
    if (encoded) {
        // Base64 decode and read the key=value text back (standard Java, no JSON parser)
        def props = new Properties()
        props.load(new StringReader(new String(encoded.toString().decodeBase64(), StandardCharsets.UTF_8)))

        // Set every entry as an Exchange Property again (all values are Strings)
        props.stringPropertyNames().each { k -> message.setProperty(k, props.getProperty(k)) }

        // Remove the Header so it is not sent on to the Receiver System
        message.getHeaders().remove("SSAB_Dispatcher_Properties")
    }
    return message
}
