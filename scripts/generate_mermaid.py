#!/usr/bin/env python3
"""
Script que usa GitHub Copilot (via CLI o subprocess) para generar diagrama Mermaid
basado en el diff del PR.
"""
import argparse
import json
import os
import subprocess
import tempfile
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
        print(f"Comando: gh copilot (stdin)")
        print(f"\nPrompt enviado ({len(prompt)} caracteres):")
        print("-" * 60)
        print(prompt)
        print("-" * 60)
        
        # Configurar variables de entorno para autenticación
        env = os.environ.copy()
        if "GITHUB_TOKEN" in env and "COPILOT_GITHUB_TOKEN" not in env:
            env["COPILOT_GITHUB_TOKEN"] = env["GITHUB_TOKEN"]
            print("🔑 Usando GITHUB_TOKEN para autenticación")
        if "GH_TOKEN" not in env and "GITHUB_TOKEN" in env:
            env["GH_TOKEN"] = env["GITHUB_TOKEN"]

        # Crear archivo temporal con el prompt
        with tempfile.NamedTemporaryFile(mode='w', delete=False, suffix='.txt') as tmp:
            tmp.write(prompt)
            tmp_path = tmp.name
        
        try:
            # Intentar diferentes sintaxis del Copilot CLI
            commands_to_try = [
                # Método 1: cat + pipe
                ["sh", "-c", f"cat {tmp_path} | gh copilot suggest"],
                # Método 2: gh copilot con stdin
                ["gh", "copilot", "suggest"],
            ]
            
            result = None
            for i, cmd in enumerate(commands_to_try):
                try:
                    cmd_display = ' '.join(cmd[:3]) if len(cmd) <= 3 else f"{cmd[0]} {cmd[1]} ..."
                    print(f"🔄 Intento {i+1}: {cmd_display}")
                    
                    if i == 0:  # cat + pipe
                        result = subprocess.run(
                            cmd,
                            capture_output=True,
                            text=True,
                            timeout=30,
                            env=env
                        )
                    else:  # stdin directo
                        result = subprocess.run(
                            cmd,
                            input=prompt,
                            capture_output=True,
                            text=True,
                            timeout=30,
                            env=env
                        )
                    
                    if result.returncode == 0:
                        print(f"✅ Comando exitoso")
                        break
                    else:
                        print(f"⚠️  Falló con exit code {result.returncode}")
                except FileNotFoundError:
                    print(f"⚠️  Comando no encontrado: {cmd[0]}")
                    continue
                except Exception as e:
                    print(f"⚠️  Error: {e}")
                    continue
        finally:
            # Limpiar archivo temporal
            if os.path.exists(tmp_path):
                os.unlink(tmp_path)
        
        if result is None:
            raise FileNotFoundError("No se encontró ninguna versión de Copilot CLI")
        
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
                end = output.find("```", start + 10)
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
            if result and result.stderr:
                print(f"STDERR: {result.stderr}")
            print("="*60 + "\n")
            
    except (subprocess.CalledProcessError, FileNotFoundError, subprocess.TimeoutExpired) as e:
        print(f"\n❌ EXCEPCIÓN AL LLAMAR COPILOT CLI")
        print(f"Error: {type(e).__name__}: {e}")
        print("="*60)
        print("\n💡 SOLUCIONES:")
        print("  1. Instala GitHub Copilot CLI:")
        print("     gh extension install github/gh-copilot")
        print("  2. O instala el CLI standalone:")
        print("     npm install -g @githubnext/github-copilot-cli")
        print("  3. Verifica que esté autenticado:")
        print("     gh auth status")
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
                if filename and filename != "/dev/null":
                    files.append(filename)
                    print(f"  📄 Archivo detectado: {filename}")
        elif line.startswith("+") and not line.startswith("+++"):
            # Detectar métodos Java
            if "public" in line and "(" in line and not "{" in line[:line.find("(")]:
                try:
                    method_part = line.split("(")[0].strip()
                    method_name = method_part.split()[-1]
                    # Filtrar nombres válidos: alfanuméricos, guiones bajos
                    if method_name and len(method_name) < 50 and method_name.replace("_", "").isalnum():
                        methods.append(method_name)
                        print(f"  ⚙️  Método Java detectado: {method_name}()")
                except:
                    pass
            # Detectar funciones Python
            elif "def " in line and "(" in line:
                try:
                    # Remover el + del diff y espacios
                    clean_line = line.lstrip("+").strip()
                    if clean_line.startswith("def "):
                        func_part = clean_line.split("(")[0].strip()
                        func_name = func_part.replace("def ", "").strip()
                        # Filtrar nombres válidos
                        if func_name and len(func_name) < 50 and func_name.replace("_", "").isalnum():
                            methods.append(func_name)
                            print(f"  🐍 Función Python detectada: {func_name}()")
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
