## 📊 PR Summary

Este Pull Request incluye {{ summary_description }}.

**Estadísticas:**

- 📁 Archivos modificados: {{ files_changed }}
- ➕ Líneas agregadas: {{ lines_added }}
- ➖ Líneas eliminadas: {{ lines_removed }}

## 🔄 Changes

{% for change in changes_list -%}

- {{ change }}
  {% endfor %}

## 📈 Diagrama de Secuencia del Flujo

```mermaid
sequenceDiagram
    actor Dev as 👨‍💻 Desarrollador
    participant Git as 🔧 Git/GitHub
    participant Script as 🐍 generate_pr_docs.py
    participant Files as 📁 Sistema Archivos
    participant Engine as 🎨 Jinja2 Engine

    Dev->>Git: 1. Realiza cambios y commit
    Dev->>Git: 2. git diff > changes.diff

    Dev->>Script: 3. Ejecuta script
    activate Script

    Script->>Files: 4. Lee changes.diff
    Files-->>Script: contenido del diff

    Script->>Files: 5. Lee README.md
    Files-->>Script: contenido del README

    Note over Script: 6. Análisis de cambios
    Script->>Script: Cuenta líneas (+/-)
    Script->>Script: Extrae archivos modificados
    Script->>Script: Detecta tipos de cambios

    Note over Script: 7. Clasificación automática
    Script->>Script: ✨ Nueva funcionalidad?
    Script->>Script: 🐛 Corrección de bugs?
    Script->>Script: 📝 Actualización docs?
    Script->>Script: ♻️ Refactorización?

    Script->>Files: 8. Lee pr_template.md
    Files-->>Script: plantilla Jinja2

    Script->>Engine: 9. Render con datos
    activate Engine
    Engine->>Engine: Procesa variables
    Engine->>Engine: Genera diagrama Mermaid
    Engine-->>Script: Documentación completa
    deactivate Engine

    Script->>Files: 10. Guarda pr_documentation.md
    Files-->>Script: ✅ Guardado exitoso

    deactivate Script
    Script-->>Dev: ✨ Documentación generada

    Note over Dev,Files: Total: {{ files_changed }} archivos, +{{ lines_added }}/-{{ lines_removed }} líneas
```

## 📝 Impact

Este cambio mejora la calidad y funcionalidad del proyecto. Se recomienda revisar los cambios antes de aprobar el merge.

{% if has_new_feature %}
**✨ Características nuevas:** Este PR introduce nuevas funcionalidades al proyecto.
{% endif %}

{% if has_fix %}
**🐛 Correcciones:** Se han solucionado errores o problemas existentes.
{% endif %}

{% if has_docs %}
**📚 Documentación:** La documentación ha sido actualizada o mejorada.
{% endif %}

{% if has_refactor %}
**♻️ Refactorización:** El código ha sido optimizado o reestructurado.
{% endif %}

## ✅ Next Steps

- Revisar los cambios en detalle
- Ejecutar pruebas si están disponibles
- Verificar que la documentación esté actualizada
- Validar el diagrama de secuencia refleja el flujo correcto
