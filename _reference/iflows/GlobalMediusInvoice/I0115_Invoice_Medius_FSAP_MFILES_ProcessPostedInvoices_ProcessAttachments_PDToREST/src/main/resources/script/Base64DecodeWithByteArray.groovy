import com.sap.gateway.ip.core.customdev.util.Message
import java.util.Base64

def Message processData(Message message) {
    // Retrieve Base64 payload from the message body
    def base64Payload = message.getBody(String)

    // Decode the Base64 payload to a byte array, using the MIME decoder to handle newlines
    byte[] decodedBytes = Base64.mimeDecoder.decode(base64Payload)

    // Calculate the content length
    int contentLength = decodedBytes.length

    // Set the Content-Length header
    message.setHeader("Content-Length", contentLength.toString())

    // Set the decoded byte array as the new message body
    message.setBody(decodedBytes)

    return message
}
