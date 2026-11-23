import com.sap.gateway.ip.core.customdev.util.Message
import groovy.util.XmlSlurper

def Message processData(Message message) {
    def body = message.getBody(String)
    def response = new XmlSlurper().parseText(body)

    def base64Xml = response.EV_XML_X.text()
    byte[] decoded = base64Xml.decodeBase64()
    def idocXml = new String(decoded, 'UTF-8')

    message.setBody(idocXml)
    message.setHeader('Content-Type', 'application/xml')
    return message
}