# scripts/generate_pr_docs.py
import os
import sys
import requests
from datetime import datetime
from pathlib import Path

# Cargar variables de entorno desde .env
def load_env():
    """Carga variables de entorno desde .env si existe"""
    env_path = Path(__file__).parent / '.env'
    if env_path.exists():
        with open(env_path, 'r') as f:
            for line in f:
                line = line.strip()
                if line and not line.startswith('#') and '=' in line:
                    key, value = line.split('=', 1)
                    os.environ[key.strip()] = value.strip()

load_env()

def analyze_pr_with_copilot(diff_content, readme_content):
    """
    Usa un análisis simple basado en reglas cuando no hay acceso a API
    Para producción, considera usar OpenAI API o Azure OpenAI
    """
    github_token = os.getenv('GITHUB_TOKEN')
    
    if not github_token:
        raise ValueError("GITHUB_TOKEN no configurada. Por favor, configura tu token de GitHub.")
    
    # Análisis básico de cambios
    lines_added = len([l for l in diff_content.split('\n') if l.startswith('+')])
    lines_removed = len([l for l in diff_content.split('\n') if l.startswith('-')])
    files_changed = len(set([l.split()[2] for l in diff_content.split('\n') if l.startswith('+++')]))
    
    # Detectar tipos de cambios
    has_new_feature = any(word in diff_content.lower() for word in ['new', 'add', 'feature', 'implement'])
    has_fix = any(word in diff_content.lower() for word in ['fix', 'bug', 'error', 'issue'])
    has_docs = any(word in diff_content.lower() for word in ['readme', 'doc', 'documentation'])
    has_refactor = any(word in diff_content.lower() for word in ['refactor', 'improve', 'optimize'])
    
    # Generar documentación
    summary_parts = []
    changes_list = []
    
    if has_new_feature:
        summary_parts.append("nuevas funcionalidades")
        changes_list.append("✨ Nueva funcionalidad agregada")
    if has_fix:
        summary_parts.append("correcciones de errores")
        changes_list.append("🐛 Corrección de bugs")
    if has_docs:
        summary_parts.append("mejoras en documentación")
        changes_list.append("📝 Actualización de documentación")
    if has_refactor:
        summary_parts.append("refactorización de código")
        changes_list.append("♻️ Refactorización y optimizaciones")
    
    if not summary_parts:
        summary_parts = ["cambios generales en el código"]
        changes_list = ["🔧 Cambios generales"]
    
    documentation = f"""## 📊 PR Summary

Este Pull Request incluye {', '.join(summary_parts)}.

**Estadísticas:**
- 📁 Archivos modificados: {files_changed}
- ➕ Líneas agregadas: {lines_added}
- ➖ Líneas eliminadas: {lines_removed}

## 🔄 Changes

{chr(10).join(f'- {change}' for change in changes_list)}

## 📝 Impact

Este cambio mejora la calidad y funcionalidad del proyecto. Se recomienda revisar los cambios antes de aprobar el merge.

## ✅ Next Steps

- Revisar los cambios en detalle
- Ejecutar pruebas si están disponibles
- Verificar que la documentación esté actualizada
"""
    
    return documentation

if __name__ == "__main__":
    with open('changes.diff', 'r') as f:
        diff_content = f.read()
    
    # Buscar README en diferentes variantes (prioriza el primero que encuentre)
    readme_variants = ['README.md', 'README.MD', 'readme.md', 'Readme.md']
    readme_path = None
    for variant in readme_variants:
        if Path(variant).exists():
            readme_path = variant
            break
    
    if not readme_path:
        raise FileNotFoundError("No se encontró ningún archivo README (README.md, README.MD, readme.md)")
    
    with open(readme_path, 'r') as f:
        readme_content = f.read()
    
    documentation = analyze_pr_with_copilot(diff_content, readme_content)
    
    # Guardar para el siguiente step
    with open('pr_documentation.md', 'w') as f:
        f.write(documentation)