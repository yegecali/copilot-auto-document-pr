import java.util.ArrayList;
import java.util.List;

public class CalculadoraBasica {
    
    // Historial de operaciones
    private final List<String> historial;
    
    public CalculadoraBasica() {
        this.historial = new ArrayList<>();
    }
    
    // Registrar operación en el historial
    private void registrarOperacion(String operacion) {
        historial.add(operacion);
    }
    
    // Obtener historial
    public List<String> getHistorial() {
        return new ArrayList<>(historial);
    }
    
    // Limpiar historial
    public void limpiarHistorial() {
        historial.clear();
    }
    
    // Suma de dos números
    public double sumar(double a, double b) {
        double resultado = a + b;
        registrarOperacion(String.format("%.2f + %.2f = %.2f", a, b, resultado));
        return resultado;
    }
    
    // Resta de dos números
    public double restar(double a, double b) {
        double resultado = a - b;
        registrarOperacion(String.format("%.2f - %.2f = %.2f", a, b, resultado));
        return resultado;
    }
    
    // Multiplicación de dos números
    public double multiplicar(double a, double b) {
        double resultado = a * b;
        registrarOperacion(String.format("%.2f × %.2f = %.2f", a, b, resultado));
        return resultado;
    }
    
    // División de dos números
    public double dividir(double a, double b) {
        if (b == 0) {
            throw new ArithmeticException("No se puede dividir por cero");
        }
        double resultado = a / b;
        registrarOperacion(String.format("%.2f ÷ %.2f = %.2f", a, b, resultado));
        return resultado;
    }
    
    // Módulo (resto de la división)
    public double modulo(double a, double b) {
        if (b == 0) {
            throw new ArithmeticException("No se puede calcular módulo con divisor cero");
        }
        double resultado = a % b;
        registrarOperacion(String.format("%.2f mod %.2f = %.2f", a, b, resultado));
        return resultado;
    }
    
    // Potencia de dos números (a elevado a la b)
    public double potencia(double base, double exponente) {
        double resultado = Math.pow(base, exponente);
        registrarOperacion(String.format("%.2f ^ %.2f = %.2f", base, exponente, resultado));
        return resultado;
    }
    
    // Raíz cuadrada de un número
    public double raizCuadrada(double numero) {
        if (numero < 0) {
            throw new ArithmeticException("No se puede calcular la raíz cuadrada de un número negativo");
        }
        double resultado = Math.sqrt(numero);
        registrarOperacion(String.format("√%.2f = %.2f", numero, resultado));
        return resultado;
    }
    
    // Raíz n-ésima
    public double raizNesima(double numero, double n) {
        if (numero < 0 && n % 2 == 0) {
            throw new ArithmeticException("No se puede calcular raíz par de un número negativo");
        }
        double resultado = Math.pow(numero, 1.0 / n);
        registrarOperacion(String.format("%.0f√%.2f = %.2f", n, numero, resultado));
        return resultado;
    }
    
    // Valor absoluto
    public double valorAbsoluto(double numero) {
        double resultado = Math.abs(numero);
        registrarOperacion(String.format("|%.2f| = %.2f", numero, resultado));
        return resultado;
    }
    
    // Factorial
    public long factorial(int n) {
        if (n < 0) {
            throw new ArithmeticException("No se puede calcular factorial de número negativo");
        }
        if (n > 20) {
            throw new ArithmeticException("Factorial muy grande (máximo 20)");
        }
        long resultado = 1;
        for (int i = 2; i <= n; i++) {
            resultado *= i;
        }
        registrarOperacion(String.format("%d! = %d", n, resultado));
        return resultado;
    }
    
    // Porcentaje (calcular x% de y)
    public double porcentaje(double porcentaje, double total) {
        double resultado = (porcentaje / 100.0) * total;
        registrarOperacion(String.format("%.2f%% de %.2f = %.2f", porcentaje, total, resultado));
        return resultado;
    }
    
    // Logaritmo natural
    public double logaritmoNatural(double numero) {
        if (numero <= 0) {
            throw new ArithmeticException("El logaritmo solo acepta números positivos");
        }
        double resultado = Math.log(numero);
        registrarOperacion(String.format("ln(%.2f) = %.2f", numero, resultado));
        return resultado;
    }
    
    // Logaritmo base 10
    public double logaritmoBase10(double numero) {
        if (numero <= 0) {
            throw new ArithmeticException("El logaritmo solo acepta números positivos");
        }
        double resultado = Math.log10(numero);
        registrarOperacion(String.format("log₁₀(%.2f) = %.2f", numero, resultado));
        return resultado;
    }
    
    // Seno (en radianes)
    public double seno(double angulo) {
        double resultado = Math.sin(angulo);
        registrarOperacion(String.format("sin(%.2f) = %.2f", angulo, resultado));
        return resultado;
    }
    
    // Coseno (en radianes)
    public double coseno(double angulo) {
        double resultado = Math.cos(angulo);
        registrarOperacion(String.format("cos(%.2f) = %.2f", angulo, resultado));
        return resultado;
    }
    
    // Tangente (en radianes)
    public double tangente(double angulo) {
        double resultado = Math.tan(angulo);
        registrarOperacion(String.format("tan(%.2f) = %.2f", angulo, resultado));
        return resultado;
    }
    
    // Convertir grados a radianes
    public double gradosARadianes(double grados) {
        return Math.toRadians(grados);
    }
    
    // Convertir radianes a grados
    public double radianesAGrados(double radianes) {
        return Math.toDegrees(radianes);
    }
    
    // Método main para pruebas
    public static void main(String[] args) {
        CalculadoraBasica calc = new CalculadoraBasica();
        
        System.out.println("=== Calculadora Avanzada ===\n");
        
        // Operaciones básicas
        System.out.println("--- Operaciones Básicas ---");
        System.out.println("10 + 5 = " + calc.sumar(10, 5));
        System.out.println("10 - 5 = " + calc.restar(10, 5));
        System.out.println("10 × 5 = " + calc.multiplicar(10, 5));
        System.out.println("10 ÷ 5 = " + calc.dividir(10, 5));
        System.out.println("10 mod 3 = " + calc.modulo(10, 3));
        
        // Potencias y raíces
        System.out.println("\n--- Potencias y Raíces ---");
        System.out.println("2 ^ 3 = " + calc.potencia(2, 3));
        System.out.println("5 ^ 2 = " + calc.potencia(5, 2));
        System.out.println("√16 = " + calc.raizCuadrada(16));
        System.out.println("√25 = " + calc.raizCuadrada(25));
        System.out.println("∛27 = " + calc.raizNesima(27, 3));
        
        // Otras operaciones
        System.out.println("\n--- Otras Operaciones ---");
        System.out.println("|-15| = " + calc.valorAbsoluto(-15));
        System.out.println("5! = " + calc.factorial(5));
        System.out.println("20% de 150 = " + calc.porcentaje(20, 150));
        System.out.println("ln(10) = " + String.format("%.4f", calc.logaritmoNatural(10)));
        System.out.println("log₁₀(100) = " + calc.logaritmoBase10(100));
        
        // Trigonometría
        System.out.println("\n--- Trigonometría ---");
        double angulo45 = calc.gradosARadianes(45);
        System.out.println("sin(45°) = " + String.format("%.4f", calc.seno(angulo45)));
        System.out.println("cos(45°) = " + String.format("%.4f", calc.coseno(angulo45)));
        System.out.println("tan(45°) = " + String.format("%.4f", calc.tangente(angulo45)));
        
        // Manejo de errores
        System.out.println("\n--- Manejo de Errores ---");
        try {
            System.out.println("10 ÷ 0 = " + calc.dividir(10, 0));
        } catch (ArithmeticException e) {
            System.out.println("Error: " + e.getMessage());
        }
        
        try {
            System.out.println("√-4 = " + calc.raizCuadrada(-4));
        } catch (ArithmeticException e) {
            System.out.println("Error: " + e.getMessage());
        }
        
        try {
            System.out.println("(-1)! = " + calc.factorial(-1));
        } catch (ArithmeticException e) {
            System.out.println("Error: " + e.getMessage());
        }
        
        // Mostrar historial
        System.out.println("\n--- Historial de Operaciones ---");
        List<String> historial = calc.getHistorial();
        System.out.println("Total de operaciones: " + historial.size());
        System.out.println("\nÚltimas 5 operaciones:");
        int inicio = Math.max(0, historial.size() - 5);
        for (int i = inicio; i < historial.size(); i++) {
            System.out.println((i + 1) + ". " + historial.get(i));
        }
    }
}
