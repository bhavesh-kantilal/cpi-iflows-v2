import com.sap.gateway.ip.core.customdev.util.Message;
import com.sap.it.api.pd.PartnerDirectoryService;
import com.sap.it.api.ITApiFactory;
import java.util.HashMap;

def Message processData(Message message) {
    def body = message.getBody(java.lang.String) as String;
    def service = ITApiFactory.getApi(PartnerDirectoryService.class, null); 
    if (service == null){
          throw new IllegalStateException("Partner Directory Service not found");
       }
	String SSAB_LogPayloadAsAttachment = service.getParameter("SSAB_LogPayloadAsAttachment", "SSAB_CPI" , String.class);
	String SSAB_LogPayloadAsAttachment_Size = (service.getParameter("SSAB_LogPayloadAsAttachment_Size", "SSAB_CPI" , String.class));
	def map = message.getProperties();
	String LogPayload =(map?.get("LogPayload")?:'false');
	String LogPayloadSize =(map?.get("LogPayloadSize")?:SSAB_LogPayloadAsAttachment_Size);
	int sizeLimitInBytes = Integer.parseInt(LogPayloadSize) * 1024
	boolean isPayloadLargerThanLimit = (body.getBytes("UTF-8").length > sizeLimitInBytes)

	
	def messageLog = messageLogFactory.getMessageLog(message);
    if(messageLog != null){
		if(!isPayloadLargerThanLimit){
        if(LogPayload.equalsIgnoreCase("true") && SSAB_LogPayloadAsAttachment.equalsIgnoreCase("true")){
            //Get the StepId of the execution
			def mpl = message.getProperty('SAP_MessageProcessingLog')
			def stepId = "payload"
			//In SimulationMode mpl will be null
			if(mpl !=null){
				Set mplKeys = mpl.getContainedKeys()
				stepId = mpl.get(mplKeys.find { it.getName() == 'StepId' })    
			}    
			//GetAttachmentName Property. If this is not set (NULL), then set AttachmentName to StepId
			// If you are in Simulation Mode, then stepId is set to "payload"
			String AttachmentName = (map?.get("AttachmentName") ?: stepId)
			// commented old code to hardcode AttachmentName as payload if null
			//String AttachmentName = (map?.get("AttachmentName")?:'Payload');;
			messageLog.addAttachmentAsString(AttachmentName, body, "text/plain");
        }
     }
	}
    return message;
}