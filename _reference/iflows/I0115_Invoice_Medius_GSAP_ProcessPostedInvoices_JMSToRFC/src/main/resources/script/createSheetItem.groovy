import com.sap.it.api.mapping.*;

/*Add MappingContext parameter to read or set headers and properties
def String customFunc1(String P1,String P2,MappingContext context) {
         String value1 = context.getHeader(P1);
         String value2 = context.getProperty(P2);
         return value1+value2;
}

Add Output parameter to assign the output value.
def void custFunc2(String[] is,String[] ps, Output output, MappingContext context) {
        String value1 = context.getHeader(is[0]);
        String value2 = context.getProperty(ps[0]);
        output.addValue(value1);
        output.addValue(value2);
}*/

def void createSheetItem(String[] metaDataName,String[] metaDataValue, Output output, MappingContext context){
    String GSAP_ENTRY_SHEET_Found = "";
    String finalOutput=""
	for(int i=0;i<metaDataName.length;i++){
	    if(metaDataName[i].equals("GSAP_SUBPACKNO")){
	        //output.addValue(metaDataValue[i])
	        finalOutput = metaDataValue[i]
	        break;
	    }
	     if(metaDataName[i].equals("GSAP_ENTRY_SHEET")){
	            GSAP_ENTRY_SHEET_Found = "true"
	        }
	    
	}
	if(finalOutput.equals("")){
	    if(GSAP_ENTRY_SHEET_Found.equals("true")){
	        output.addValue("0000000010")
	    
	    }    
	}else{
	    output.addValue(finalOutput)
	}
	
	
	
}