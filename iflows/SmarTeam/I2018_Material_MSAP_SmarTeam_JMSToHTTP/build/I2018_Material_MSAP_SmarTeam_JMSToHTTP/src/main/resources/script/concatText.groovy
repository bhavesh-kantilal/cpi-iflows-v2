

import com.sap.it.api.mapping.Output;
import com.sap.it.api.mapping.MappingContext;
/*
def void custFunc2(String[] is,String[] ps, Output output, MappingContext context) {
        String value1 = context.getHeader(is[0]);
        String value2 = context.getProperty(ps[0]);
        output.addValue(value1);
        output.addValue(value2);
}
*/

def  void concatText(String[] is, Output output, MappingContext context) {
       String concatString = "";
       for(int i=0;i<is.length;i++){
           if(concatString.equals("")){
               concatString = is[i]
           }else{
              concatString = concatString + "\r\n"+ is[i]
           }
       }
       output.addValue(concatString);
}