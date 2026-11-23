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

def void GetDeliveryDetails(String[] delivery,String[] metaDataName,String[] metaDataValue, Output output, MappingContext context) {
   boolean valueFound =  false
   if(delivery[0].startsWith("500")){
       for(int i=0;i<metaDataName.length;i++){
           
           if((metaDataName[i].equals("MSAP_ENTRY_SHEET"))||(metaDataName[i].equals("MSAP_Reference_GR"))){
              def value = "__"
                 try {
                    value = metaDataValue[i]
                } catch (ArrayIndexOutOfBoundsException e) {
                    // just use "__"
                }
                output.addValue(value)
               valueFound = true
               break
           }
           else if(metaDataName[i].equals("MSAP_INVOICE_PLAN"))
           {
                output.addValue("__")
                valueFound = true
                break
           }
       }
       if(valueFound == false){
            output.addValue(delivery[0])
       }
   }else{
       output.addValue("__")
   }
}