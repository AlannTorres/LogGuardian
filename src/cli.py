import argparse
import os
import pandas as pd
from normalizer import normalize_log
from analysis import run_analysis
from report_generator import export_to_markdown

OUTPUT_DIR = "./output"
MD_OUTPUT_FILE = os.path.join(OUTPUT_DIR, "analysis_report.md")

def main():
    parser = argparse.ArgumentParser(description="Framework de análise de logs Traefik")
    subparsers = parser.add_subparsers(dest="command", required=True)

    # Subcomando: normalizar
    parser_norm = subparsers.add_parser("normalizado", help="Normalizar log cru em CSV")
    parser_norm.add_argument("src", help="Arquivo de log de entrada")
    parser_norm.add_argument("--out", default="traefik.csv", help="Arquivo CSV de saída")

    # Subcomando: analisar
    parser_analyze = subparsers.add_parser("exec-analisy", help="Rodar análise em CSV normalizado")
    parser_analyze.add_argument("src", help="Arquivo CSV normalizado")

    args = parser.parse_args()

    if args.command == "normalizado":
        normalize_log(args.src, args.out)

    elif args.command == "exec-analisy":
        df = pd.read_csv(args.src)
        results = run_analysis(df)
        if results:
            success = export_to_markdown(results, MD_OUTPUT_FILE)
            if success:
                print(f"📄 Relatório salvo em: {MD_OUTPUT_FILE}")
            else:
                print("❌ Erro ao gerar relatório.")

if __name__ == "__main__":
    main()
