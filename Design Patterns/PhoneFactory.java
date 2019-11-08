package phone.java;

public class PhoneFactory {
	//use getPhone method to get object of type of phone 
	public Phone getPhone(String phoneType) {
		if(phoneType == null) {
			return null;
			
		}
		if(phoneType.equalsIgnoreCase("ATT")) {
			return new ATT();
		}
		else if(phoneType.equalsIgnoreCase("Sprint")) {
			return new Sprint();
		}
		else if(phoneType.equalsIgnoreCase("Verizon")) {
			return new Verizon();
		}
		return null;
	}

}
