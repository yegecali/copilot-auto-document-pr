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

{% if changed_files_details %}

**Archivos modificados:**
{% for file_detail in changed_files_details -%}

- `{{ file_detail }}`
  {% endfor %}
  {% endif %}

## 📈 Diagrama de Cambios

{% if mermaid_diagram %}
{{ mermaid_diagram }}
{% else %}

```mermaid
graph LR
    A[Código Original] -->|{{ files_changed }} archivos| B[Cambios Aplicados]
    B -->|+{{ lines_added }} líneas| C[Código Actualizado]
    B -->|−{{ lines_removed }} líneas| C

    {% if has_new_feature %}
    C --> D[✨ Nuevas Funcionalidades]
    {% endif %}
    {% if has_fix %}
    C --> E[🐛 Correcciones]
    {% endif %}
    {% if has_refactor %}
    C --> F[♻️ Optimizaciones]
    {% endif %}
```

{% endif %}

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
