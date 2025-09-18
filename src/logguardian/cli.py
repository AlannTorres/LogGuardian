import argparse
import os
import pandas as pd
from .normalizer import normalize_log
from .analysis import run_analysis
from .report_generator import export_to_markdown

OUTPUT_DIR = "./output"
MD_OUTPUT_FILE = os.path.join(OUTPUT_DIR, "analysis_report.md")

# ---- Custom Formatter para deixar o help bonito ----
class CustomHelpFormatter(argparse.RawTextHelpFormatter):
    def _format_action(self, action):
        if isinstance(action, argparse._SubParsersAction):
            parts = []
            parts.append("Comandos disponíveis:\n")
            for cmd, sub in action.choices.items():
                usage = sub.usage or cmd
                help_text = sub.description or sub.help or ""
                parts.append(f"    {usage:<35} : {help_text}\n")
            return "".join(parts)
        return super()._format_action(action)

def main():
    parser = argparse.ArgumentParser(
        prog="loguard",
        description="Framework de análise de logs Traefik",
        formatter_class=CustomHelpFormatter
    )
    subparsers = parser.add_subparsers(dest="command", required=True)

    # Subcomando: normalize
    parser_norm = subparsers.add_parser(
        "normalize",
        help="Normaliza logs crus (.log) em CSV",
        description="Normaliza logs crus (.log) em CSV",
        usage="normalize <src = file.log> <out = file.csv>"
    )
    parser_norm.add_argument("src", help="Arquivo de log de entrada (.log)")
    parser_norm.add_argument("out", nargs="?", default="traefik.csv",
                             help="Arquivo CSV de saída (.csv) [padrão: traefik.csv]")

    # Subcomando: analyze
    parser_analyze = subparsers.add_parser(
        "analyze",
        help="Executa análise em CSV normalizado",
        description="Executa análise em CSV normalizado",
        usage="analyze <src = file.csv>"
    )
    parser_analyze.add_argument("src", help="Arquivo CSV normalizado")

    # Subcomando: process
    parser_process = subparsers.add_parser(
        "process",
        help="Executa normalização e análise em sequência",
        description="Executa normalização e análise em sequência",
        usage="process <src = file.log> <out = file.csv>"
    )
    parser_process.add_argument("src", help="Arquivo de log cru (.log)")
    parser_process.add_argument("out", nargs="?", default="traefik.csv",
                                help="Arquivo CSV intermediário de saída (.csv) [padrão: traefik.csv]")

    args = parser.parse_args()

    if args.command == "normalize":
        print("Iniciando normalização...")
        normalize_log(args.src, args.out)
        print("Normalização concluida!.")
        print(f"Log normalizado salvo em: {args.out}")

    elif args.command == "analyze":
        print("Iniciando análise...")
        df = pd.read_csv(args.src)
        print("CSV carregado.")

        results = run_analysis(df)
        if results:
            success = export_to_markdown(results, MD_OUTPUT_FILE)
            if success:
                print(f"Relatório salvo em: {MD_OUTPUT_FILE}")
            else:
                print("Erro ao gerar relatório.")

    elif args.command == "process":
        # 1. Normalizar
        normalize_log(args.src, args.out)
        print(f"Log normalizado salvo em: {args.out}")

        # 2. Analisar
        print("Iniciando análise...")
        df = pd.read_csv(args.out)
        print("CSV carregado.")

        results = run_analysis(df)
        if results:
            success = export_to_markdown(results, MD_OUTPUT_FILE)
            if success:
                print(f"Relatório salvo em: {MD_OUTPUT_FILE}")
            else:
                print("Erro ao gerar relatório.")

if __name__ == "__main__":
    main()
