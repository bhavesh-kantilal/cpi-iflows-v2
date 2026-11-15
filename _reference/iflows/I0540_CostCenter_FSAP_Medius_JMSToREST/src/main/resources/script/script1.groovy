/* Refer the link below to learn more about the use cases of script.
https://help.sap.com/viewer/368c481cd6954bdfa5d0435479fd4eaf/Cloud/en-GB/148851bf8192412cba1f9d2c17f4bd25.html

If you want to know more about the SCRIPT APIs, refer the link below
https://help.sap.com/doc/a56f52e1a58e4e2bac7f7adbf45b2e26/Cloud/en-GB/index.html */
import com.sap.gateway.ip.core.customdev.util.Message
import groovy.json.JsonSlurper
import groovy.json.JsonOutput

def Message processData(Message message) {

    // body as a reader
    def reader = message.getBody(java.io.Reader)
    if (reader == null) {
        return message
    }

    // Parse JSON
    def json = new JsonSlurper().parse(reader)

    // CE_COSTCENTEREVENTS 
    def data = json.data ?: json

    // Odata
    message.setProperty('ControllingArea',  data.ControllingArea  ?: '')
    message.setProperty('CostCenter',       data.CostCenter       ?: '')
    message.setProperty('ValidityEndDate',  data.ValidityEndDate  ?: '')

    // eventType -> Operation (C/U/D)
    def rawEventType = (json.eventType ?: json.EventType ?: json.type ?: '')?.toString()
    def lowerType = rawEventType.toLowerCase()

    def operation = ''
    if (lowerType.contains('created')) {
        operation = 'C'
    } else if (lowerType.contains('changed')) {
        operation = 'U'
    } else if (lowerType.contains('deleted')) {
        operation = 'D'
    }
    message.setProperty('Operation', operation)

    // Save raw event
    message.setProperty('RAW_EVENT', JsonOutput.toJson(json))

    return message
}

