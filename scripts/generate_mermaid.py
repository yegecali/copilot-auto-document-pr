#!/usr/bin/env python3
"""
Script que usa GitHub Copilot (via CLI o subprocess) para generar diagrama Mermaid
basado en el diff del PR.
"""
import argparse
import json
import os
import subprocess
from pathlib import Path


def load_diff(diff_path):
    """Lee el archivo diff"""
    with open(diff_path, "r", encoding="utf-8") as f:
        return f.read()


def generate_mermaid_with_copilot(diff_content):
    """
    Genera diagrama Mermaid usando GitHub Copilot CLI o fallback a prompt manual.
    
    Intenta usar `gh copilot` si está disponible, de lo contrario crea un prompt
    básico que el usuario puede pasar a Copilot manualmente.
    """
    # Intentar usar gh copilot CLI
    try:
        prompt = f"""Genera un diagrama de secuencia Mermaid que muestre los cambios realizados en este PR.

Diff del PR:
```
{diff_content[:2000]}  # Limitar tamaño
```

Instrucciones:
- Si hay métodos/funciones nuevos, muestra su flujo de ejecución
- Si hay configuración, muestra el flujo de cambios
- Usa formato sequenceDiagram o graph según corresponda
- Formato: solo el código mermaid dentro de ```mermaid ... ```
"""

        result = subprocess.run(
            ["gh", "copilot", "suggest", "-t", "shell"],
            input=prompt,
            capture_output=True,
            text=True,
            timeout=30
        )
        
        if result.returncode == 0 and result.stdout:
            # Extraer bloque mermaid del output
            output = result.stdout
            if "```mermaid" in output:
                start = output.find("```mermaid")
                end = output.find("```", start + 10)
                if end > start:
                    return output[start:end + 3]
            return output
            
    except (subprocess.CalledProcessError, FileNotFoundError, subprocess.TimeoutExpired) as e:
        print(f"⚠️  No se pudo usar gh copilot CLI: {e}")
    
    # Fallback: generar diagrama básico
    print("ℹ️  Generando diagrama básico como fallback...")
    return generate_basic_mermaid(diff_content)


def generate_basic_mermaid(diff_content):
    """Genera un diagrama Mermaid básico analizando el diff"""
    lines = diff_content.split("\n")
    files = []
    methods = []
    
    for line in lines:
        if line.startswith("+++"):
            parts = line.split()
            if len(parts) >= 2:
                file_path = parts[1].replace("b/", "")
                files.append(file_path.split("/")[-1])
        elif line.startswith("+") and not line.startswith("+++"):
            if "public" in line and "(" in line:
                try:
                    method_name = line.split("(")[0].strip().split()[-1]
                    if method_name and len(method_name) < 50:
                        methods.append(method_name)
                except:
                    pass
    
    # Limitar a 5 items
    files = files[:5]
    methods = list(set(methods))[:5]
    
    if methods:
        diagram = "```mermaid\nsequenceDiagram\n"
        diagram += "    actor User as 👤 Usuario\n"
        diagram += "    participant App as 📱 Aplicación\n\n"
        
        for i, method in enumerate(methods, 1):
            diagram += f"    User->>App: {i}. Llama {method}()\n"
            diagram += "    activate App\n"
            diagram += f"    App->>App: Ejecuta {method}\n"
            diagram += "    App-->>User: Retorna resultado\n"
            diagram += "    deactivate App\n"
        
        diagram += f"\n    Note over User,App: {len(methods)} nuevos métodos agregados\n"
        diagram += "```"
        return diagram
    
    # Diagrama genérico de archivos
    diagram = "```mermaid\ngraph LR\n"
    diagram += "    A[🔄 PR Changes] --> B[Archivos Modificados]\n"
    
    for i, file in enumerate(files, 1):
        diagram += f"    B --> C{i}[📄 {file}]\n"
    
    diagram += "```"
    return diagram


def main():
    parser = argparse.ArgumentParser(description="Genera diagrama Mermaid con Copilot")
    parser.add_argument("--diff", dest="diff_path", default="changes.diff", help="Ruta del diff")
    parser.add_argument("--output", dest="output_path", default="scripts/copilot_mermaid.md", help="Ruta de salida")
    args = parser.parse_args()
    
    base_dir = Path(__file__).resolve().parent.parent
    diff_path = Path(args.diff_path)
    output_path = Path(args.output_path)
    
    if not diff_path.is_absolute():
        diff_path = base_dir / diff_path
    if not output_path.is_absolute():
        output_path = base_dir / output_path
    
    print("🎨 Generando diagrama Mermaid con Copilot...")
    
    if not diff_path.exists():
        print(f"❌ No se encontró el archivo diff: {diff_path}")
        return 1
    
    diff_content = load_diff(diff_path)
    mermaid_diagram = generate_mermaid_with_copilot(diff_content)
    
    output_path.parent.mkdir(parents=True, exist_ok=True)
    with open(output_path, "w", encoding="utf-8") as f:
        f.write(mermaid_diagram)
    
    print(f"✅ Diagrama Mermaid guardado en: {output_path}")
    print("\n--- Preview ---")
    print(mermaid_diagram[:500] + ("..." if len(mermaid_diagram) > 500 else ""))
    print("---")
    
    return 0


if __name__ == "__main__":
    exit(main())
