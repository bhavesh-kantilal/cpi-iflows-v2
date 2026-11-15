import groovy.json.JsonSlurper
import com.sap.gateway.ip.core.customdev.util.Message


def Message processData(Message message) {


def body = message.getBody(String)
def json = new JsonSlurper().parseText(body)

// companyId looks like: "company[FI00]"
// We need: FI00
def companyId = json[0]?.companyId
def companyCode = (companyId =~ /.*\[(.*)\]/)[0][1]  // extract text inside []

message.setProperty("CH_CompanyCode", companyCode)

return message
}
