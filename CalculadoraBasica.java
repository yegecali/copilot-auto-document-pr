public class CalculadoraBasica {
    
    // Suma de dos números
    public double sumar(double a, double b) {
        return a + b;
    }
    
    // Resta de dos números
    public double restar(double a, double b) {
        return a - b;
    }
    
    // Multiplicación de dos números
    public double multiplicar(double a, double b) {
        return a * b;
    }
    
    // División de dos números
    public double dividir(double a, double b) {
        if (b == 0) {
            throw new ArithmeticException("No se puede dividir por cero");
        }
        return a / b;
    }
    
    // Potencia de dos números (a elevado a la b)
    public double potencia(double base, double exponente) {
        return Math.pow(base, exponente);
    }
    
    // Raíz cuadrada de un número
    public double raizCuadrada(double numero) {
        if (numero < 0) {
            throw new ArithmeticException("No se puede calcular la raíz cuadrada de un número negativo");
        }
        return Math.sqrt(numero);
    }
    
    // Método main para pruebas
    public static void main(String[] args) {
        CalculadoraBasica calc = new CalculadoraBasica();
        
        System.out.println("=== Calculadora Básica ===");
        System.out.println("10 + 5 = " + calc.sumar(10, 5));
        System.out.println("10 - 5 = " + calc.restar(10, 5));
        System.out.println("10 * 5 = " + calc.multiplicar(10, 5));
        System.out.println("10 / 5 = " + calc.dividir(10, 5));
        System.out.println("2 ^ 3 = " + calc.potencia(2, 3));
        System.out.println("√16 = " + calc.raizCuadrada(16));
        System.out.println("5 ^ 2 = " + calc.potencia(5, 2));
        System.out.println("√25 = " + calc.raizCuadrada(25));
        
        // Probar división por cero
        try {
            System.out.println("10 / 0 = " + calc.dividir(10, 0));
        } catch (ArithmeticException e) {
            System.out.println("Error: " + e.getMessage());
        }
        
        // Probar raíz cuadrada de número negativo
        try {
            System.out.println("√-4 = " + calc.raizCuadrada(-4));
        } catch (ArithmeticException e) {
            System.out.println("Error: " + e.getMessage());
        }
    }
}
