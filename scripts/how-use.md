# 📚 Scripts - Automatización con GitHub Copilot API

Colección de scripts para automatizar tareas de desarrollo usando **GitHub Copilot API**.

## 📋 Scripts Disponibles

### 1. **generate_pr_docs.py** ⭐

Genera documentación automática para Pull Requests usando GitHub Copilot AI.

**¿Qué hace?**

- Analiza cambios de un PR (diff)
- Lee el README actual del proyecto
- Genera automáticamente:
  - Resumen ejecutivo de cambios
  - Lista de features/fixes
  - Impacto en arquitectura
  - Actualización sugerida para README.md

**Ideal para:**

- Automatizar documentación de PRs
- Mantener README actualizado
- Ahorrar tiempo en revisiones
- Asegurar documentación consistente

---

## 🚀 Instalación Rápida

### 1️⃣ Instalar Dependencias

```bash
cd scripts
pip install -r requirements.txt
```

**Dependencias:**

- `requests>=2.31.0` - Para llamadas HTTP
- `python-dotenv>=1.0.0` - Para cargar variables de entorno

### 2️⃣ Configurar GitHub Token

#### Opción A: Archivo `.env` (Recomendado) 🎯

```bash
# Guarda tu token de GitHub localmente
cat > .env << EOF
GITHUB_TOKEN=ghp_xxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx
EOF
```

#### Opción B: Variable de Entorno Global

```bash
# macOS/Linux
export GITHUB_TOKEN=ghp_xxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx

# Windows (PowerShell)
$env:GITHUB_TOKEN="ghp_xxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx"
```

#### Opción C: GitHub CLI (Automático)

```bash
# Si tienes GitHub CLI instalado y autenticado
gh auth login
# El script detectará tu token automáticamente
```

### 3️⃣ Obtener tu GitHub Token

1. Abre https://github.com/settings/tokens
2. Click en **"Generate new token"** → **Classic**
3. Dale un nombre: `copilot-pr-docs`
4. Selecciona estos permisos:
   - ✅ `repo` (acceso completo a repositorios)
   - ✅ `copilot` (acceso a Copilot API)
5. Click en **"Generate token"**
6. **Copia el token inmediatamente** (solo se mostrará una vez)

---

## 📖 Cómo Usar `generate_pr_docs.py`

### Estructura de Archivos

El script espera estos archivos en el mismo directorio:

```
scripts/
├── generate_pr_docs.py
├── .env                    # Tu configuración (copia de .env.example)
├── changes.diff           # Los cambios del PR (requerido)
└── README.md              # El README actual (requerido)
```

### Paso 1: Preparar los Cambios

```bash
# Generar el diff de cambios
git diff > scripts/changes.diff

# O manualmente, copia el diff en scripts/changes.diff
```

### Paso 2: Confirmar el README

```bash
# Copiar el README actual
cp README.md scripts/README.md

# El script lo leerá como referencia
```

### Paso 3: Ejecutar el Script

```bash
python scripts/generate_pr_docs.py
```

### Paso 4: Revisar Resultados

```bash
# El script genera:
cat scripts/pr_documentation.md
```

**Salida esperada:**

```
## PR Summary
Descripción general de los cambios implementados...

## Changes
- Feature: Nuevo sistema de autenticación
- Fix: Corrección en validación de entrada
- Feature: Soporte para múltiples lenguajes

## README Update
### Características Nuevas
...
```

---

## 💡 Ejemplos de Uso

### Ejemplo 1: Documentar un PR Simple

```bash
# Cambios realizados
git diff > scripts/changes.diff

# Ejecutar análisis
cd scripts && python generate_pr_docs.py

# Ver documentación generada
cat pr_documentation.md
```

### Ejemplo 2: En un CI/CD Pipeline

```yaml
# GitHub Actions ejemplo
- name: Generate PR Documentation
  run: |
    cd scripts
    pip install -r requirements.txt
    git diff > changes.diff
    python generate_pr_docs.py

- name: Upload Documentation
  uses: actions/upload-artifact@v2
  with:
    name: pr-documentation
    path: scripts/pr_documentation.md
```

### Ejemplo 3: Script Automatizado

```bash
#!/bin/bash
# auto-doc-pr.sh

cd scripts

# Generar diff
git diff > changes.diff

# Generar documentación
python generate_pr_docs.py

# Actualizar README si quieres
# cat pr_documentation.md >> ../../README.md
```

---

## 🔧 Configuración Avanzada

### Variables de Entorno

Puedes personalizar el comportamiento modificando `generate_pr_docs.py`:

```python
# Cambiar el modelo de IA
"model": "gpt-4"               # Opciones: gpt-4, gpt-4-turbo, gpt-3.5-turbo

# Ajustar la temperatura (0-1)
"temperature": 0.3             # Más bajo = más determinista, más alto = más creativo

# Cambiar límite de tokens
"max_tokens": 2000             # Máximo de caracteres a generar
```

### Sistema Prompt Personalizado

Modifica el system prompt para obtener documentación en tu estilo:

```python
{"role": "system", "content": "Eres un documentador técnico experto en castellano..."}
```

---

## 🐛 Troubleshooting

### Error: "GITHUB_TOKEN no configurada"

```bash
# Verifica que el token está configurado
echo $GITHUB_TOKEN

# Si está vacío, configúralo
export GITHUB_TOKEN=ghp_xxxx...

# O crea .env en scripts/
cat > scripts/.env << EOF
GITHUB_TOKEN=ghp_xxxx...
EOF
```

### Error: "401 - Unauthorized"

```bash
# El token es inválido o expiró
# Genera uno nuevo: https://github.com/settings/tokens

# Verifica que el token tiene los permisos correctos:
# - repo
# - copilot
```

### Error: "403 - Forbidden"

```bash
# Tu cuenta no tiene acceso a Copilot API
# Soluciones:
# 1. Verifica que tienes Copilot habilitado en tu cuenta
# 2. Algunos tokens pueden requerir suscripción a Copilot
# 3. Intenta generar un nuevo token
```

### Error: "changes.diff no encontrado"

```bash
# Genera el diff primero
cd scripts
git diff > changes.diff

# O proporciona el archivo manualmente
```

### Error: "README.md no encontrado"

```bash
# Copia el README al directorio scripts
cp README.md scripts/README.md
```

### El script está lento

```bash
# Es normal si es la primera vez (2-5 segundos)
# Si tarda más:
# 1. Revisa tu conexión a internet
# 2. GitHub API puede estar bajo carga
# 3. Intenta de nuevo en unos minutos
```

---

## 🔐 Seguridad

### Proteger tu Token

⚠️ **IMPORTANTE:**

- ❌ **NO** hagas commit de tu `.env`
- ✅ Usa `.gitignore` para excluir `.env`
- ✅ Usualmente ya está en el `.gitignore` del proyecto
- ✅ Regenera tu token si crees que se expuso

### Verificar `.gitignore`

```bash
# Confirma que .env está en .gitignore
cat .gitignore | grep -E "\.env|secrets"

# Si no está, agrégalo
echo ".env" >> .gitignore
echo ".env.local" >> .gitignore
```

---

## 📊 Dependencias

| Paquete         | Versión  | Propósito                                |
| --------------- | -------- | ---------------------------------------- |
| `requests`      | >=2.31.0 | Comunicación HTTP con GitHub Copilot API |
| `python-dotenv` | >=1.0.0  | Cargar variables de entorno desde `.env` |

---

## 📚 Documentación Adicional

- **[COPILOT_API_SETUP.md](COPILOT_API_SETUP.md)** - Guía detallada de configuración
- **[QUICK_START.md](QUICK_START.md)** - Inicio rápido
- **[.env.example](.env.example)** - Template de configuración
- **[requirements.txt](requirements.txt)** - Dependencias Python

---

## 🤝 Contribuir

¿Quieres mejorar estos scripts? ¡Haz un PR!

Algunas ideas:

- [ ] Soporte para otros formatos de documentación
- [ ] Análisis de cobertura de código
- [ ] Validación de cambios
- [ ] Integración con más sistemas de CI/CD
- [ ] Múltiples idiomas de salida

---

## 📝 Licencia

MIT

---

## ❓ Preguntas Frecuentes

**P: ¿Necesito Copilot Pro?**  
R: No necesariamente, pero algunos usuarios reportan mejor acceso con Copilot Pro.

**P: ¿Puedo usar esto sin token?**  
R: No, se requiere un GitHub Token válido con acceso a Copilot API.

**P: ¿Qué información se envía a GitHub?**  
R: Tu diff de cambios y README actual. No se almacena en GitHub.

**P: ¿Cuál es el costo?**  
R: Normalmente gratuito si tienes acceso a Copilot. Verifica tu plan.

**P: ¿Hay límite de uso?**  
R: GitHub Copilot API tiene límites de tasa, generalmente suficientes para uso normal.

**P: ¿Puedo usar esto en Windows?**  
R: Sí, Python funciona en todos los SO. Solo necesitas Python 3.8+ instalado.

---

## 🚀 Próximos Pasos

1. **Instala**: `pip install -r requirements.txt`
2. **Configura**: Crea `scripts/.env` con tu `GITHUB_TOKEN`
3. **Prueba**: `python scripts/generate_pr_docs.py`
4. **Automatiza**: Añade a tu CI/CD pipeline

---

## 📞 Soporte

Si tienes problemas:

1. Revisa el [Troubleshooting](#-troubleshooting)
2. Verifica que cumples los [requisitos](#requisitos)
3. Mira la [documentación detallada](COPILOT_API_SETUP.md)
4. Abre un issue en el repositorio

---

**¡Hecho con ❤️ usando GitHub Copilot API!**
