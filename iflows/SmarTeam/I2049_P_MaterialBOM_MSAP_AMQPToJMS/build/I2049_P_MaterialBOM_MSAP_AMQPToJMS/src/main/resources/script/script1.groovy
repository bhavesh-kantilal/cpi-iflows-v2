import com.sap.gateway.ip.core.customdev.util.Message

def Message processData(Message message) {
    def body = message.getBody(String)
    def json = new groovy.json.JsonSlurper().parseText(body)
    def data = json.data

    message.setProperty("BillOfMaterialVariantUsage", data.BillOfMaterialVariantUsage)
    message.setProperty("BillOfMaterial", data.BillOfMaterial)
    message.setProperty("BillOfMaterialCategory", data.BillOfMaterialCategory)
    message.setProperty("BillOfMaterialVariant", data.BillOfMaterialVariant)
    message.setProperty("Material", data.Material)
    message.setProperty("Plant", data.Plant)

    return message
}