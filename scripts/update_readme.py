# scripts/update_readme.py
import os
import re
from datetime import datetime
from pathlib import Path

def find_readme():
    """Busca el archivo README en diferentes variantes"""
    readme_variants = ['README.md', 'README.MD', 'readme.md', 'Readme.md']
    for variant in readme_variants:
        if Path(variant).exists():
            return variant
    raise FileNotFoundError("No se encontró ningún archivo README (README.md, README.MD, readme.md)")

def update_readme_with_pr_docs():
    """
    Actualiza el README con la documentación generada por el PR
    """
    # Buscar README
    readme_path = find_readme()
    print(f"📄 README encontrado: {readme_path}")
    
    # Leer documentación generada
    if not Path('pr_documentation.md').exists():
        print("⚠️  No se encontró pr_documentation.md, no hay nada que actualizar")
        return
    
    with open('pr_documentation.md', 'r', encoding='utf-8') as f:
        pr_docs = f.read()
    
    # Leer README actual
    with open(readme_path, 'r', encoding='utf-8') as f:
        readme_content = f.read()
    
    # Preparar sección de changelog
    today = datetime.now().strftime('%Y-%m-%d')
    changelog_section = f"""
## 📝 Recent Changes

### Update - {today}

{pr_docs}

---

"""
    
    # Verificar si existe la sección "Recent Changes"
    if '## 📝 Recent Changes' in readme_content or '## Recent Changes' in readme_content:
        # Insertar después del título de Recent Changes
        pattern = r'(##\s*📝?\s*Recent Changes\s*\n)'
        updated_content = re.sub(
            pattern,
            f'\\1\n### Update - {today}\n\n{pr_docs}\n\n---\n\n',
            readme_content,
            count=1
        )
    else:
        # Agregar la sección al final del README
        updated_content = readme_content.rstrip() + '\n\n' + changelog_section
    
    # Guardar README actualizado
    with open(readme_path, 'w', encoding='utf-8') as f:
        f.write(updated_content)
    
    print(f"✅ {readme_path} actualizado exitosamente")
    print(f"📊 Documentación del PR agregada en la sección 'Recent Changes'")

if __name__ == "__main__":
    try:
        update_readme_with_pr_docs()
    except Exception as e:
        print(f"❌ Error: {e}")
        import sys
        sys.exit(1)
