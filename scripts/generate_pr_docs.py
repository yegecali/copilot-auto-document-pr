# scripts/generate_pr_docs.py
import os
import sys
import json
import re
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

def slugify(value):
    """Convierte texto a slug seguro para nombres de archivo"""
    if not value:
        return "pr"
    value = value.lower()
    value = re.sub(r"[^a-z0-9]+", "-", value)
    return value.strip("-") or "pr"

def load_pr_context():
    """Carga datos del PR desde variables de entorno o evento de GitHub"""
    pr_number = os.getenv("PR_NUMBER")
    pr_title = os.getenv("PR_TITLE")
    pr_url = os.getenv("PR_URL")
    repo = os.getenv("GITHUB_REPOSITORY")
    event_path = os.getenv("GITHUB_EVENT_PATH")

    if event_path and Path(event_path).exists():
        try:
            with open(event_path, "r", encoding="utf-8") as f:
                event = json.load(f)
            pr = event.get("pull_request", {})
            pr_number = pr_number or pr.get("number")
            pr_title = pr_title or pr.get("title")
            pr_url = pr_url or pr.get("html_url")
            repo = repo or event.get("repository", {}).get("full_name")
        except (json.JSONDecodeError, OSError):
            pass

    return {
        "number": pr_number,
        "title": pr_title or "PR sin titulo",
        "url": pr_url,
        "repo": repo
    }

def get_history_paths():
    base_dir = Path(__file__).resolve().parent.parent
    history_dir = base_dir / "pr_history"
    index_path = history_dir / "history.json"
    latest_path = history_dir / "latest.md"
    return history_dir, index_path, latest_path

def load_history_index(index_path):
    if index_path.exists():
        try:
            with open(index_path, "r", encoding="utf-8") as f:
                return json.load(f)
        except (json.JSONDecodeError, OSError):
            return {"entries": []}
    return {"entries": []}

def save_history_index(index_path, data):
    index_path.parent.mkdir(parents=True, exist_ok=True)
    with open(index_path, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=2)

def build_comparison_summary(previous_entry, current_entry):
    if not previous_entry:
        return []

    summary = []
    prev_title = previous_entry.get("title", "PR anterior")
    prev_number = previous_entry.get("number")
    prev_label = f"#{prev_number} - {prev_title}" if prev_number else prev_title
    summary.append(f"PR anterior: {prev_label}")

    prev_files = previous_entry.get("files_changed", 0)
    prev_added = previous_entry.get("lines_added", 0)
    prev_removed = previous_entry.get("lines_removed", 0)
    summary.append(f"Archivos modificados: {prev_files} -> {current_entry.get('files_changed', 0)}")
    summary.append(f"Lineas agregadas: {prev_added} -> {current_entry.get('lines_added', 0)}")
    summary.append(f"Lineas eliminadas: {prev_removed} -> {current_entry.get('lines_removed', 0)}")

    prev_methods = set(previous_entry.get("new_methods", []))
    curr_methods = set(current_entry.get("new_methods", []))
    added_methods = sorted(curr_methods - prev_methods)
    removed_methods = sorted(prev_methods - curr_methods)
    if added_methods:
        summary.append("Nuevos metodos vs anterior: " + ", ".join(added_methods))
    if removed_methods:
        summary.append("Metodos ya no presentes: " + ", ".join(removed_methods))

    return summary

def extract_added_methods(diff_content):
    """Extrae métodos/funciones agregados del diff"""
    added_methods = []
    lines = diff_content.split('\n')
    
    for line in lines:
        if line.startswith('+') and not line.startswith('+++'):
            # Java methods
            if 'public' in line and '(' in line and ')' in line:
                signature = line[1:].strip()
                method_name = signature.split('(')[0].strip()
                if method_name:
                    method_name = method_name.split()[-1]
                    params = signature.split('(')[1].split(')')[0].strip()
                    added_methods.append({
                        'lang': 'java',
                        'name': method_name,
                        'params': params,
                        'description': "Método agregado en Java"
                    })
            # Python methods
            elif line.strip().startswith('+ def ') or line.strip().startswith('+def '):
                signature = line[1:].strip()
                if 'def ' in signature:
                    method_name = signature.split('def ')[1].split('(')[0].strip()
                    params = signature.split('(')[1].split(')')[0].strip()
                    added_methods.append({
                        'lang': 'python',
                        'name': method_name,
                        'params': params,
                        'description': "Función agregada en Python"
                    })
    
    return added_methods

def generate_mermaid_diagram(files, added_methods, has_new_feature, has_fix, has_refactor, diff_content):
    """Genera un diagrama Mermaid específico basado en los cambios"""
    
    # Detectar tipo de archivos modificados
    has_java = any('.java' in f for f in files)
    has_python = any('.py' in f for f in files)
    has_config = any(f.endswith(('.yml', '.yaml', '.json', '.xml')) for f in files)
    has_docs_files = any(f.endswith('.md') for f in files)
    
    # Si hay código Java/Python con métodos nuevos, generar diagrama de secuencia
    if (has_java or has_python) and added_methods:
        diagram = "```mermaid\nsequenceDiagram\n"
        diagram += "    actor User as 👤 Usuario\n"
        
        if has_java:
            diagram += "    participant Calc as 📊 Calculadora\n"
        else:
            diagram += "    participant App as 🐍 Aplicación\n"
        
        diagram += "\n"
        
        # Agregar llamadas para cada método nuevo
        for i, method_info in enumerate(added_methods[:5], 1):  # Limitar a 5 métodos
            method = method_info['name']
            clean_method = method.replace('_', ' ').title()
            if has_java:
                diagram += f"    User->>Calc: {i}. Llama {clean_method}\n"
                diagram += f"    activate Calc\n"
                diagram += f"    Calc->>Calc: Ejecuta {method}()\n"
                diagram += f"    Calc-->>User: Retorna resultado\n"
                diagram += f"    deactivate Calc\n"
            else:
                diagram += f"    User->>App: {i}. Usa {clean_method}\n"
                diagram += f"    activate App\n"
                diagram += f"    App->>App: Procesa {method}()\n"
                diagram += f"    App-->>User: Devuelve resultado\n"
                diagram += f"    deactivate App\n"
        
        diagram += "\n    Note over User"
        if has_java:
            diagram += ",Calc"
        else:
            diagram += ",App"
        diagram += f": ✨ {len(added_methods)} nuevos métodos agregados\n"
        diagram += "```"
        return diagram
    
    # Si son cambios de configuración/workflow
    elif has_config and not has_java and not has_python:
        diagram = "```mermaid\ngraph TB\n"
        diagram += "    A[⚙️ Configuración Original] -->|Modificar| B[Archivos Config]\n"
        for f in files[:3]:
            file_name = f.split('/')[-1]
            diagram += f"    B --> C{i}[📝 {file_name}]\n"
        diagram += "    B --> D[✅ Config Actualizada]\n"
        diagram += "```"
        return diagram
    
    # Si son solo docs
    elif has_docs_files and not has_java and not has_python:
        diagram = "```mermaid\ngraph LR\n"
        diagram += "    A[📚 Docs Antiguas] -->|Actualizar| B[Cambios]\n"
        if has_new_feature:
            diagram += "    B --> C[✨ Nuevas secciones]\n"
        if has_fix:
            diagram += "    B --> D[🔧 Correcciones]\n"
        diagram += "    B --> E[📖 Docs Actualizadas]\n"
        diagram += "```"
        return diagram
    
    # Diagrama genérico para otros casos
    else:
        return None

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
    
    # Extraer métodos agregados
    print("🔎 Analizando métodos/funciones agregados...")
    added_methods = extract_added_methods(diff_content)
    if added_methods:
        print(f"✅ Métodos detectados: {len(added_methods)}")
        for method_info in added_methods:
            print(f"   - {method_info['lang']}: {method_info['name']}({method_info['params']})")

    # Contexto del PR e historico
    pr_context = load_pr_context()
    history_dir, history_index_path, history_latest_path = get_history_paths()
    history_index = load_history_index(history_index_path)
    previous_entry = history_index.get("entries", [])[-1] if history_index.get("entries") else None
    
    # Generar diagrama Mermaid específico
    print("📊 Generando diagrama Mermaid de cambios...")
    mermaid_diagram = generate_mermaid_diagram(
        files, 
        added_methods, 
        has_new_feature, 
        has_fix, 
        has_refactor, 
        diff_content
    )
    if mermaid_diagram:
        print("✅ Diagrama generado exitosamente")
    else:
        print("ℹ️  Usando diagrama genérico")
    
    # Cargar plantilla Jinja2
    print("📄 Cargando plantilla pr_template.md...")
    template_path = Path(__file__).parent / 'pr_template.md'
    
    if not template_path.exists():
        raise FileNotFoundError(f"No se encontró la plantilla: {template_path}")
    
    with open(template_path, 'r', encoding='utf-8') as f:
        template_content = f.read()
    
    print("✅ Plantilla cargada exitosamente")
    
    # Preparar lista de archivos modificados
    changed_files_details = [f for f in set(files)]
    
    # Detalles adicionales de cambios
    code_changes_detail = []
    if files_changed > 0:
        code_changes_detail.append(f"Archivos tocados: {files_changed}")
    if lines_added > 0:
        code_changes_detail.append(f"Se agregaron {lines_added} líneas nuevas")
    if lines_removed > 0:
        code_changes_detail.append(f"Se eliminaron {lines_removed} líneas")
    if added_methods:
        code_changes_detail.append(f"Se agregaron {len(added_methods)} nuevos métodos/funciones")
    
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
        'has_refactor': has_refactor,
        'mermaid_diagram': mermaid_diagram,
        'changed_files_details': changed_files_details,
        'new_methods': added_methods,
        'code_changes_detail': code_changes_detail
    }
    
    # Renderizar plantilla con Jinja2
    print("🎨 Renderizando documentación con Jinja2...")
    template = Template(template_content)
    
    current_entry = {
        "number": pr_context.get("number"),
        "title": pr_context.get("title"),
        "url": pr_context.get("url"),
        "repo": pr_context.get("repo"),
        "created_at": datetime.utcnow().isoformat() + "Z",
        "files_changed": files_changed,
        "lines_added": lines_added,
        "lines_removed": lines_removed,
        "new_methods": [m["name"] for m in added_methods],
        "changed_files": changed_files_details
    }
    comparison_summary = build_comparison_summary(previous_entry, current_entry)
    template_data["comparison_summary"] = comparison_summary
    template_data["pr_context"] = pr_context

    documentation = template.render(**template_data)
    print("✅ Documentación renderizada exitosamente")

    # Guardar historico si ya existe pr_documentation.md o si hay un PR real
    existing_doc = Path("pr_documentation.md")
    if existing_doc.exists() or pr_context.get("number"):
        history_dir.mkdir(parents=True, exist_ok=True)
        safe_title = slugify(pr_context.get("title"))
        pr_number = pr_context.get("number") or "local"
        history_file = history_dir / f"PR-{pr_number}-{safe_title}.md"
        with open(history_file, "w", encoding="utf-8") as f:
            f.write(documentation)
        with open(history_latest_path, "w", encoding="utf-8") as f:
            f.write(documentation)

        history_index.setdefault("entries", []).append(current_entry)
        save_history_index(history_index_path, history_index)
    
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