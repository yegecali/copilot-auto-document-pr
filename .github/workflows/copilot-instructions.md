# Copilot PR Documentation Instructions

## 📊 Contexto del PR

Este PR implementa **scripts de automatización** para generar documentación de Pull Requests usando **GitHub Copilot API**:

**Cambios principales:**

- **4 archivos modificados**: scripts Python, documentación, README
- **96 líneas agregadas** / **7 líneas eliminadas**
- Nuevos scripts: `generate_pr_docs.py`, `post_pr_comment.py`, `update_readme.py`
- Sistema de análisis de diffs y generación automática de documentación

**Flujo implementado:**

1. El desarrollador hace cambios en código
2. Ejecuta `generate_pr_docs.py`
3. Script lee el diff + README actual
4. Analiza tipos de cambios (features, fixes, docs, refactor)
5. Genera documentación estructurada del PR
6. Opcionalmente publica comentario en GitHub

---

## 🎯 Tarea Principal

**Genera un diagrama de secuencia en Mermaid** que muestre el flujo completo del sistema de automatización de documentación de PRs implementado.

### Elementos a incluir:

1. **Actores:**
   - Desarrollador
   - Git/GitHub
   - Script generate_pr_docs.py
   - GitHub Copilot API
   - Archivos (diff, README.md, pr_documentation.md)

2. **Flujo de secuencia:**
   - Creación de cambios y commit
   - Extracción del diff
   - Lectura de archivos (diff, README)
   - Análisis de cambios (líneas, archivos, tipo de cambios)
   - Detección de features/bugs/docs/refactor
   - Generación de documentación estructurada
   - Escritura del archivo pr_documentation.md
   - Opcional: Post de comentario en GitHub PR

3. **Detalles técnicos a mostrar:**
   - Análisis de líneas agregadas/eliminadas
   - Detección de archivos modificados
   - Clasificación automática de cambios
   - Generación de estadísticas del PR

### Formato esperado:

```mermaid
sequenceDiagram
    actor Dev as Desarrollador
    participant Git as Git/GitHub
    participant Script as generate_pr_docs.py
    participant Files as Archivos
    participant API as GitHub Copilot API

    [... tu diagrama aquí ...]
```

**Nota:** Enfócate en mostrar claramente el flujo de automatización y análisis de PRs, no en arquitecturas genéricas.
