def processData(message) {
    def body = message.getBody(String)
    def xml = new XmlSlurper().parseText(body)
    
    def allNotes = xml.'**'.findAll { it.name() == 'Note' }*.text()
    
    message.setProperty("prop_error", allNotes.join(" | "))
    return message
}