package strategy;

import javax.naming.Context;

public class StrategyPatternDemo {

	public static void main(String[] args) {
		main main = new main(new AddStrategy());
		System.out.println("25 + 75 = " + main.executeStrategy(25, 75));
		
		main = new main(new SubtractStrategy());
		System.out.println("100 - 22 = " + main.executeStrategy(100, 22));
		
		main = new main(new MultiplyStrategy());
		System.out.println("208 * 48 = " + main.executeStrategy(208, 48));

	}

}
