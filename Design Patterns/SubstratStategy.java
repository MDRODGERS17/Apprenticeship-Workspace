package strategy;

public class SubtractStrategy implements Strategy {
	@Override
	public int solveStrategy(int num1, int num2) {
		return num1 - num2;
	}
}
