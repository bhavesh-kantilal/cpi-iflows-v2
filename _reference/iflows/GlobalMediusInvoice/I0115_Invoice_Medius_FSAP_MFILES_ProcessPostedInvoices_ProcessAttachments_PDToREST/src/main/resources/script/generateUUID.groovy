import com.sap.gateway.ip.core.customdev.util.Message
import java.util.UUID

def Message processData(Message message) {
    
def uuid = UUID.randomUUID().toString().toUpperCase().replace("-", "")
message.setProperty("CH_DocumentID", uuid)
return message
}
