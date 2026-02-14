public class CalculadoraBasica {
    
    // Suma de dos números
    public double sumar(double a, double b) {
        return a + b;
    }
    
    // Resta de dos números
    public double restar(double a, double b) {
        return a - b;
    }
    
    // División de dos números
    public double dividir(double a, double b) {
        if (b == 0) {
            throw new ArithmeticException("No se puede dividir por cero");
        }
        return a / b;
    }
    
    // Método main para pruebas
    public static void main(String[] args) {
        CalculadoraBasica calc = new CalculadoraBasica();
        
        System.out.println("=== Calculadora Básica ===");
        System.out.println("10 + 5 = " + calc.sumar(10, 5));
        System.out.println("10 - 5 = " + calc.restar(10, 5));
        System.out.println("10 / 5 = " + calc.dividir(10, 5));
        
        // Probar división por cero
        try {
            System.out.println("10 / 0 = " + calc.dividir(10, 0));
        } catch (ArithmeticException e) {
            System.out.println("Error: " + e.getMessage());
        }
    }
}
