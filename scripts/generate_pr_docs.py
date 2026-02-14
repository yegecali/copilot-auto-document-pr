# scripts/generate_pr_docs.py
import os
import sys
import requests
from datetime import datetime
from pathlib import Path
from jinja2 import Template

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
    Analiza cambios del PR y genera documentación usando plantilla Jinja2
    """
    github_token = os.getenv('GITHUB_TOKEN')
    
    if not github_token:
        raise ValueError("GITHUB_TOKEN no configurada. Por favor, configura tu token de GitHub.")
    
    print("🔍 Analizando cambios del PR...")
    print(f"📄 Tamaño del diff: {len(diff_content)} caracteres")
    
    # Análisis básico de cambios
    lines_added = len([l for l in diff_content.split('\n') if l.startswith('+') and not l.startswith('+++')])
    lines_removed = len([l for l in diff_content.split('\n') if l.startswith('-') and not l.startswith('---')])
    
    # Extraer archivos cambiados de forma segura
    files = []
    for line in diff_content.split('\n'):
        if line.startswith('+++'):
            parts = line.split()
            if len(parts) >= 2:
                # Formato: +++ b/ruta/archivo.ext
                file_path = parts[1].replace('b/', '') if parts[1].startswith('b/') else parts[1]
                files.append(file_path)
                print(f"  📁 Archivo detectado: {file_path}")
    
    files_changed = len(set(files))
    print(f"✅ Archivos únicos modificados: {files_changed}")
    print(f"➕ Líneas agregadas: {lines_added}")
    print(f"➖ Líneas eliminadas: {lines_removed}")
    
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
    
    # Cargar plantilla Jinja2
    print("📄 Cargando plantilla pr_template.md...")
    template_path = Path(__file__).parent / 'pr_template.md'
    
    if not template_path.exists():
        raise FileNotFoundError(f"No se encontró la plantilla: {template_path}")
    
    with open(template_path, 'r', encoding='utf-8') as f:
        template_content = f.read()
    
    print("✅ Plantilla cargada exitosamente")
    
    # Preparar datos para la plantilla
    template_data = {
        'summary_description': ', '.join(summary_parts),
        'files_changed': files_changed,
        'lines_added': lines_added,
        'lines_removed': lines_removed,
        'changes_list': changes_list,
        'has_new_feature': has_new_feature,
        'has_fix': has_fix,
        'has_docs': has_docs,
        'has_refactor': has_refactor
    }
    
    # Renderizar plantilla con Jinja2
    print("🎨 Renderizando documentación con Jinja2...")
    template = Template(template_content)
    documentation = template.render(**template_data)
    print("✅ Documentación renderizada exitosamente")
    
    return documentation

if __name__ == "__main__":
    print("🚀 Iniciando generación de documentación del PR...")
    
    print("📖 Leyendo changes.diff...")
    with open('changes.diff', 'r') as f:
        diff_content = f.read()
    
    print(f"✓ Diff leído: {len(diff_content)} caracteres")
    
    # Buscar README en diferentes variantes (prioriza el primero que encuentre)
    print("🔍 Buscando README...")
    readme_variants = ['README.md', 'README.MD', 'readme.md', 'Readme.md']
    readme_path = None
    for variant in readme_variants:
        if Path(variant).exists():
            readme_path = variant
            print(f"✓ README encontrado: {variant}")
            break
    
    if not readme_path:
        raise FileNotFoundError("No se encontró ningún archivo README (README.md, README.MD, readme.md)")
    
    print(f"📖 Leyendo {readme_path}...")
    with open(readme_path, 'r') as f:
        readme_content = f.read()
    
    print(f"✓ README leído: {len(readme_content)} caracteres\n")
    
    documentation = analyze_pr_with_copilot(diff_content, readme_content)
    
    print("\n" + "=" * 50)
    print("📝 Documentación generada:")
    print("=" * 50)
    print(documentation)
    print("=" * 50 + "\n")
    
    # Guardar para el siguiente step
    print("💾 Guardando en pr_documentation.md...")
    with open('pr_documentation.md', 'w', encoding='utf-8') as f:
        f.write(documentation)
    
    # Verificar que se guardó correctamente
    if Path('pr_documentation.md').exists():
        saved_size = Path('pr_documentation.md').stat().st_size
        print(f"✅ pr_documentation.md guardado exitosamente ({saved_size} bytes)")
    else:
        print("❌ Error: pr_documentation.md no se pudo guardar")
        import sys
        sys.exit(1)