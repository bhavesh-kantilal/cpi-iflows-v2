import com.sap.it.api.mapping.*;

def void check_MSAP_MULTI_ACCTASSGNMT(String[] name,String[] value, Output output, MappingContext context){
String outputValue =""
for(int i=0;i<name.length;i++){
    if(name[i].equals("MSAP_PO_ACCTASSGMT_DISTR")){
        outputValue = value[i]
        break
    }
 }
 output.addValue(outputValue)
}