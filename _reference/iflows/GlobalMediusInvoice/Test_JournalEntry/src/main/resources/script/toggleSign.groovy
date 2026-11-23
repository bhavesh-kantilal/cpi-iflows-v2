import com.sap.it.api.mapping.*;

def String toggleSign(String totalAmount) {

    double value = Double.parseDouble(totalAmount);
    
    double result = value * -1;
    
    return String.valueOf(result);
}