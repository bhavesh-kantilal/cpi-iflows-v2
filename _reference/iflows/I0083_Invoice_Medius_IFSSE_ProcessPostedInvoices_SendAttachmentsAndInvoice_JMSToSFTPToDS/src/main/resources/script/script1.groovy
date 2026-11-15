import com.sap.gateway.ip.core.customdev.util.Message;
import java.util.HashMap;
def Message processData(Message message) {
  
    def properties = message.getProperties();
    String Medius_CompanyId = properties.get("CH_Medius_CompanyId");
    String AttachmentDirMapping = ""
    String AttachmentDir = ""
    String TargetDS = ""
    
    if(Medius_CompanyId.equals("10")){
        AttachmentDirMapping = message.getProperty("AttachmentDirMapping_BO")
        AttachmentDir = message.getProperty("AttachmentDir_BO")
        TargetDS = message.getProperty("Invoice_DS_BO")
    } else if(Medius_CompanyId.equals("20")){
        AttachmentDirMapping = message.getProperty("AttachmentDirMapping_LU")
        AttachmentDir = message.getProperty("AttachmentDir_LU")
         TargetDS = message.getProperty("Invoice_DS_LU")
    }else{
        AttachmentDirMapping = message.getProperty("AttachmentDirMapping_OX")
        AttachmentDir = message.getProperty("AttachmentDir_OX")
         TargetDS = message.getProperty("Invoice_DS_OX")
    }
    message.setProperty("AttachmentDirMapping",AttachmentDirMapping)
    message.setProperty("AttachmentDir",AttachmentDir)
    message.setProperty("TargetDS",TargetDS)
    return message;
}