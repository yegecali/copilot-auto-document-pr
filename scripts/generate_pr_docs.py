# scripts/generate_pr_docs.py
import argparse

from copilot_analyzer import run_analyzer
from generate_docs import run_generator


def main():
    parser = argparse.ArgumentParser(description="Orquesta analisis y generacion de PR docs")
    parser.add_argument("--diff", dest="diff_path", help="Ruta del archivo diff")
    parser.add_argument("--readme", dest="readme_path", help="Ruta del README")
    parser.add_argument("--context", dest="context_path", help="Ruta del JSON de contexto")
    parser.add_argument("--output", dest="output_path", help="Ruta de salida del Markdown")
    parser.add_argument("--template", dest="template_path", help="Ruta de la plantilla")
    args = parser.parse_args()

    context_path = run_analyzer(
        diff_path=args.diff_path,
        readme_path=args.readme_path,
        output_path=args.context_path
    )
    run_generator(
        context_path=context_path,
        output_path=args.output_path,
        template_path=args.template_path
    )


if __name__ == "__main__":
    main()
