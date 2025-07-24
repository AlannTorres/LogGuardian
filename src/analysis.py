import pandas as pd
import numpy as np
import os
import re
import matplotlib.pyplot as plt
import seaborn as sns
import requests
import json
import time
from collections import Counter

# --- Configurações Globais ---
OUTPUT_DIR = "./output"
PLOT_DIR = os.path.join(OUTPUT_DIR, "plots")

# Cache para geolocalização de IP
IP_GEOLOCATION_CACHE = {}
CACHE_FILE = os.path.join(OUTPUT_DIR, "ip_geolocation_cache.json")

# Configurações para a API de geolocalização
API_URL = "http://ip-api.com/json/"
API_FIELDS = "status,country,regionName,city"
MAX_RETRIES = 3
RETRY_DELAY = 1 # seconds

def ensure_dir(directory):
    """Garante que um diretório exista, criando-o se necessário."""
    os.makedirs(directory, exist_ok=True)

def load_cache():
    """Carrega o cache de geolocalização de um arquivo."""
    ensure_dir(OUTPUT_DIR)
    if os.path.exists(CACHE_FILE):
        with open(CACHE_FILE, 'r', encoding='utf-8') as f:
            try:
                return json.load(f)
            except json.JSONDecodeError:
                print(f"Erro ao decodificar o cache JSON em {CACHE_FILE}. Criando um novo cache.")
                return {}
    return {}

def save_cache(cache_data):
    """Salva o cache de geolocalização em um arquivo."""
    ensure_dir(OUTPUT_DIR)
    with open(CACHE_FILE, 'w', encoding='utf-8') as f:
        json.dump(cache_data, f, ensure_ascii=False, indent=4)

# Carrega o cache ao iniciar
IP_GEOLOCATION_CACHE = load_cache()

def load_data(df):
    """Realiza o pré-processamento inicial do DataFrame."""
    print("Pré-processando dados...")
    df["data1"] = pd.to_datetime(df["data1"])
    df["hora"] = df["data1"].dt.hour
    df["dia_semana"] = df["data1"].dt.day_name()
    df["mes"] = df["data1"].dt.month_name()
    print("Dados pré-processados.")
    return df

def get_geolocation(ip):
    """Obtém a geolocalização de um endereço IP usando a API ip-api.com, com cache e retries."""
    if ip in IP_GEOLOCATION_CACHE:
        return IP_GEOLOCATION_CACHE[ip]

    for attempt in range(MAX_RETRIES):
        try:
            response = requests.get(f"{API_URL}{ip}?fields={API_FIELDS}", timeout=5) # Adicionado timeout
            data = response.json()
            if data and data.get("status") == "success":
                result = {
                    "country": data.get("country", "Desconhecido"),
                    "region": data.get("regionName", "Desconhecido"),
                    "city": data.get("city", "Desconhecido")
                }
                IP_GEOLOCATION_CACHE[ip] = result
                return result
        except requests.exceptions.RequestException as e:
            print(f"Erro de conexão ao obter geolocalização para {ip} (Tentativa {attempt + 1}/{MAX_RETRIES}): {e}")
        except json.JSONDecodeError:
            print(f"Erro ao decodificar JSON para {ip} (Tentativa {attempt + 1}/{MAX_RETRIES}). Resposta: {response.text[:100]}...")
        except Exception as e:
            print(f"Erro inesperado ao obter geolocalização para {ip} (Tentativa {attempt + 1}/{MAX_RETRIES}): {e}")
        
        if attempt < MAX_RETRIES - 1:
            time.sleep(RETRY_DELAY) # Espera antes de tentar novamente

    # Se todas as tentativas falharem
    result = {"country": "Erro", "region": "Erro", "city": "Erro"}
    IP_GEOLOCATION_CACHE[ip] = result
    return result

def analyze_ip_geolocation(df, top_n=10):
    """Analisa a geolocalização dos top N IPs com status 200 e top N IPs com status 404."""
    if df is None or df.empty or 'ip' not in df.columns or 'status' not in df.columns:
        return {}
    print(f"Analisando geolocalização dos top {top_n} IPs (200 e 404)...")

    # IPs com status 200
    df_200 = df[df['status'] == 200].copy()
    top_ips_200 = df_200['ip'].value_counts().head(top_n).index.tolist()

    # IPs com status 404
    df_404 = df[df['status'] == 404].copy()
    top_ips_404 = df_404['ip'].value_counts().head(top_n).index.tolist()

    # Combina e obtém IPs únicos para geolocalização
    all_ips_to_geo = list(set(top_ips_200 + top_ips_404))

    if not all_ips_to_geo:
        print("Nenhum IP encontrado para geolocalização.")
        return {
            "top_200_ips_geo": {},
            "top_404_ips_geo": {},
            "total_ips_analisados": 0
        }

    # Processa os IPs usando a função com cache
    ip_location_data = {ip: get_geolocation(ip) for ip in all_ips_to_geo}

    # Organiza os resultados para os top 200 IPs
    top_200_ips_geo_results = {}
    for ip in top_ips_200:
        top_200_ips_geo_results[ip] = ip_location_data.get(ip, {"country": "N/A", "region": "N/A", "city": "N/A"})
    
    # Organiza os resultados para os top 404 IPs
    top_404_ips_geo_results = {}
    for ip in top_ips_404:
        top_404_ips_geo_results[ip] = ip_location_data.get(ip, {"country": "N/A", "region": "N/A", "city": "N/A"})

    # Salva o cache após a análise
    save_cache(IP_GEOLOCATION_CACHE)

    print("Análise de geolocalização de IPs concluída.")
    return {
        "top_200_ips_geo": top_200_ips_geo_results,
        "top_404_ips_geo": top_404_ips_geo_results,
        "total_ips_analisados": len(all_ips_to_geo)
    }

def calculate_general_stats(df):
    """Calcula estatísticas gerais do DataFrame."""
    if df is None or df.empty:
        return {}
    print("Calculando estatísticas gerais...")
    data_final = df["data1"].max()
    data_inicial = df["data1"].min()
    periodo_str = f"{data_inicial.strftime('%d/%m/%Y')} - {data_final.strftime('%d/%m/%Y')}"
    delta_dias = (data_final - data_inicial).days
    total_registros = int(df.shape[0])

    stats = {
        "periodo_analisado": periodo_str,
        "duracao_dias": delta_dias,
        "total_registros": total_registros,
        "data_inicio": data_inicial.isoformat(),
        "data_fim": data_final.isoformat()
    }
    print("Estatísticas gerais calculadas.")
    return stats

def analyze_status_codes(df, plot_dir):
    """Analisa a distribuição dos códigos de status HTTP e gera um gráfico."""
    if df is None or df.empty:
        return {}
    print("Analisando códigos de status...")
    contagem_status = df["status"].value_counts().sort_index()
    status_plot_path = os.path.join(plot_dir, "status_distribution.png")

    try:
        plt.figure(figsize=(8, 5))
        bars = plt.bar(contagem_status.index.astype(str), contagem_status.values, color='mediumseagreen', edgecolor='black')
        for bar in bars:
            yval = bar.get_height()
            plt.text(bar.get_x() + bar.get_width()/2, yval + max(1, yval*0.01), f'{int(yval)}', ha='center', va='bottom')
        plt.title('Distribuição de Status HTTP nas Requisições')
        plt.xlabel('Código de Status HTTP')
        plt.ylabel('Quantidade')
        plt.xticks(rotation=0)
        plt.grid(axis='y', linestyle='--', alpha=0.5)
        plt.tight_layout()
        plt.savefig(status_plot_path)
        plt.close()
        print(f"Gráfico de status salvo em: {status_plot_path}")
    except Exception as e:
        print(f"Erro ao gerar gráfico de status: {e}")
        status_plot_path = None

    results = {
        "contagem_status": contagem_status.to_dict(),
        "plot_path": status_plot_path
    }
    print("Análise de códigos de status concluída.")
    return results

def analyze_time_patterns(df, plot_dir):
    """Analisa padrões temporais e gera gráficos de requisições."""
    if df is None or df.empty:
        return {}
    print("Analisando padrões temporais...")
    results = {}

    # Requisições por Hora
    req_hora = df.groupby('hora').size()
    pico_hora = int(req_hora.idxmax())
    results['requisicoes_por_hora'] = req_hora.to_dict()
    results['pico_requisicoes_hora'] = pico_hora
    hora_plot_path = os.path.join(plot_dir, "requests_per_hour.png")
    try:
        plt.figure(figsize=(10, 6))
        req_hora.plot(kind='bar', color='mediumseagreen', edgecolor='black')
        plt.title('Requisições por Hora do Dia (Geral)')
        plt.xlabel('Hora do dia')
        plt.ylabel('Total de Requisições')
        plt.xticks(rotation=0)
        plt.grid(axis='y', linestyle='--', alpha=0.5)
        plt.tight_layout()
        plt.savefig(hora_plot_path)
        plt.close()
        results['plot_path_hora'] = hora_plot_path
        print(f"Gráfico de requisições por hora salvo em: {hora_plot_path}")
    except Exception as e:
        print(f"Erro ao gerar gráfico de requisições por hora: {e}")
        results['plot_path_hora'] = None

    # Requisições por Dia da Semana
    dias_ordem = ["Monday", "Tuesday", "Wednesday", "Thursday", "Friday", "Saturday", "Sunday"]
    req_dia_semana = df.groupby('dia_semana').size().reindex(dias_ordem).fillna(0)
    pico_dia = req_dia_semana.idxmax()
    results['requisicoes_por_dia_semana'] = req_dia_semana.to_dict()
    results['pico_requisicoes_dia'] = pico_dia

    # Histórico de Requisições Diárias
    req_data = df.set_index('data1').resample('D').size()
    results['historico_requisicoes_diarias'] = {d.strftime('%Y-%m-%d'): v for d, v in req_data.items()}
    hist_plot_path = os.path.join(plot_dir, "daily_requests_history.png")
    try:
        plt.figure(figsize=(10, 5))
        plt.plot(req_data.index, req_data.values, linestyle='-', color='mediumseagreen')
        plt.title('Histórico de Requisições Diárias')
        plt.xlabel('Data')
        plt.ylabel('Quantidade de Requisições')
        plt.grid(True, linestyle='--', alpha=0.5)
        plt.xticks(rotation=45)
        plt.tight_layout()
        plt.savefig(hist_plot_path)
        plt.close()
        print(f"Gráfico de histórico diário salvo em: {hist_plot_path}")
    except Exception as e:
        print(f"Erro ao gerar gráfico de histórico diário: {e}")
        results['plot_path_historico'] = None

    # Heatmap Hora/Método
    heatmap_plot_path = os.path.join(plot_dir, "heatmap_hour_method.png")
    try:
        heatmap_data = df.groupby(['hora', 'metodo']).size().unstack().fillna(0)
        plt.figure(figsize=(10, 6))
        sns.heatmap(heatmap_data, cmap='viridis', annot=True, fmt=".0f")
        plt.title('Requisições por Hora e Método HTTP')
        plt.xlabel("Método HTTP")
        plt.ylabel("Hora do Dia")
        plt.tight_layout()
        plt.savefig(heatmap_plot_path)
        plt.close()
        print(f"Heatmap salvo em: {heatmap_plot_path}")
    except Exception as e:
        print(f"Erro ao gerar heatmap: {e}")
        results['plot_path_heatmap'] = None

    print("Análise de padrões temporais concluída.")
    return results

def analyze_resources(df, top_n=10):
    """Analisa os recursos mais e menos acessados."""
    if df is None or df.empty:
        return {}
    print("Analisando acesso a recursos...")
    contagem_recursos = df['recurso'].value_counts()
    mais_acessadas = contagem_recursos.head(top_n)
    menos_acessadas = contagem_recursos.tail(top_n)

    results = {
        f"top_{top_n}_recursos_mais_acessados": mais_acessadas.to_dict(),
        f"top_{top_n}_recursos_menos_acessados": menos_acessadas.to_dict()
    }
    print("Análise de acesso a recursos concluída.")
    return results

def analyze_404_errors(df, plot_dir, top_n=10):
    """Analisa especificamente os erros 404 (Não Encontrado)."""
    if df is None or df.empty:
        return {}
    print("Analisando erros 404...")
    df_404 = df[df['status'] == 404].copy()
    total_registros_404 = df_404.shape[0]

    if total_registros_404 == 0:
        print("Nenhum erro 404 encontrado.")
        return {"total_erros_404": 0}

    req_hora_404 = df_404.groupby('hora').size()
    pico_hora_404 = int(req_hora_404.idxmax()) if not req_hora_404.empty else None

    dias_ordem = ["Monday", "Tuesday", "Wednesday", "Thursday", "Friday", "Saturday", "Sunday"]
    req_dia_semana_404 = df_404.groupby('dia_semana').size().reindex(dias_ordem).fillna(0)
    pico_dia_404 = req_dia_semana_404.idxmax() if not req_dia_semana_404.empty else None

    contagem_recursos_404 = df_404['recurso'].value_counts()
    mais_acessadas_404 = contagem_recursos_404.head(top_n)
    menos_acessadas_404 = contagem_recursos_404.tail(top_n)

    plot_path_404_hora = os.path.join(plot_dir, "404_requests_per_hour.png")
    try:
        plt.figure(figsize=(10, 6))
        req_hora_404.plot(kind='bar', color='salmon', edgecolor='black')
        plt.title('Requisições com Status 404 por Hora do Dia')
        plt.xlabel('Hora do dia')
        plt.ylabel('Total de Requisições 404')
        plt.xticks(rotation=0)
        plt.grid(axis='y', linestyle='--', alpha=0.5)
        plt.tight_layout()
        plt.savefig(plot_path_404_hora)
        plt.close()
        print(f"Gráfico de 404 por hora salvo em: {plot_path_404_hora}")
    except Exception as e:
        print(f"Erro ao gerar gráfico de 404 por hora: {e}")
        plot_path_404_hora = None

    results = {
        "total_erros_404": total_registros_404,
        "requisicoes_404_por_hora": req_hora_404.to_dict(),
        "pico_404_hora": pico_hora_404,
        "requisicoes_404_por_dia_semana": req_dia_semana_404.to_dict(),
        "pico_404_dia": pico_dia_404,
        f"top_{top_n}_recursos_404_mais_acessados": mais_acessadas_404.to_dict(),
        f"top_{top_n}_recursos_404_menos_acessados": menos_acessadas_404.to_dict(),
        "plot_path_404_hora": plot_path_404_hora
    }
    print("Análise de erros 404 concluída.")
    return results

def detect_anomalies(df, plot_dir):
    """Detecta potenciais anomalias nas requisições com base em um conjunto de regras."""
    if df is None or df.empty:
        return {}, pd.DataFrame()
    print("Detectando anomalias...")

    # 1. Métodos HTTP incomuns
    metodos_incomuns = ['CONNECT', 'PUT', 'PATCH', 'DELETE', 'OPTIONS', 'TRACE']
    df_metodos_anomalos = df[df['metodo'].isin(metodos_incomuns)].copy()
    contagem_metodos_anomalos = df_metodos_anomalos['metodo'].value_counts().to_dict()

    # 2. IPs com muitos erros 404
    df_404 = df[df['status'] == 404]
    ips_com_404 = df_404['ip'].value_counts()
    ips_suspeitos_404 = ips_com_404[ips_com_404 > 5].head(10).to_dict()

    # 3. Tamanho de resposta suspeito (maior que 1MB)
    limite_tamanho = 1 * 1024 * 1024  # 1 MB
    df_tamanho_suspeito = df[df['tamanho'] > limite_tamanho].copy()
    contagem_tamanho_suspeito = df_tamanho_suspeito.shape[0]
    recursos_tamanho_suspeito = df_tamanho_suspeito['recurso'].value_counts().head(10).to_dict()

    # 4. Filtragem e Análise de Padrões em Recursos
    recursos_normais = ["/cppgi/api/editais", "/cppgi/", "/main/", "/pesquisa/", "/favicon.ico"]
    padrao_recursos_normais = '^(?:' + '|'.join(re.escape(r) for r in recursos_normais) + ')'
    df_filtrado = df[~df['recurso'].astype(str).str.match(padrao_recursos_normais, na=False)].copy()

    # Marcadores de anomalias
    padrao_sql = r'(?:\bselect\b|\bunion\b|\bdrop\b|\binsert\b|\bupdate\b|\bdelete\b|[\;\*\'\]-])'
    df_filtrado['suspeita_sql'] = df_filtrado['recurso'].astype(str).str.contains(padrao_sql, flags=re.IGNORECASE, regex=True, na=False)

    padrao_xss = r'(?:<script|alert\(|onerror=|onload=|javascript:|data:|\%3C|\%3E)'
    df_filtrado['suspeita_xss'] = df_filtrado['recurso'].astype(str).str.contains(padrao_xss, flags=re.IGNORECASE, regex=True, na=False)

    padrao_ext = r'\.(?:php|asp|jsp|cgi|pl|exe|dll|sh|bash|py|rb|bak|sql|conf|ini|log|swp|env)(?:[\?#]$)'
    df_filtrado['extensao_incomum'] = df_filtrado['recurso'].astype(str).str.contains(padrao_ext, regex=True, na=False)

    limite_url = df_filtrado['recurso'].astype(str).str.len().quantile(0.98)
    df_filtrado['url_longa'] = df_filtrado['recurso'].astype(str).str.len() > limite_url

    df_filtrado['recurso_404'] = df_filtrado['status'] == 404

    contagem_recursos_filtrados = df_filtrado['recurso'].value_counts()
    limiar_sup = contagem_recursos_filtrados.quantile(0.99)
    limiar_inf = contagem_recursos_filtrados.quantile(0.01)
    recursos_raros = contagem_recursos_filtrados[contagem_recursos_filtrados <= max(1, limiar_inf)].index
    recursos_frequentes_demais = contagem_recursos_filtrados[contagem_recursos_filtrados > limiar_sup].index
    df_filtrado['acesso_incomum'] = df_filtrado['recurso'].isin(recursos_raros) | df_filtrado['recurso'].isin(recursos_frequentes_demais)

    cols_anomalias = ['suspeita_sql', 'suspeita_xss', 'extensao_incomum', 'url_longa', 'recurso_404', 'acesso_incomum']
    df_filtrado['metodo_incomum'] = df_filtrado['metodo'].isin(metodos_incomuns)
    df_filtrado['ip_com_muitos_404'] = df_filtrado['ip'].isin(ips_suspeitos_404.keys())
    df_filtrado['tamanho_resposta_suspeito'] = df_filtrado['tamanho'] > limite_tamanho

    # Novas regras de anomalia
    # 5. Requisições com muitos parâmetros/query strings longas
    # Define um limiar para o número de parâmetros ou comprimento da query string
    # Exemplo: mais de 5 parâmetros ou query string com mais de 100 caracteres
    df_filtrado['query_string_longa'] = df_filtrado['recurso'].astype(str).apply(lambda x: len(x.split('?')[-1]) > 100 if '?' in x else False)
    df_filtrado['muitos_parametros'] = df_filtrado['recurso'].astype(str).apply(lambda x: len(x.split('?')[-1].split('&')) > 5 if '?' in x else False)

    # 6. Picos de requisições por IP em curto período (ex: mais de 10 requisições em 1 segundo)
    # Para uma abordagem simples, podemos identificar IPs com um número muito alto de requisições totais.
    ip_request_counts = df['ip'].value_counts()
    high_request_ip_threshold = ip_request_counts.quantile(0.99) # IPs no top 1% de requisições
    high_request_ips = ip_request_counts[ip_request_counts > high_request_ip_threshold].index
    df_filtrado['ip_alto_volume'] = df_filtrado['ip'].isin(high_request_ips)

    cols_anomalias_todas = cols_anomalias + ['metodo_incomum', 'ip_com_muitos_404', 'tamanho_resposta_suspeito', 
                                            'query_string_longa', 'muitos_parametros', 'ip_alto_volume']

    df_filtrado['anomalia_detectada'] = df_filtrado[cols_anomalias_todas].any(axis=1)
    df_anomalias_final = df_filtrado[df_filtrado['anomalia_detectada']].copy()

    contagem_tipos_anomalia = df_anomalias_final[cols_anomalias_todas].sum().astype(int).to_dict()
    total_anomalias = df_anomalias_final.shape[0]
    total_registros = df.shape[0]
    percentual_anomalias = (total_anomalias / total_registros * 100) if total_registros > 0 else 0

    top_recursos_anomalos = df_anomalias_final['recurso'].value_counts().head(10).to_dict()

    status_anomalias = df_anomalias_final['status'].value_counts().sort_index()
    status_anomalias_pct = (df_anomalias_final['status'].value_counts(normalize=True) * 100).sort_index()

    anomalias_plot_path = os.path.join(plot_dir, "anomaly_types_count.png")
    try:
        anomalias_series = pd.Series(contagem_tipos_anomalia).sort_values(ascending=False)
        plt.figure(figsize=(10, 6))
        bars = anomalias_series.plot(kind='bar', color='coral', edgecolor='black')
        plt.title('Contagem de Tipos de Anomalias Detectadas', fontsize=14, fontweight='bold')
        plt.ylabel('Quantidade de Ocorrências', fontsize=12)
        plt.xlabel('Tipo de Anomalia', fontsize=12)
        plt.xticks(rotation=45, ha='right')
        plt.grid(axis='y', linestyle='--', alpha=0.5)
        for bar in bars.containers[0]:
            height = bar.get_height()
            if height > 0:
                plt.text(bar.get_x() + bar.get_width()/2, height + max(1, height*0.01), f'{int(height)}', ha='center', va='bottom', fontsize=10)
        plt.tight_layout()
        plt.savefig(anomalias_plot_path)
        plt.close()
        print(f"Gráfico de tipos de anomalia salvo em: {anomalias_plot_path}")
    except Exception as e:
        print(f"Erro ao gerar gráfico de tipos de anomalia: {e}")
        anomalias_plot_path = None

    status_anomalias_plot_path = os.path.join(plot_dir, "anomaly_status_distribution_pct.png")
    try:
        plt.figure(figsize=(8, 5))
        bars = plt.bar(status_anomalias_pct.index.astype(str), status_anomalias_pct.values, color='lightcoral', edgecolor='black')
        for bar in bars:
            yval = bar.get_height()
            if yval > 0:
                plt.text(bar.get_x() + bar.get_width()/2, yval + 0.5, f'{yval:.2f}%', ha='center', va='bottom')
        plt.title('Distribuição de Status HTTP nas Requisições Anômalas (%)')
        plt.xlabel('Código de Status HTTP')
        plt.ylabel('Porcentagem')
        plt.ylim(0, 100)
        plt.grid(axis='y', linestyle='--', alpha=0.5)
        plt.tight_layout()
        plt.savefig(status_anomalias_plot_path)
        plt.close()
        print(f"Gráfico de status em anomalias salvo em: {status_anomalias_plot_path}")
    except Exception as e:
        print(f"Erro ao gerar gráfico de status em anomalias: {e}")
        status_anomalias_plot_path = None

    results = {
        "total_requisicoes_analisadas_para_anomalias": df_filtrado.shape[0],
        "total_anomalias_detectadas": total_anomalias,
        "percentual_anomalias": round(percentual_anomalias, 2),
        "contagem_por_tipo_anomalia": contagem_tipos_anomalia,
        "metodos_http_incomuns_detectados": contagem_metodos_anomalos,
        "ips_suspeitos_com_muitos_404": ips_suspeitos_404,
        "requisicoes_tamanho_suspeito": {
            "contagem": contagem_tamanho_suspeito,
            "top_10_recursos": recursos_tamanho_suspeito
        },
        "top_10_recursos_anomalos": top_recursos_anomalos,
        "distribuicao_status_http_anomalias": status_anomalias.to_dict(),
        "distribuicao_status_http_anomalias_percentual": status_anomalias_pct.to_dict(),
        "plot_path_tipos_anomalia": anomalias_plot_path,
        "plot_path_status_anomalias": status_anomalias_plot_path,
        "recursos_query_string_longa": Counter(df_filtrado[df_filtrado['query_string_longa']]['recurso']).most_common(10),
        "recursos_muitos_parametros": Counter(df_filtrado[df_filtrado['muitos_parametros']]['recurso']).most_common(10),
        "ips_alto_volume": Counter(df_filtrado[df_filtrado['ip_alto_volume']]['ip']).most_common(10)
    }
    print("Detecção de anomalias concluída.")
    return results, df_anomalias_final

# --- Função Principal de Análise ---

def run_analysis(df):
    """Orquestra a execução de todas as funções de análise."""
    ensure_dir(OUTPUT_DIR)
    ensure_dir(PLOT_DIR)

    df = load_data(df)

    if df is not None:
        all_results = {}

        all_results['general_stats'] = calculate_general_stats(df)
        all_results['status_codes'] = analyze_status_codes(df, PLOT_DIR)
        all_results['time_patterns'] = analyze_time_patterns(df, PLOT_DIR)
        all_results['resource_analysis'] = analyze_resources(df)
        all_results['404_analysis'] = analyze_404_errors(df, PLOT_DIR)
        
        # A geolocalização agora foca apenas nos IPs com status 404
        ip_geo_results = analyze_ip_geolocation(df)
        all_results['ip_geolocation'] = ip_geo_results # Renomeado para refletir o foco

        anomaly_results, df_anomalies = detect_anomalies(df, PLOT_DIR)
        all_results['anomaly_detection'] = anomaly_results

        print("\n--- Análise Concluída ---")
        return all_results
    else:
        print("Não foi possível carregar os dados. Análise abortada.")
        return None