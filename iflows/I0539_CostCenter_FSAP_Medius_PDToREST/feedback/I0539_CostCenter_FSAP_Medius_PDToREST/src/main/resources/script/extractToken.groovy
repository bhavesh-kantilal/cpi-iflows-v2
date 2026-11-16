import groovy.json.JsonSlurper

def body = message.getBody(String)
def json = new JsonSlurper().parseText(body)
message.setProperty("access_token", json.access_token)

return message