import com.sap.it.api.mapping.*;

def void check_MSAP_GR_UOM(String[] name,String[] value, Output output, MappingContext context){
String outputValue =""
for(int i=0;i<name.length;i++){
    if(name[i].equals("MSAP_GR_UOM")){
        outputValue = value[i]
        break
    }
 }
 output.addValue(outputValue)
}