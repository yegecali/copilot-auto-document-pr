# 🤖 Configuración opcional: GitHub Models API

## Estado actual

✅ El sistema funciona perfectamente con el **generador Python** que:

- Analiza el diff automáticamente
- Detecta métodos Java y funciones Python
- Genera diagramas Mermaid inteligentes
- **No requiere configuración adicional**

## ¿Por qué GitHub Models API requiere configuración?

El `GITHUB_TOKEN` automático de GitHub Actions **no tiene** el permiso `models` necesario para usar GitHub Models API. Este es un permiso especial que requiere un Personal Access Token (PAT).

## Cómo habilitar GitHub Models API (opcional)

Si quieres usar GitHub Models API en lugar del generador Python:

### 1. Crear Personal Access Token

1. Ve a GitHub → Settings → Developer settings → [Personal access tokens (classic)](https://github.com/settings/tokens)
2. Click en "Generate new token (classic)"
3. Configuración del token:
   - **Note**: `GitHub Models API for PR Automation`
   - **Expiration**: 90 días o más
   - **Scopes**: Selecciona:
     - ✅ `repo` (Full control of private repositories)
     - ✅ `workflow` (Update GitHub Action workflows)
     - ✅ `models` (Access to GitHub Models API) - **Este es el importante**
4. Click "Generate token"
5. **COPIA EL TOKEN** (solo se muestra una vez)

### 2. Agregar como Secret

1. Ve a tu repositorio → Settings → Secrets and variables → Actions
2. Click "New repository secret"
3. Configuración:
   - **Name**: `GITHUB_MODELS_TOKEN`
   - **Value**: [pega el token copiado]
4. Click "Add secret"

### 3. Actualizar el workflow

Reemplaza el step actual en `.github/workflows/auto-document-pr.yml`:

````yaml
- name: Generate Mermaid diagram with GitHub Models API
  env:
    GITHUB_TOKEN: ${{ secrets.GITHUB_MODELS_TOKEN }} # Usa el nuevo token
  run: |
    echo "🎨 Generando diagrama Mermaid con GitHub Models API..."

    DIFF_CONTENT=$(head -c 4000 changes.diff)

    PAYLOAD=$(jq -n \
      --arg diff "$DIFF_CONTENT" \
      '{
        model: "gpt-4o",
        messages: [
          {
            role: "system",
            content: "Eres un experto en diagramas Mermaid. Respondes SOLO con código Mermaid válido dentro de bloques ```mermaid, sin texto adicional."
          },
          {
            role: "user",
            content: ("Analiza estos cambios de código y genera un diagrama de secuencia Mermaid que muestre el flujo de los nuevos métodos/funciones:\n\n```diff\n" + $diff + "\n```\n\nInstrucciones:\n- Si hay métodos Java, muestra su flujo\n- Si hay funciones Python, muestra cómo interactúan\n- Usa sequenceDiagram para flujos de métodos\n- Responde SOLO con el bloque ```mermaid ... ``` sin explicaciones")
          }
        ],
        temperature: 0.3,
        max_tokens: 1000
      }')

    RESPONSE=$(curl -s -w "\n%{http_code}" -X POST https://models.inference.ai.azure.com/chat/completions \
      -H "Authorization: Bearer $GITHUB_TOKEN" \
      -H "Content-Type: application/json" \
      -d "$PAYLOAD")

    HTTP_CODE=$(echo "$RESPONSE" | tail -n1)
    BODY=$(echo "$RESPONSE" | sed '$d')

    if [ "$HTTP_CODE" = "200" ]; then
      echo "✅ GitHub Models API respondió exitosamente"
      MERMAID_CONTENT=$(echo "$BODY" | jq -r '.choices[0].message.content')
      echo "$MERMAID_CONTENT" > scripts/copilot_mermaid.md
    else
      echo "⚠️  GitHub Models API falló (código $HTTP_CODE), usando fallback..."
      python3 scripts/generate_mermaid.py \
        --diff changes.diff \
        --output scripts/copilot_mermaid.md
    fi
````

## Comparación

| Aspecto          | Generador Python                        | GitHub Models API                    |
| ---------------- | --------------------------------------- | ------------------------------------ |
| Configuración    | ✅ Ninguna                              | ⚠️ Requiere PAT con permiso `models` |
| Costo            | ✅ Gratis                               | ⚠️ Puede tener límites de uso        |
| Velocidad        | ✅ Instantáneo                          | ⏱️ Depende de la API (~2-5 seg)      |
| Calidad diagrama | ✅ Buena (basado en análisis de código) | 🤖 Excelente (GPT-4o)                |
| Fallback         | N/A                                     | ✅ Usa Python si falla               |
| Confiabilidad    | ✅ 100%                                 | ⚠️ Depende de disponibilidad de API  |

## Recomendación

**Continúa usando el generador Python actual**. Es:

- Simple
- Confiable
- Sin configuración
- Genera diagramas correctos

Solo configura GitHub Models API si:

- Necesitas diagramas más elaborados
- Tienes casos de uso complejos
- Quieres experimentar con GPT-4o

## Troubleshooting

### Error 401: Unauthorized

- El token no tiene el permiso `models`
- Verifica que seleccionaste **todos** los scopes necesarios

### Error 429: Rate limit exceeded

- Has excedido el límite de llamadas a la API
- Espera unos minutos o usa el fallback Python

### Error 403: Forbidden

- El repositorio o cuenta no tiene acceso a GitHub Models
- GitHub Models puede estar en beta limitada

## Referencias

- [GitHub Models Documentation](https://docs.github.com/en/enterprise-cloud@latest/rest/models)
- [Personal Access Tokens Guide](https://docs.github.com/en/authentication/keeping-your-account-and-data-secure/creating-a-personal-access-token)
- [Mermaid Diagram Syntax](https://mermaid.js.org/)
