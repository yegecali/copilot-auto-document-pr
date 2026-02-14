import java.nio.charset.StandardCharsets;
import java.util.Base64;

public class StringUtils {

	public static String encodeBase64(String value) {
		if (value == null) {
			throw new IllegalArgumentException("El valor no puede ser null");
		}
		return Base64.getEncoder().encodeToString(value.getBytes(StandardCharsets.UTF_8));
	}
}
