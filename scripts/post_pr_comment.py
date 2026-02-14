# scripts/post_pr_comment.py
import os
import sys
import requests
from pathlib import Path

def post_pr_comment():
    """
    Publica un comentario en el PR con la documentación generada
    """
    print("🚀 Iniciando publicación de comentario en PR...")
    
    github_token = os.getenv('GITHUB_TOKEN')
    pr_number = os.getenv('PR_NUMBER')
    repo = os.getenv('REPO')
    
    print(f"📋 Variables de entorno:")
    print(f"  - REPO: {repo}")
    print(f"  - PR_NUMBER: {pr_number}")
    print(f"  - GITHUB_TOKEN: {'✓ Configurado' if github_token else '✗ No configurado'}")
    
    if not all([github_token, pr_number, repo]):
        print("❌ Variables de entorno faltantes: GITHUB_TOKEN, PR_NUMBER, REPO")
        sys.exit(1)
    
    # Verificar que existe pr_documentation.md
    print("🔍 Buscando pr_documentation.md...")
    if not Path('pr_documentation.md').exists():
        print("⚠️  No se encontró pr_documentation.md")
        print("📂 Archivos en el directorio actual:")
        for f in Path('.').glob('*'):
            print(f"  - {f.name}")
        sys.exit(0)
    
    print("✓ pr_documentation.md encontrado")
    
    # Leer documentación generada
    print("📖 Leyendo pr_documentation.md...")
    with open('pr_documentation.md', 'r', encoding='utf-8') as f:
        pr_docs = f.read()
    
    print(f"📝 Contenido leído ({len(pr_docs)} caracteres)")
    print("=" * 50)
    print(pr_docs[:300] + "..." if len(pr_docs) > 300 else pr_docs)
    print("=" * 50)
    
    # Preparar comentario
    comment_body = f"""## 🤖 Análisis Automático con GitHub Copilot

{pr_docs}

---
*Generado automáticamente por GitHub Actions con Copilot*
"""
    
    # API de GitHub para comentarios
    url = f"https://api.github.com/repos/{repo}/issues/{pr_number}/comments"
    
    print(f"🌐 Enviando comentario a: {url}")
    
    response = requests.post(
        url,
        headers={
            "Authorization": f"Bearer {github_token}",
            "Accept": "application/vnd.github.v3+json",
            "Content-Type": "application/json"
        },
        json={"body": comment_body}
    )
    
    if response.status_code == 201:
        print(f"✅ Comentario publicado exitosamente en PR #{pr_number}")
        print(f"🔗 URL: {response.json().get('html_url', 'N/A')}")
    else:
        print(f"❌ Error al publicar comentario: {response.status_code}")
        print(f"📝 Respuesta: {response.text}")
        sys.exit(1)

if __name__ == "__main__":
    try:
        post_pr_comment()
    except Exception as e:
        print(f"❌ Error: {e}")
        sys.exit(1)
