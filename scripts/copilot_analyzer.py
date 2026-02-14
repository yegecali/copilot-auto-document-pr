# scripts/copilot_analyzer.py
import argparse
import json
import os
from pathlib import Path


def load_env():
    """Carga variables de entorno desde .env si existe"""
    env_path = Path(__file__).parent / ".env"
    if env_path.exists():
        with open(env_path, "r", encoding="utf-8") as f:
            for line in f:
                line = line.strip()
                if line and not line.startswith("#") and "=" in line:
                    key, value = line.split("=", 1)
                    os.environ[key.strip()] = value.strip()


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


def extract_added_methods(diff_content):
    """Extrae metodos/funciones agregados del diff"""
    added_methods = []
    lines = diff_content.split("\n")

    for line in lines:
        if line.startswith("+") and not line.startswith("+++"):
            if "public" in line and "(" in line and ")" in line:
                signature = line[1:].strip()
                method_name = signature.split("(")[0].strip()
                if method_name:
                    method_name = method_name.split()[-1]
                    params = signature.split("(")[1].split(")")[0].strip()
                    added_methods.append({
                        "lang": "java",
                        "name": method_name,
                        "params": params,
                        "description": "Metodo agregado en Java"
                    })
            elif line.strip().startswith("+ def ") or line.strip().startswith("+def "):
                signature = line[1:].strip()
                if "def " in signature:
                    method_name = signature.split("def ")[1].split("(")[0].strip()
                    params = signature.split("(")[1].split(")")[0].strip()
                    added_methods.append({
                        "lang": "python",
                        "name": method_name,
                        "params": params,
                        "description": "Funcion agregada en Python"
                    })

    return added_methods


def generate_mermaid_diagram(files, added_methods, has_new_feature, has_fix, has_refactor):
    """Genera un diagrama Mermaid especifico basado en los cambios"""
    has_java = any(".java" in f for f in files)
    has_python = any(".py" in f for f in files)
    has_config = any(f.endswith((".yml", ".yaml", ".json", ".xml")) for f in files)
    has_docs_files = any(f.endswith(".md") for f in files)

    if (has_java or has_python) and added_methods:
        diagram = "```mermaid\nsequenceDiagram\n"
        diagram += "    actor User as Usuario\n"

        if has_java:
            diagram += "    participant Calc as Calculadora\n"
        else:
            diagram += "    participant App as Aplicacion\n"

        diagram += "\n"

        for i, method_info in enumerate(added_methods[:5], 1):
            method = method_info["name"]
            clean_method = method.replace("_", " ").title()
            if has_java:
                diagram += f"    User->>Calc: {i}. Llama {clean_method}\n"
                diagram += "    activate Calc\n"
                diagram += f"    Calc->>Calc: Ejecuta {method}()\n"
                diagram += "    Calc-->>User: Retorna resultado\n"
                diagram += "    deactivate Calc\n"
            else:
                diagram += f"    User->>App: {i}. Usa {clean_method}\n"
                diagram += "    activate App\n"
                diagram += f"    App->>App: Procesa {method}()\n"
                diagram += "    App-->>User: Devuelve resultado\n"
                diagram += "    deactivate App\n"

        diagram += "\n    Note over User"
        diagram += ",Calc" if has_java else ",App"
        diagram += f": {len(added_methods)} nuevos metodos agregados\n"
        diagram += "```"
        return diagram

    if has_config and not has_java and not has_python:
        diagram = "```mermaid\ngraph TB\n"
        diagram += "    A[Configuracion Original] -->|Modificar| B[Archivos Config]\n"
        diagram += "    B --> C[Configuracion Actualizada]\n"
        diagram += "```"
        return diagram

    if has_docs_files and not has_java and not has_python:
        diagram = "```mermaid\ngraph LR\n"
        diagram += "    A[Docs Antiguas] -->|Actualizar| B[Cambios]\n"
        if has_new_feature:
            diagram += "    B --> C[Nuevas secciones]\n"
        if has_fix:
            diagram += "    B --> D[Correcciones]\n"
        if has_refactor:
            diagram += "    B --> E[Optimizaciones]\n"
        diagram += "    B --> F[Docs Actualizadas]\n"
        diagram += "```"
        return diagram

    return None


def load_mermaid_from_copilot(base_dir):
    """Carga diagrama Mermaid generado por Copilot desde archivo"""
    mermaid_path = os.getenv("COPILOT_MERMAID_PATH") or "copilot_mermaid.md"
    mermaid_file = Path(mermaid_path)
    if not mermaid_file.is_absolute():
        mermaid_file = base_dir / mermaid_file
    if mermaid_file.exists():
        with open(mermaid_file, "r", encoding="utf-8") as f:
            return f.read().strip()
    return ""


def analyze_pr(diff_content, readme_content):
    """Analiza cambios del PR y retorna datos para plantilla"""
    print("🔍 Analizando cambios del PR...")
    print(f"📄 Tamano del diff: {len(diff_content)} caracteres")

    lines_added = len([l for l in diff_content.split("\n") if l.startswith("+") and not l.startswith("+++")])
    lines_removed = len([l for l in diff_content.split("\n") if l.startswith("-") and not l.startswith("---")])

    files = []
    for line in diff_content.split("\n"):
        if line.startswith("+++"):
            parts = line.split()
            if len(parts) >= 2:
                file_path = parts[1].replace("b/", "") if parts[1].startswith("b/") else parts[1]
                files.append(file_path)
                print(f"  📁 Archivo detectado: {file_path}")

    files_changed = len(set(files))
    print(f"✅ Archivos unicos modificados: {files_changed}")
    print(f"➕ Lineas agregadas: {lines_added}")
    print(f"➖ Lineas eliminadas: {lines_removed}")

    has_new_feature = any(word in diff_content.lower() for word in ["new", "add", "feature", "implement"])
    has_fix = any(word in diff_content.lower() for word in ["fix", "bug", "error", "issue"])
    has_docs = any(word in diff_content.lower() for word in ["readme", "doc", "documentation"])
    has_refactor = any(word in diff_content.lower() for word in ["refactor", "improve", "optimize"])

    summary_parts = []
    changes_list = []

    if has_new_feature:
        summary_parts.append("nuevas funcionalidades")
        changes_list.append("Nueva funcionalidad agregada")
    if has_fix:
        summary_parts.append("correcciones de errores")
        changes_list.append("Correccion de bugs")
    if has_docs:
        summary_parts.append("mejoras en documentacion")
        changes_list.append("Actualizacion de documentacion")
    if has_refactor:
        summary_parts.append("refactorizacion de codigo")
        changes_list.append("Refactorizacion y optimizaciones")

    if not summary_parts:
        summary_parts = ["cambios generales en el codigo"]
        changes_list = ["Cambios generales"]

    added_methods = extract_added_methods(diff_content)
    if added_methods:
        print(f"✅ Metodos detectados: {len(added_methods)}")

    pr_context = load_pr_context()

    base_dir = Path(__file__).resolve().parent.parent
    mermaid_diagram = load_mermaid_from_copilot(base_dir)

    changed_files_details = [f for f in set(files)]

    code_changes_detail = []
    if files_changed > 0:
        code_changes_detail.append(f"Archivos tocados: {files_changed}")
    if lines_added > 0:
        code_changes_detail.append(f"Se agregaron {lines_added} lineas nuevas")
    if lines_removed > 0:
        code_changes_detail.append(f"Se eliminaron {lines_removed} lineas")
    if added_methods:
        code_changes_detail.append(f"Se agregaron {len(added_methods)} nuevos metodos/funciones")

    return {
        "summary_description": ", ".join(summary_parts),
        "files_changed": files_changed,
        "lines_added": lines_added,
        "lines_removed": lines_removed,
        "changes_list": changes_list,
        "has_new_feature": has_new_feature,
        "has_fix": has_fix,
        "has_docs": has_docs,
        "has_refactor": has_refactor,
        "mermaid_diagram": mermaid_diagram,
        "changed_files_details": changed_files_details,
        "new_methods": added_methods,
        "code_changes_detail": code_changes_detail,
        "pr_context": pr_context
    }


def resolve_readme(base_dir, readme_path=None):
    if readme_path:
        candidate = Path(readme_path)
        if not candidate.is_absolute():
            candidate = base_dir / candidate
        if not candidate.exists():
            raise FileNotFoundError(f"No se encontro README: {candidate}")
        return candidate

    readme_variants = ["README.md", "README.MD", "readme.md", "Readme.md"]
    for variant in readme_variants:
        candidate = base_dir / variant
        if candidate.exists():
            print(f"✅ README encontrado: {variant}")
            return candidate

    raise FileNotFoundError("No se encontro ningun README")


def run_analyzer(diff_path=None, readme_path=None, output_path=None):
    load_env()
    base_dir = Path(__file__).resolve().parent.parent
    diff_path = Path(diff_path) if diff_path else base_dir / "changes.diff"
    output_path = Path(output_path) if output_path else base_dir / "pr_context.json"

    if not diff_path.is_absolute():
        diff_path = base_dir / diff_path

    print("📖 Leyendo changes.diff...")
    with open(diff_path, "r", encoding="utf-8") as f:
        diff_content = f.read()

    readme_resolved = resolve_readme(base_dir, readme_path)
    with open(readme_resolved, "r", encoding="utf-8") as f:
        readme_content = f.read()

    analysis = analyze_pr(diff_content, readme_content)

    output_path.parent.mkdir(parents=True, exist_ok=True)
    with open(output_path, "w", encoding="utf-8") as f:
        json.dump(analysis, f, ensure_ascii=False, indent=2)

    print(f"✅ Contexto guardado en {output_path}")
    return str(output_path)


def main():
    parser = argparse.ArgumentParser(description="Analiza cambios y genera pr_context.json")
    parser.add_argument("--diff", dest="diff_path", help="Ruta del archivo diff")
    parser.add_argument("--readme", dest="readme_path", help="Ruta del README")
    parser.add_argument("--context", dest="output_path", help="Ruta de salida del JSON")
    args = parser.parse_args()

    run_analyzer(
        diff_path=args.diff_path,
        readme_path=args.readme_path,
        output_path=args.output_path
    )


if __name__ == "__main__":
    main()
