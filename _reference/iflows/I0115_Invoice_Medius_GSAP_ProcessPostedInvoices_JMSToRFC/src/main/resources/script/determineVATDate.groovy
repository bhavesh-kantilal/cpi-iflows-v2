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

def String determineVATDate(String companyCode,String VATDate, String invoiceDate, String finalBookingDate, String receivedDate ){
	String returnDate = ""
	if(companyCode.startsWith("PL")){
	    if(VATDate.equals("")){
	       if(receivedDate.equals("")){
	        returnDate= invoiceDate.substring(0,10)
	       }else{
	        returnDate= receivedDate.substring(0,10)
	       }
	    }else{
	        returnDate= VATDate.substring(0,10)
	    }
	}else if(companyCode.startsWith("CZ") || companyCode.startsWith("SK")){
	       if(VATDate.equals("")){
	        returnDate= invoiceDate.substring(0,10)
	    }else{
	        returnDate= VATDate.substring(0,10)
	    }
	}else{
	    
	}
	return returnDate
}