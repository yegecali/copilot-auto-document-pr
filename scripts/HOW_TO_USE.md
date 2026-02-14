# 📚 Cómo usar el sistema de documentación automática de PRs

Este sistema genera automáticamente documentación profesional para tus Pull Requests usando GitHub Copilot.

## 🚀 Flujo de trabajo

```
PR abierto/actualizado
    ↓
GitHub Actions se activa
    ↓
1. Genera diff: changes.diff
    ↓
2. 🎨 generate_mermaid.py → scripts/copilot_mermaid.md
    ↓
3. 📊 copilot_analyzer.py → pr_context.json
    ↓
4. 📝 generate_docs.py → pr_documentation.md + pr_history/
    ↓
5. 💬 post_pr_comment.py (comenta en el PR)
    ↓
6. 📖 update_readme.py (actualiza README)
    ↓
Commit automático [skip ci]
```

## 📂 Estructura de scripts

- **`generate_mermaid.py`**: Genera diagrama Mermaid con Copilot CLI (fallback básico)
- **`copilot_analyzer.py`**: Analiza diff, extrae métodos, carga Mermaid
- **`generate_docs.py`**: Renderiza template Jinja2, valida JSON, guarda historial
- **`generate_pr_docs.py`**: Orquestador que ejecuta analyzer → generator
- **`post_pr_comment.py`**: Postea documentación en comentario del PR
- **`update_readme.py`**: Actualiza README.md con última versión PR
- **`pr_template.md`**: Template Jinja2 con variables dinámicas

## 🔧 Uso local (desarrollo)

### 1. Generar diagrama Mermaid

```bash
# Generar desde un diff existente
python3 scripts/generate_mermaid.py --diff changes.diff --output scripts/copilot_mermaid.md

# Ver output
cat scripts/copilot_mermaid.md
```

### 2. Generar documentación completa

```bash
# Generar diff
git diff main...HEAD > changes.diff

# Ejecutar pipeline completo
python3 scripts/generate_pr_docs.py \
  --diff changes.diff \
  --context pr_context.json \
  --output pr_documentation.md \
  --template scripts/pr_template.md

# Ver resultado
cat pr_documentation.md
cat pr_context.json
ls -la pr_history/
```

### 3. Revisar historial de PRs

```bash
# Ver índice histórico
cat pr_history/history.json

# Ver documentación específica de un PR
cat pr_history/pr_5_v2.md
```

## 🎯 Configuración GitHub Actions

El workflow `.github/workflows/auto-document-pr.yml` se ejecuta automáticamente en:

- `pull_request: opened`
- `pull_request: synchronize`

### Variables de entorno necesarias

- `GITHUB_TOKEN`: Token automático de GitHub (ya disponible)

### Permisos requeridos

```yaml
permissions:
  contents: write # Para hacer commits
  pull-requests: write # Para comentar en PRs
```

## 💡 Características

✅ **Diagramas Mermaid generados por Copilot** - Usa Copilot CLI o fallback inteligente  
✅ **Análisis automático de código** - Detecta métodos Java y funciones Python  
✅ **Historial de versiones** - Guarda cada versión del PR en `pr_history/`  
✅ **Comparación con PR anterior** - Muestra delta de cambios  
✅ **Template Jinja2** - Personalizable vía `pr_template.md`  
✅ **Validación JSON Schema** - Garantiza calidad de datos  
✅ **CLI completo** - Argumentos flexibles para testing  
✅ **Emoji logs** - Output legible con iconos

## 🐛 Troubleshooting

### El diagrama Mermaid no se genera

1. Verificar que `gh copilot` está instalado:

   ```bash
   gh extension list | grep copilot
   ```

2. Si no está disponible, el script usará fallback básico automáticamente

### El workflow falla en GitHub Actions

1. Revisar logs del workflow
2. Verificar que `scripts/requirements.txt` tiene todas las dependencias:
   ```
   jinja2>=3.1.0
   requests>=2.31.0
   python-dotenv>=1.0.0
   ```

### No se detectan métodos en el diff

1. Verificar que el diff no está vacío:

   ```bash
   cat changes.diff
   ```

2. El script actual detecta:
   - Java: `public [static] tipo nombreMetodo(`
   - Python: `def nombre_funcion(`

## 📖 Ejemplo de output

### pr_context.json

````json
{
  "pr_number": 5,
  "pr_title": "Add power and square root to calculator",
  "pr_description": "Enhanced mathematical operations",
  "code_changes": "Added 15 new methods",
  "new_methods": ["potencia()", "raizCuadrada()"],
  "mermaid_diagram": "```mermaid\nsequenceDiagram...",
  "comparison_summary": "Previous PR #4 modified 3 files..."
}
````

### pr_documentation.md

```markdown
# 📋 Documentación del PR #5

## 📝 Resumen

Enhanced mathematical operations

## 🔄 Diagrama de cambios

[Mermaid diagram here]

## 🆕 Métodos nuevos

- `potencia(double base, double exponente)`
- `raizCuadrada(double numero)`
  ...
```

## 🔗 Referencias

- [GitHub Actions Docs](https://docs.github.com/actions)
- [Jinja2 Template Engine](https://jinja.palletsprojects.com/)
- [Mermaid Syntax](https://mermaid.js.org/)
- [GitHub Copilot CLI](https://github.com/github/gh-copilot)
