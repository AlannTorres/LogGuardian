import os
import datetime
from collections import Counter

def ensure_dir(directory):
    """Garante que um diretório exista."""
    os.makedirs(directory, exist_ok=True)

def format_dict_for_md(data_dict, indent=0):
    """Formata um dicionário para Markdown, tratando sub-dicionários."""
    md_string = ""
    prefix = "  " * indent
    for key, value in data_dict.items():
        if isinstance(value, dict):
            md_string += f"{prefix}- **{key}:**\n"
            md_string += format_dict_for_md(value, indent + 1)
        elif isinstance(value, list):
            md_string += f"{prefix}- **{key}:**\n"
            for item in value:
                 md_string += f"{prefix}  - {item}\n"
        else:
            md_string += f"{prefix}- **{key}:** {value}\n"
    return md_string

def export_to_markdown(data, output_file):
    """Gera um relatório Markdown estruturado com os resultados da análise.

    Args:
        data (dict): Dicionário contendo todos os resultados da análise.
        output_file (str): Caminho completo para o arquivo Markdown de saída.
    """
    print(f"Gerando relatório Markdown: {output_file}")
    ensure_dir(os.path.dirname(output_file))
    md_content = f"# Relatório de Análise de Logs Traefik\n\n"
    
    now = datetime.datetime.now()
    date_str = now.strftime("%d/%m/%Y %H:%M:%S")
    md_content += f"**Data de Geração:** {date_str}\n\n"
    
    md_content += "Este relatório apresenta uma análise detalhada dos logs do Traefik, incluindo estatísticas gerais, padrões de tráfego, análise de erros e detecção de anomalias. Além disso, foi incorporada uma análise de geolocalização dos IPs para identificar a origem geográfica das requisições.\n\n"

    # Seção: Sumário Executivo
    md_content += f"## Sumário Executivo\n\n"
    if 'general_stats' in data:
        gs = data["general_stats"]
        md_content += f"- **Período Analisado:** {gs.get('periodo_analisado', 'N/A')} ({gs.get('duracao_dias', 'N/A')} dias)\n"
        md_content += f"- **Total de Requisições Processadas:** {gs.get('total_registros', 'N/A'):,}\n"
    
    # Atualizado para usar 'ip_geolocation_404'
    if 'ip_geolocation' in data and data['ip_geolocation'].get('top_404_ips_geo'):
        # Contar países dos IPs 404 para o sumário
        country_counts_404 = Counter([geo_data['country'] for geo_data in data['ip_geolocation']['top_404_ips_geo'].values()])
        sorted_countries = sorted(country_counts_404.items(), key=lambda x: x[1], reverse=True)
        if sorted_countries:
            top_country = sorted_countries[0]
            md_content += f"- **País com Maior Volume de Erros 404 (Top IPs):** {top_country[0]} com {top_country[1]:,} IPs.\n"

    if '404_analysis' in data and data['404_analysis'].get('total_erros_404', 0) > 0:
        error_rate = (data['404_analysis']['total_erros_404'] / data['general_stats']['total_registros']) * 100
        md_content += f"- **Taxa de Erros 404 (Não Encontrado):** {error_rate:.2f}% do total de requisições.\n"
    
    if 'anomaly_detection' in data:
        anomaly_rate = data['anomaly_detection'].get('percentual_anomalias', 0)
        md_content += f"- **Percentual de Requisições Anômalas Detectadas:** {anomaly_rate:.2f}% do total.\n\n"

    # Seção: Resumo Geral
    if 'general_stats' in data:
        gs = data["general_stats"]
        md_content += f"## Resumo Geral\n\n"
        md_content += f"- **Período Analisado:** {gs.get('periodo_analisado', 'N/A')} ({gs.get('duracao_dias', 'N/A')} dias)\n"
        md_content += f"- **Total de Registros Processados:** {gs.get('total_registros', 'N/A'):,}\n\n"

    # Seção: Análise de Geolocalização de IPs (agora focada em top 200 e top 404)
    if 'ip_geolocation' in data:
        geo = data['ip_geolocation']
        md_content += f"## Análise de Geolocalização dos Top IPs\n\n"
        md_content += "Esta seção detalha a origem geográfica dos IPs com maior volume de requisições (status 200) e dos IPs que geraram erros 404 (Não Encontrado).\n\n"
        
        if geo.get('top_200_ips_geo'):
            md_content += f"### Top IPs com Status 200 (Requisições Bem-Sucedidas)\n\n"
            md_content += "Os IPs com maior volume de requisições bem-sucedidas e suas localizações são:\n\n"
            for ip, loc_data in geo['top_200_ips_geo'].items():
                md_content += f"- **{ip}:** País: {loc_data.get('country', 'N/A')}, Estado/Região: {loc_data.get('region', 'N/A')}, Cidade: {loc_data.get('city', 'N/A')}\n"
            md_content += "\n"
        
        if geo.get('top_404_ips_geo'):
            md_content += f"### Top IPs com Erro 404 (Requisições Não Encontradas)\n\n"
            md_content += "Os IPs com maior volume de erros 404 e suas localizações são:\n\n"
            for ip, loc_data in geo['top_404_ips_geo'].items():
                md_content += f"- **{ip}:** País: {loc_data.get('country', 'N/A')}, Estado/Região: {loc_data.get('region', 'N/A')}, Cidade: {loc_data.get('city', 'N/A')}\n"
            md_content += "\n"
        
        if geo.get('total_ips_analisados') is not None:
            md_content += f"- **Total de IPs únicos analisados (Top 200 e Top 404):** {geo.get('total_ips_analisados'):,}\n\n"

    # Seção: Análise de Status HTTP
    if 'status_codes' in data:
        sc = data['status_codes']
        md_content += f"## Análise de Status HTTP\n\n"
        md_content += "Esta seção apresenta a distribuição dos códigos de status HTTP retornados pelas requisições.\n\n"
        md_content += f"### Contagem por Código de Status\n\n"
        if sc.get('contagem_status'):
            for code, count in sc['contagem_status'].items():
                md_content += f"- **{code}:** {count:,}\n"
        else:
            md_content += "- Nenhuma contagem de status disponível.\n"
        md_content += "\n"
        if sc.get('plot_path') and os.path.exists(sc['plot_path']):
            md_content += f"![Distribuição de Status HTTP](./plots/status_distribution.png)\n\n" # Caminho relativo

    # Seção: Padrões Temporais
    if 'time_patterns' in data:
        tp = data['time_patterns']
        md_content += f"## Padrões Temporais\n\n"
        md_content += "Esta seção explora os padrões de requisições ao longo do tempo, por hora e por dia da semana.\n\n"
        md_content += f"- **Horário de Pico (Geral):** {tp.get('pico_requisicoes_hora', 'N/A'):02d}:00h\n"
        md_content += f"- **Dia da Semana de Pico (Geral):** {tp.get('pico_requisicoes_dia', 'N/A')}\n\n"
        if tp.get('plot_path_hora') and os.path.exists(tp['plot_path_hora']):
             md_content += f"### Requisições por Hora\n![Requisições por Hora](./plots/requests_per_hour.png)\n\n"
        if tp.get('plot_path_historico') and os.path.exists(tp['plot_path_historico']):
             md_content += f"### Histórico Diário de Requisições\n![Histórico Diário](./plots/daily_requests_history.png)\n\n"
        if tp.get('plot_path_heatmap') and os.path.exists(tp['plot_path_heatmap']):
             md_content += f"### Heatmap Hora vs. Método HTTP\n![Heatmap Hora/Método](./plots/heatmap_hour_method.png)\n\n"

    # Seção: Análise de Recursos
    if 'resource_analysis' in data:
        ra = data['resource_analysis']
        top_n = 10 
        md_content += f"## Análise de Acesso a Recursos\n\n"
        md_content += "Esta seção identifica os recursos mais e menos acessados no sistema.\n\n"
        md_content += f"### Top {top_n} Recursos Mais Acessados\n\n"
        if ra.get(f'top_{top_n}_recursos_mais_acessados'):
            for resource, count in ra[f'top_{top_n}_recursos_mais_acessados'].items():
                md_content += f"- `{resource}`: {count:,}\n"
        else:
            md_content += "- N/A\n"
        md_content += "\n"
        md_content += f"### Top {top_n} Recursos Menos Acessados\n\n"
        if ra.get(f'top_{top_n}_recursos_menos_acessados'):
             for resource, count in ra[f'top_{top_n}_recursos_menos_acessados'].items():
                md_content += f"- `{resource}`: {count:,}\n"
        else:
            md_content += "- N/A\n"
        md_content += "\n"

    # Seção: Análise de Erros 404
    if '404_analysis' in data:
        fa = data['404_analysis']
        top_n = 10
        md_content += f"## Análise de Erros 404 (Não Encontrado)\n\n"
        md_content += "Esta seção foca na análise de requisições que resultaram em erro 404 (Recurso Não Encontrado).\n\n"
        md_content += f"- **Total de Erros 404:** {fa.get('total_erros_404', 0):,}\n"
        if fa.get('total_erros_404', 0) > 0:
            md_content += f"- **Horário de Pico (404):** {fa.get('pico_404_hora', 'N/A'):02d}:00h\n"
            md_content += f"- **Dia da Semana de Pico (404):** {fa.get('pico_404_dia', 'N/A')}\n\n"
            if fa.get('plot_path_404_hora') and os.path.exists(fa['plot_path_404_hora']):
                md_content += f"### Requisições 404 por Hora\n![404 por Hora](./plots/404_requests_per_hour.png)\n\n"
            md_content += f"### Top {top_n} Recursos Gerando 404\n\n"
            if fa.get(f'top_{top_n}_recursos_404_mais_acessados'):
                for resource, count in fa[f'top_{top_n}_recursos_404_mais_acessados'].items():
                    md_content += f"- `{resource}`: {count:,}\n"
            else:
                md_content += "- N/A\n"
            md_content += "\n"
        else:
             md_content += "\n"

    # Seção: Detecção de Anomalias
    if 'anomaly_detection' in data:
        ad = data['anomaly_detection']
        md_content += f"## Detecção de Anomalias\n\n"
        md_content += "Esta seção identifica padrões de requisições que podem indicar atividades incomuns ou maliciosas.\n\n"
        md_content += f"- **Total de Requisições Anômalas Detectadas:** {ad.get('total_anomalias_detectadas', 0):,} ({ad.get('percentual_anomalias', 0):.2f}% do total)\n\n"

        if ad.get('plot_path_tipos_anomalia') and os.path.exists(ad['plot_path_tipos_anomalia']):
            md_content += f"### Contagem por Tipo de Anomalia\n![Tipos de Anomalia](./plots/anomaly_types_count.png)\n\n"
        else:
             md_content += f"### Contagem por Tipo de Anomalia:\n\n"
             if ad.get('contagem_por_tipo_anomalia'):
                 md_content += format_dict_for_md(ad['contagem_por_tipo_anomalia'], indent=1)
             else:
                 md_content += "- Nenhuma anomalia específica contada.\n"
             md_content += "\n"

        if ad.get('plot_path_status_anomalias') and os.path.exists(ad['plot_path_status_anomalias']):
            md_content += f"### Distribuição de Status HTTP em Anomalias (%)\n![Status em Anomalias](./plots/anomaly_status_distribution_pct.png)\n\n"

        md_content += f"### Detalhes das Anomalias\n\n"
        md_content += f"- **Métodos HTTP Incomuns:**\n{format_dict_for_md(ad.get('metodos_http_incomuns_detectados', {}), 1)}"
        md_content += f"- **IPs Suspeitos (Muitos 404s):**\n{format_dict_for_md(ad.get('ips_suspeitos_com_muitos_404', {}), 1)}"
        md_content += f"- **Requisições com Tamanho Suspeito (>1MB):**\n"
        ts = ad.get('requisicoes_tamanho_suspeito', {})
        md_content += f"  - Contagem: {ts.get('contagem', 0):,}\n"
        md_content += f"  - Top 10 Recursos:\n{format_dict_for_md(ts.get('top_10_recursos', {}), 2)}"

        md_content += f"- **Top 10 Recursos Anômalos:**\n{format_dict_for_md(ad.get('top_10_recursos_anomalos', {}), 1)}"

        # Novas seções para as anomalias adicionadas
        if ad.get('user_agents_incomuns'):
            md_content += f"### User-Agents Incomuns\n\n"
            md_content += "Os seguintes User-Agents foram identificados como incomuns (pouco frequentes) nas requisições anômalas:\n\n"
            for ua, count in ad['user_agents_incomuns']:
                md_content += f"- `{ua}`: {count:,} ocorrências\n"
            md_content += "\n"

        if ad.get('recursos_query_string_longa'):
            md_content += f"### Recursos com Query Strings Longas\n\n"
            md_content += "Os seguintes recursos contêm query strings consideradas excessivamente longas:\n\n"
            for recurso, count in ad['recursos_query_string_longa']:
                md_content += f"- `{recurso}`: {count:,} ocorrências\n"
            md_content += "\n"

        if ad.get('recursos_muitos_parametros'):
            md_content += f"### Recursos com Muitos Parâmetros\n\n"
            md_content += "Os seguintes recursos contêm um número elevado de parâmetros na query string:\n\n"
            for recurso, count in ad['recursos_muitos_parametros']:
                md_content += f"- `{recurso}`: {count:,} ocorrências\n"
            md_content += "\n"

        if ad.get('ips_alto_volume'):
            md_content += f"### IPs com Alto Volume de Requisições\n\n"
            md_content += "Os seguintes IPs foram identificados com um volume de requisições anormalmente alto:\n\n"
            for ip, count in ad['ips_alto_volume']:
                md_content += f"- `{ip}`: {count:,} requisições\n"
            md_content += "\n"


    # Adicionar seção de conclusões e recomendações
    md_content += f"## Conclusões e Recomendações\n\n"
    md_content += "Com base na análise, as seguintes conclusões e recomendações podem ser feitas:\n\n"
    
    # Atualizado para usar 'ip_geolocation'
    if 'ip_geolocation' in data and data['ip_geolocation'].get('top_404_ips_geo'):
        country_counts_404 = Counter([geo_data['country'] for geo_data in data['ip_geolocation']['top_404_ips_geo'].values()])
        sorted_countries = sorted(country_counts_404.items(), key=lambda x: x[1], reverse=True)
        if sorted_countries:
            top_country = sorted_countries[0]
            md_content += f"- A maior parte dos erros 404 (dentre os top IPs analisados) origina-se de **{top_country[0]}**. *Recomendação: Se este tráfego não for esperado, considere investigar a origem ou aplicar restrições de acesso geográfico.*\n"
    
    if '404_analysis' in data and data['404_analysis'].get('total_erros_404', 0) > 0:
        error_rate = (data['404_analysis']['total_erros_404'] / data['general_stats']['total_registros']) * 100
        md_content += f"- Foram detectados {data['404_analysis']['total_erros_404']:,} erros 404, representando {error_rate:.2f}% do total de requisições. *Recomendação: Analisar os recursos que mais geram 404s para corrigir links quebrados ou remover conteúdo obsoleto, melhorando a experiência do usuário e a otimização para motores de busca.*\n"
    
    if 'anomaly_detection' in data:
        anomaly_rate = data['anomaly_detection'].get('percentual_anomalias', 0)
        if anomaly_rate > 0:
            md_content += f"- **Atenção:** {anomaly_rate:.2f}% das requisições foram classificadas como anômalas. *Recomendação: Revisar detalhadamente as requisições anômalas, especialmente aquelas relacionadas a SQLi, XSS ou métodos HTTP incomuns, para identificar e mitigar possíveis ameaças de segurança.*\n"
        else:
            md_content += f"- Nenhuma anomalia significativa foi detectada, indicando um comportamento de tráfego normal. *Recomendação: Manter o monitoramento contínuo para identificar novas ameaças.*\n"

    md_content += "\n---\n"
    
    now_final = datetime.datetime.now()
    final_date_str = now_final.strftime("%d/%m/%Y às %H:%M:%S")
    md_content += f"*Relatório gerado automaticamente em {final_date_str}*\n"

    try:
        with open(output_file, 'w', encoding='utf-8') as f:
            f.write(md_content)
        print("Relatório Markdown gerado com sucesso.")
        return True
    except Exception as e:
        print(f"Erro ao gerar relatório Markdown: {e}")
        return False