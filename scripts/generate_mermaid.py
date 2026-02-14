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

        print("\n" + "="*60)
        print("📤 ENVIANDO A COPILOT CLI")
        print("="*60)
        print(f"Comando: gh copilot suggest")
        print(f"\nPrompt enviado ({len(prompt)} caracteres):")
        print("-" * 60)
        print(prompt)
        print("-" * 60)

        result = subprocess.run(
            ["gh", "copilot", "suggest"],
            input=prompt,
            capture_output=True,
            text=True,
            timeout=30
        )
        
        print(f"\n📥 RESPUESTA DE COPILOT (exit code: {result.returncode})")
        print("="*60)
        
        if result.returncode == 0 and result.stdout:
            # Extraer bloque mermaid del output
            output = result.stdout
            print(f"\nSTDOUT ({len(output)} caracteres):")
            print("-" * 60)
            print(output)
            print("-" * 60)
            
            if result.stderr:
                print(f"\nSTDERR:")
                print(result.stderr)
            
            print("\n🔍 PROCESANDO RESPUESTA...")
            if "```mermaid" in output:
                print("✅ Encontrado bloque ```mermaid en la respuesta")
                start = output.find("```mermaid")
                end = output.find("""`""", start + 10)
                if end > start:
                    extracted = output[start:end + 3]
                    print(f"✅ Extraído bloque Mermaid ({end - start} caracteres)")
                    print("="*60 + "\n")
                    return extracted
            else:
                print("⚠️  No se encontró bloque ```mermaid, usando respuesta completa")
            print("="*60 + "\n")
            return output
        else:
            print(f"❌ Copilot CLI falló o no retornó output")
            if result.stderr:
                print(f"STDERR: {result.stderr}")
            print("="*60 + "\n")
            
    except (subprocess.CalledProcessError, FileNotFoundError, subprocess.TimeoutExpired) as e:
        print(f"\n❌ EXCEPCIÓN AL LLAMAR COPILOT CLI")
        print(f"Error: {type(e).__name__}: {e}")
        print("="*60 + "\n")
    
    # Fallback: generar diagrama básico
    print("ℹ️  Generando diagrama básico como fallback...")
    return generate_basic_mermaid(diff_content)


def generate_basic_mermaid(diff_content):
    """Genera un diagrama Mermaid básico analizando el diff"""
    print("\n" + "="*60)
    print("🔧 GENERADOR FALLBACK ACTIVADO")
    print("="*60)
    print(f"Analizando diff de {len(diff_content)} caracteres...\n")
    
    lines = diff_content.split("\n")
    files = []
    methods = []
    
    for line in lines:
        if line.startswith("+++"):
            parts = line.split()
            if len(parts) >= 2:
                file_path = parts[1].replace("b/", "")
                filename = file_path.split("/")[-1]
                files.append(filename)
                print(f"  📄 Archivo detectado: {filename}")
        elif line.startswith("+") and not line.startswith("+++"):
            if "public" in line and "(" in line:
                try:
                    method_name = line.split("(")[0].strip().split()[-1]
                    if method_name and len(method_name) < 50:
                        methods.append(method_name)
                        print(f"  ⚙️  Método detectado: {method_name}()")
                except:
                    pass
    
    # Limitar a 5 items
    files = files[:5]
    methods = list(set(methods))[:5]
    
    print(f"\n📊 Resumen: {len(files)} archivos, {len(methods)} métodos únicos")
    print("="*60)
    
    if methods:
        print("\n🎨 Generando sequenceDiagram con métodos detectados...")
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
        print(f"✅ Diagrama sequenceDiagram generado ({len(diagram)} caracteres)")
        print("="*60 + "\n")
        return diagram
    
    # Diagrama genérico de archivos
    print("\n🎨 Generando graph LR con archivos detectados...")
    diagram = "```mermaid\ngraph LR\n"
    diagram += "    A[🔄 PR Changes] --> B[Archivos Modificados]\n"
    
    for i, file in enumerate(files, 1):
        diagram += f"    B --> C{i}[📄 {file}]\n"
    
    diagram += "```"
    print(f"✅ Diagrama graph LR generado ({len(diagram)} caracteres)")
    print("="*60 + "\n")
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
    
    print("\n" + "="*60)
    print("🎨 INICIANDO GENERADOR DE DIAGRAMAS MERMAID")
    print("="*60)
    print(f"Diff input: {diff_path}")
    print(f"Output: {output_path}")
    
    if not diff_path.exists():
        print(f"❌ No se encontró el archivo diff: {diff_path}")
        return 1
    
    diff_content = load_diff(diff_path)
    print(f"✅ Diff cargado: {len(diff_content)} caracteres, {len(diff_content.splitlines())} líneas")
    
    mermaid_diagram = generate_mermaid_with_copilot(diff_content)
    
    output_path.parent.mkdir(parents=True, exist_ok=True)
    with open(output_path, "w", encoding="utf-8") as f:
        f.write(mermaid_diagram)
    
    print("\n" + "="*60)
    print("💾 GUARDANDO RESULTADO")
    print("="*60)
    print(f"✅ Archivo guardado: {output_path}")
    print(f"📏 Tamaño: {len(mermaid_diagram)} caracteres")
    print("\n--- Preview del diagrama generado ---")
    print(mermaid_diagram[:500] + ("..." if len(mermaid_diagram) > 500 else ""))
    print("---")
    print("="*60)
    
    return 0


if __name__ == "__main__":
    exit(main())
