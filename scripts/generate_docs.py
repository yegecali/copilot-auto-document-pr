# scripts/generate_docs.py
import argparse
import json
import re
from datetime import datetime
from pathlib import Path
from jinja2 import Template


def slugify(value):
    """Convierte texto a slug seguro para nombres de archivo"""
    if not value:
        return "pr"
    value = value.lower()
    value = re.sub(r"[^a-z0-9]+", "-", value)
    return value.strip("-") or "pr"


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


def render_documentation(template_path, template_data):
    with open(template_path, "r", encoding="utf-8") as f:
        template_content = f.read()
    template = Template(template_content)
    return template.render(**template_data)


def validate_context(template_data):
    if not isinstance(template_data, dict):
        raise ValueError("El contexto debe ser un objeto JSON")

    required_keys = [
        "summary_description",
        "files_changed",
        "lines_added",
        "lines_removed",
        "changes_list",
        "has_new_feature",
        "has_fix",
        "has_docs",
        "has_refactor",
        "changed_files_details",
        "new_methods",
        "code_changes_detail",
        "pr_context"
    ]

    missing = [key for key in required_keys if key not in template_data]
    if missing:
        raise ValueError(f"Faltan claves requeridas: {', '.join(missing)}")

    if not isinstance(template_data["changes_list"], list):
        raise ValueError("changes_list debe ser una lista")
    if not isinstance(template_data["changed_files_details"], list):
        raise ValueError("changed_files_details debe ser una lista")
    if not isinstance(template_data["new_methods"], list):
        raise ValueError("new_methods debe ser una lista")
    if not isinstance(template_data["code_changes_detail"], list):
        raise ValueError("code_changes_detail debe ser una lista")
    if not isinstance(template_data["pr_context"], dict):
        raise ValueError("pr_context debe ser un objeto")

    int_fields = ["files_changed", "lines_added", "lines_removed"]
    for field in int_fields:
        if not isinstance(template_data[field], int):
            raise ValueError(f"{field} debe ser entero")

    bool_fields = ["has_new_feature", "has_fix", "has_docs", "has_refactor"]
    for field in bool_fields:
        if not isinstance(template_data[field], bool):
            raise ValueError(f"{field} debe ser booleano")


def run_generator(context_path=None, output_path=None, template_path=None):
    base_dir = Path(__file__).resolve().parent.parent
    context_path = Path(context_path) if context_path else base_dir / "pr_context.json"
    output_path = Path(output_path) if output_path else base_dir / "pr_documentation.md"
    template_path = Path(template_path) if template_path else Path(__file__).parent / "pr_template.md"

    if not context_path.exists():
        raise FileNotFoundError(f"No se encontro {context_path}")

    with open(context_path, "r", encoding="utf-8") as f:
        template_data = json.load(f)

    validate_context(template_data)

    if not template_path.exists():
        raise FileNotFoundError(f"No se encontro la plantilla: {template_path}")

    pr_context = template_data.get("pr_context", {})
    added_methods = template_data.get("new_methods", [])
    changed_files_details = template_data.get("changed_files_details", [])

    current_entry = {
        "number": pr_context.get("number"),
        "title": pr_context.get("title"),
        "url": pr_context.get("url"),
        "repo": pr_context.get("repo"),
        "created_at": datetime.utcnow().isoformat() + "Z",
        "files_changed": template_data.get("files_changed", 0),
        "lines_added": template_data.get("lines_added", 0),
        "lines_removed": template_data.get("lines_removed", 0),
        "new_methods": [m.get("name") for m in added_methods if m.get("name")],
        "changed_files": changed_files_details
    }

    history_dir, history_index_path, history_latest_path = get_history_paths()
    history_index = load_history_index(history_index_path)
    previous_entry = history_index.get("entries", [])[-1] if history_index.get("entries") else None

    template_data["comparison_summary"] = build_comparison_summary(previous_entry, current_entry)
    template_data["pr_context"] = pr_context

    documentation = render_documentation(template_path, template_data)

    output_path.parent.mkdir(parents=True, exist_ok=True)
    with open(output_path, "w", encoding="utf-8") as f:
        f.write(documentation)

    existing_doc = output_path.exists()
    if existing_doc or pr_context.get("number"):
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

    print(f"✅ Documentacion generada en {output_path}")
    return str(output_path)


def main():
    parser = argparse.ArgumentParser(description="Genera pr_documentation.md desde pr_context.json")
    parser.add_argument("--context", dest="context_path", help="Ruta del JSON de contexto")
    parser.add_argument("--output", dest="output_path", help="Ruta de salida del Markdown")
    parser.add_argument("--template", dest="template_path", help="Ruta de la plantilla")
    args = parser.parse_args()

    run_generator(
        context_path=args.context_path,
        output_path=args.output_path,
        template_path=args.template_path
    )


if __name__ == "__main__":
    main()
