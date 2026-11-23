/*
 * CopyPropertiesToHeader.groovy  (Parent IFlow, SSAB Simplified Pipeline)
 * Place: just before the JMS Receiver that writes to the Receiver Queue.
 * Exchange Properties are not transferred over JMS / Process Direct, Headers are.
 * This script packs all Properties into one Header, SSAB_Dispatcher_Properties.
 * The Child IFlow unpacks it again with HeaderToProperties.groovy.
 * Only runs when Property SSAB_Dispatcher_CopyPropertiesToHeader = Yes.
 */
import com.sap.gateway.ip.core.customdev.util.Message
import java.nio.charset.StandardCharsets

def Message processData(Message message) {
    // Opt-in flag: do nothing unless the Parent IFlow sets it to Yes (any case)
    def flag = message.getProperty("SSAB_Dispatcher_CopyPropertiesToHeader")?.toString()
    if (!flag?.equalsIgnoreCase("Yes")) {
        return message
    }

    // Copy all Properties as Strings; null values are skipped (java.util.Properties cannot hold null)
    def props = new Properties()
    message.getProperties().each { k, v -> if (v != null) props.setProperty(k, v.toString()) }

    // Write them as key=value text (standard Java, no JSON, so the CPI script check stays clean)
    def writer = new StringWriter()
    props.store(writer, null)

    // Base64 encode so special characters and line breaks are safe in a Header
    message.setHeader("SSAB_Dispatcher_Properties", writer.toString().getBytes(StandardCharsets.UTF_8).encodeBase64().toString())
    return message
}
