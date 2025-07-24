#!/usr/bin/env python3
"""
Analisador de Logs Traefik com Geolocalização de IPs
Arquivo principal que integra análise de dados e geração de relatório MD
"""

from kagglehub import KaggleDatasetAdapter
import kagglehub
import os
from analysis import run_analysis
from report_generator import export_to_markdown

# Configurações
OUTPUT_DIR = "./output"
MD_OUTPUT_FILE = os.path.join(OUTPUT_DIR, "analysis_report.md")

def load_data_from_kaggle(dataset_name="rafaelpbmota/sci01-traefik-semanal", csv_filename="traefik.csv"):
    """Carrega os dados do Kaggle."""
    print(f"Baixando dataset '{dataset_name}'...")
    try:
        # Carrega o dataset diretamente como DataFrame
        df = kagglehub.load_dataset(
            KaggleDatasetAdapter.PANDAS,
            dataset_name,
            csv_filename
        )
        print("Dados carregados do Kaggle.")
        return df
    except Exception as e:
        print(f"Erro ao carregar dados: {e}")
        import traceback
        traceback.print_exc()
        return None

def load_data_from_csv(csv_path):
    """Carrega os dados de um arquivo CSV local."""
    import pandas as pd
    try:
        df = pd.read_csv(csv_path)
        print(f"Dados carregados de {csv_path}")
        return df
    except Exception as e:
        print(f"Erro ao carregar dados do CSV: {e}")
        return None

def main():
    """Função principal."""
    print("=== Analisador de Logs Traefik com Geolocalização ===")
    print("Iniciando análise...")
    
    df = load_data_from_kaggle()

    if df is not None:
        print(f"Dataset carregado com {df.shape[0]} registros e {df.shape[1]} colunas.")
        
        # Executar análise
        results = run_analysis(df)
        
        if results:
            # Gerar relatório Markdown
            success = export_to_markdown(results, MD_OUTPUT_FILE)
            
            if success:
                print(f"\n✅ Análise concluída com sucesso!")
                print(f"📄 Relatório salvo em: {MD_OUTPUT_FILE}")
                print(f"📊 Gráficos salvos em: {os.path.join(OUTPUT_DIR, 'plots')}")
                
                # Mostrar resumo dos resultados
                if 'general_stats' in results:
                    gs = results['general_stats']
                    print(f"\n📈 Resumo:")
                    print(f"   • Período: {gs.get('periodo_analisado', 'N/A')}")
                    print(f"   • Total de registros: {gs.get('total_registros', 0):,}")
                
                if 'ip_geolocation' in results and results['ip_geolocation'].get('country_counts'):
                    top_country = max(results['ip_geolocation']['country_counts'].items(), key=lambda x: x[1])
                    print(f"   • País com mais requisições: {top_country[0]} ({top_country[1]:,})")
                
                if 'anomaly_detection' in results:
                    anomaly_pct = results['anomaly_detection'].get('percentual_anomalias', 0)
                    print(f"   • Requisições anômalas: {anomaly_pct:.2f}%")
            else:
                print("❌ Erro ao gerar relatório Markdown.")
        else:
            print("❌ Erro durante a análise dos dados.")
    else:
        print("❌ Não foi possível carregar os dados. Análise abortada.")

if __name__ == "__main__":
    main()