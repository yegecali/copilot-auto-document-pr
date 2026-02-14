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
    Usa GitHub Copilot API para analizar cambios
    """
    github_token = os.getenv('GITHUB_TOKEN')
    
    if not github_token:
        raise ValueError("GITHUB_TOKEN no configurada. Por favor, configura tu token de GitHub.")
    
    prompt = f"""
    Analiza los siguientes cambios de un Pull Request y genera:
    1. Un resumen ejecutivo de los cambios
    2. Lista de features/fixes agregados
    3. Impacto en la arquitectura (si aplica)
    4. Sección actualizada para el README.md
    
    README ACTUAL:
    {readme_content}
    
    CAMBIOS DEL PR:
    {diff_content}
    
    Formato de respuesta esperado:
    ## PR Summary
    [resumen]
    
    ## Changes
    - Feature/Fix 1
    - Feature/Fix 2
    
    ## README Update
    [contenido para actualizar el README]
    """
    
    # GitHub Copilot API endpoint
    endpoint = "https://api.github.com/copilot_internal/v2/chat/completions"
    
    response = requests.post(
        endpoint,
        headers={
            "Content-Type": "application/json",
            "Authorization": f"Bearer {github_token}",
            "X-GitHub-Api-Version": "2024-01-01"
        },
        json={
            "messages": [
                {"role": "system", "content": "Eres un arquitecto de software experto en documentación técnica."},
                {"role": "user", "content": prompt}
            ],
            "temperature": 0.3,
            "max_tokens": 2000,
            "model": "gpt-4-turbo"
        }
    )
    
    if response.status_code != 200:
        raise Exception(f"Error en Copilot API: {response.status_code} - {response.text}")
    
    return response.json()['choices'][0]['message']['content']

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