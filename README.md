# 🦟 Evolução dos Casos de Dengue no Brasil (2015–2024)

**Disciplina:** Linguagem de Programação — Análise e Visualização de Dados com Python
**Professor:** Alexandre Neves Louzada
**Aluno:** Raphael Cortes
**Projeto:** G1 — Tema 1

Projeto individual de análise e visualização de dados que investiga a evolução dos casos de
dengue no Brasil entre 2015 e 2024, a partir de um dataset simulado com 4.440 registros
mensais (37 municípios, 20 estados, 5 regiões).

## 🔗 Links do projeto

| Recurso | Link |
|---|---|
| Repositório GitHub | `https://github.com/RAPHAELCCORTES/projeto-dengue-brasil` |
| Página do projeto (GitHub Pages) | `https://raphaelccortes.github.io/projeto-dengue-brasil/` |
| Dashboard (Streamlit Community Cloud) | `https://projeto-dengue-brasil.streamlit.app/` |
| Notebook de análise | [`notebooks/analise_dengue.ipynb`](notebooks/analise_dengue.ipynb) |
| Base de dados | [`dados/simulacao_dengue_brasil.csv`](dados/simulacao_dengue_brasil.csv) |


## 🎯 Objetivo

Desenvolver uma aplicação analítica completa capaz de explorar os dados de dengue no
Brasil, identificar padrões temporais e regionais e apresentar visualizações interativas
para apoiar a vigilância epidemiológica. O projeto busca responder:

- Quais estados apresentam mais casos de dengue?
- Existem períodos do ano mais críticos?
- Há crescimento dos casos ao longo dos anos?
- Existe relação entre chuva e aumento de casos?
- Quais municípios apresentam maior incidência?
- Há regiões mais vulneráveis?
- Quais períodos exigem maior atenção da saúde pública?

## 🗂️ Estrutura do projeto

```
projeto-dengue-brasil/
│
├── app.py                        # Dashboard interativo (Streamlit)
├── requirements.txt              # Dependências do projeto
├── README.md                     # Este arquivo
├── index.html                    # Página de apresentação (GitHub Pages)
├── dados/
│   └── simulacao_dengue_brasil.csv
├── database/
│   ├── models.py                 # Modelagem SQLAlchemy + script de carga no SQLite
│   └── dengue.db                 # Banco SQLite gerado a partir do CSV
├── notebooks/
│   └── analise_dengue.ipynb      # Notebook de análise exploratória completa
└── imagens/                      # Gráficos exportados pelo notebook (usados no index.html)
```

## 🛠️ Tecnologias utilizadas

**Obrigatórias:** Python · Pandas · Matplotlib · Seaborn · Streamlit · GitHub
**Adicionais:** Plotly · SQLAlchemy · SQLite

### Funcionalidades intermediárias implementadas
- Filtros múltiplos no Streamlit (ano, mês, região, UF, município, nível de alerta)
- KPIs dinâmicos, recalculados conforme os filtros
- Análise temporal (evolução mensal/anual e sazonalidade)
- Dashboard organizado em seções/abas
- Visualizações comparativas (regiões e estados)

### Funcionalidades avançadas implementadas
1. **Persistência em banco + modelagem relacional** — `database/models.py` usa SQLAlchemy
   para modelar a tabela `registros_dengue` e carregar os dados do CSV em um banco SQLite
   (`database/dengue.db`); o dashboard lê os dados a partir desse banco.
2. **Mapa interativo** — aba "Mapa Interativo" do dashboard, construída com Plotly
   (`scatter_geo`), mostrando o total de casos por estado.

## 📊 Base de dados

Arquivo: `dados/simulacao_dengue_brasil.csv` — dataset simulado fornecido pelo professor.

| Coluna | Descrição |
|---|---|
| ano | Ano da ocorrência |
| mes | Mês da ocorrência |
| data | Data de referência |
| regiao | Região do Brasil |
| uf | Estado |
| municipio | Município |
| populacao | População estimada |
| chuva_mm | Volume médio de chuva |
| temperatura_media | Temperatura média |
| casos_dengue | Quantidade de casos |
| internacoes | Internações registradas |
| obitos | Óbitos registrados |
| incidencia_100k | Casos por 100 mil habitantes |
| nivel_alerta | Nível de alerta epidemiológico |

## ▶️ Como rodar localmente

```bash
# 1. Criar e ativar um ambiente virtual (recomendado)
python -m venv venv
source venv/bin/activate        # Windows: venv\Scripts\activate

# 2. Instalar as dependências
pip install -r requirements.txt

# 3. Criar o banco SQLite a partir do CSV
python database/models.py

# 4. Rodar o dashboard
streamlit run app.py
```

O dashboard abrirá em `http://localhost:8501`.

Para abrir o notebook de análise:

```bash
pip install notebook
jupyter notebook notebooks/analise_dengue.ipynb
```

## 📈 Principais achados (visão geral, 2015–2024)

- **Total de casos:** 3.560.562 | **Total de óbitos:** 5.314
- **Estado com mais casos:** Rio de Janeiro (RJ)
- **Região mais afetada:** Sudeste
- **Município com maior incidência média:** Campinas
- **Sazonalidade:** concentração de casos nos meses mais quentes/chuvosos do ano (destaque
  para o mês de abril no agregado nacional)
- **Correlação chuva x casos:** positiva, porém moderada (≈ 0,29) — a chuva é um fator
  relevante, mas não o único determinante do número de casos

Detalhes completos da análise, incluindo todos os gráficos, estão no notebook
[`analise_dengue.ipynb`](notebooks/analise_dengue.ipynb).

## 🚀 Publicação (passo a passo)


---
Projeto desenvolvido para fins educacionais — Linguagem de Programação: Análise e
Visualização de Dados com Python.
