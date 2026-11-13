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

import java.text.SimpleDateFormat
import java.util.Date

def String checkValidity(String enddate) {
    if (enddate == null || enddate == "") return "false"

    SimpleDateFormat sdf = new SimpleDateFormat("yyyyMMdd")
    
    def dateInput = sdf.format(sdf.parse(enddate)).toInteger()
    def dateToday = sdf.format(new Date()).toInteger()

    if (dateToday > dateInput) {
        return "false"
    } else {
        return "true"
    }
}