import com.sap.gateway.ip.core.customdev.util.Message;

def Message processData(Message message) {
    
	def messageLog = messageLogFactory.getMessageLog(message);
	def properties = message.getProperties();
	if(messageLog != null){
        properties.each { key, value ->
            if (key.startsWith("CH_")) {
                def logKey = key.replaceAll("CH_", "")
                def logValue = value != null ? value.toString() : "null"
                messageLog.addCustomHeaderProperty(logKey, logValue.take(5000)); // avoid truncation issues
            }
        }
	}
	return message;
}