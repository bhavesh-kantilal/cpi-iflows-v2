//Groovy : Convert deep nested specified JSON elements to double or Boolean data types
import groovy.json.JsonSlurper
import groovy.json.JsonOutput
import groovy.json.JsonBuilder
import com.sap.gateway.ip.core.customdev.util.Message
def Message processData(Message message) 
{
    def body = message.getBody(java.lang.String)
    def jsonSlurper = new JsonSlurper()
    def json = new JsonSlurper().parseText(body)
    //Get Message Properties
   // def NumericFieldsToConvert=message.getProperty("Numericfields").split(",")
    def BooleanFieldsToConvert=message.getProperty("Booleanfields").split(",")
    // Call the conversion function with the root of the JSON
    convertGPaths(json,BooleanFieldsToConvert)
    // Convert the modified JSON back to a string
    def modifiedJsonStr = new JsonBuilder(json).toPrettyString()    
    message.setBody(modifiedJsonStr)
    return message
}

def convertGPaths(node,BooleanFieldsToConvert)
{
if (node instanceof Map) 
{
    println("Node:"+node)
    node.each { key, value ->

        println("Key : "+key)
        println("Value :"+value)
        //Double fields
    
        //boolean fields
        if (key in BooleanFieldsToConvert)
        {
            try 
            {
            node[key] = value.toBoolean()
            }//try
            catch (Exception e)
            {
            node[key] = value
            }//catch
        } //if 

        else if (value instanceof Map || value instanceof List) 
        {
            node[key]=convertGPaths(value,BooleanFieldsToConvert)
        }//else if
        else
        {
            node[key] = value
        }
    }//node.each
}//if
else if (node instanceof List) 
{
        node.each { item ->
            if (item instanceof Map || item instanceof List) 
            {
                convertGPaths(item,BooleanFieldsToConvert)
            }//if
        }//node.each
}//else if
}//convertGPaths