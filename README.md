# LogGuardian - Detecção Automática de Requisições Suspeitas

![Python](https://img.shields.io/badge/Python-3.8%2B-blue)
![License](https://img.shields.io/badge/License-MIT-green)
![Research](https://img.shields.io/badge/Research-PIBIC%2FUFRPE-orange)

## 📌 Visão Geral

O **LogGuardian** é uma ferramenta de análise de logs de acesso web que utiliza técnicas de aprendizado de máquina para identificar padrões suspeitos e anomalias em requisições HTTP. Desenvolvido como parte de um projeto de pesquisa PIBIC na UFRPE, este sistema automatiza a detecção de atividades maliciosas em logs de servidores, substituindo a análise manual por uma abordagem baseada em dados.

## 🎯 Objetivos do Projeto

1. Automatizar a identificação de requisições maliciosas em logs web
2. Desenvolver técnicas para detecção de anomalias baseadas em comportamento
3. Comparar a eficácia da abordagem com métodos tradicionais e diferentes estudos
4. Investigar relações entre anomalias em diferentes logs para identificar ataques coordenados

## ⚙️ Funcionalidades Principais

- **Análise Estatística Completa**:
  - Distribuição de códigos de status HTTP
  - Padrões temporais (hora/dia/semana)
  - Recursos mais e menos acessados
  - Análise detalhada de erros 404
  
- **Detecção de Anomalias**:
  - Identificação de métodos HTTP incomuns
  - Detecção de padrões de injeção (SQL, XSS)
  - URLs excessivamente longas
  - Extensões de arquivo suspeitas
  - IPs com múltiplos erros 404
  - Respostas com tamanho anormal

- **Visualização de Dados**:
  - Gráficos interativos de distribuição
  - Heatmaps hora/método
  - Visualização de tendências temporais

## 🛠️ Tecnologias Utilizadas

- **Linguagem**: Python 3.8+
- **Bibliotecas Principais**:
  - Pandas (manipulação de dados)
  - Matplotlib/Seaborn (visualização)
  - Scikit-learn (modelos de ML)
  - Kagglehub (acesso a datasets)
- **Frameworks**: Jupyter Notebooks (análise exploratória)
- **Formato de Saída**: JSON, Markdown, PNG (gráficos)

## 📥 Instalação e Execução

### Pré-requisitos
- Python 3.8
- Gerenciador de pacotes pip

### Passo a Passo

1. Clone o repositório:
   ```bash
   git clone https://github.com/seu-usuario/LogGuardian.git
   cd LogGuardian
   ```

2. Crie um ambiente virtual (opcional mas recomendado):
   ```bash
   python -m venv venv
   source venv/bin/activate  # Linux/Mac
   venv\Scripts\activate     # Windows
   ```

3. Instale as dependências:
   ```bash
   pip install -r requirements.txt
   ```

4. Execute a análise principal:
   ```bash
   python main.py
   ```

5. Acesse os resultados:
   - Relatório completo: `output/analysis_report.md`
   - Dados processados: `output/analysis_results.json`
   - Visualizações: `output/plots/`

## 📊 Resultados Esperados

A ferramenta gera relatórios abrangentes que incluem:

1. Estatísticas gerais de acesso
2. Distribuição temporal das requisições
3. Identificação de recursos problemáticos
4. Detecção de padrões anômalos
5. Visualizações profissionais prontas para publicação

## 📜 Licença

Distribuído sob a licença MIT. Veja `LICENSE` para mais informações.

## 🌐 Contato

**Pesquisador Responsável**: Alan Torres
**Orientador Responsável**: Rafael Perazzo
**Instituição**: Universidade Federal Rural de Pernambuco (UFRPE)  
**Programa**: PIBIC/CNPq  
