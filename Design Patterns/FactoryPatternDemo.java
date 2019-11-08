package phone.java;

public class FactoryPatternDemo {

	public static void main(String[] args) {
		PhoneFactory PhoneFactory = new PhoneFactory();
		
		//get an object of ATT and call its provider method.
		Phone phone1 = PhoneFactory.getPhone("ATT");
		
		//call provider method of phone
		phone1.provider();
		
		//get an object of Sprint and call its provider method.
		Phone phone2 = PhoneFactory.getPhone("Sprint");
		
		//call provider method of phone
		phone2.provider();
		
		//get an object of Sprint and call its provider method.
		Phone phone3 = PhoneFactory.getPhone("Verizon");
		
		//call provider method of phone
		phone3.provider();
	}

}
