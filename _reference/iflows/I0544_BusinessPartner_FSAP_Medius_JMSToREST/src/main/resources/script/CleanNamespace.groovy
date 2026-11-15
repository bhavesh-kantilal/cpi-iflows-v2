import com.sap.gateway.ip.core.customdev.util.Message;

def Message processData(Message message) {
    def body = message.getBody(java.lang.String);
    
    body = body.replaceAll(/\s?xsi:\w+="[^"]*"/, "");
    body = body.replaceAll(/\s?xmlns(:?\w+)?="[^"]*"/, "");
    body = body.replaceAll(/<\/?[a-zA-Z0-9]+:/, { it.getAt(0) == '<' && it.getAt(1) == '/' ? '</' : '<' });
    
    message.setBody(body);
    return message;
}