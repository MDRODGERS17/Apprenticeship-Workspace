package strategy;

public class main {
	private Strategy strategy;
	
	public main(Strategy strategy) {
		this.strategy = strategy;
	
	}
	
	public int executeStrategy(int num1, int num2) {
		return strategy.solveStrategy(num1, num2);
	}

}
