"""
Dashboard interativo — Evolução dos Casos de Dengue no Brasil (2015-2024)

Projeto G1 — Tema 1
Disciplina: Linguagem de Programação — Análise e Visualização de Dados com Python
Professor: Alexandre Neves Louzada
Aluno: Raphael Cortes

Executar localmente:
    pip install -r requirements.txt
    python database/models.py      # cria/atualiza database/dengue.db a partir do CSV
    streamlit run app.py
"""
from __future__ import annotations

import os

import matplotlib.pyplot as plt
import pandas as pd
import plotly.express as px
import seaborn as sns
import streamlit as st

from database.models import DB_PATH, carregar_dataframe, criar_banco

# --------------------------------------------------------------------------- Config geral
st.set_page_config(
    page_title="Dengue no Brasil — Dashboard G1",
    page_icon="🦟",
    layout="wide",
)

sns.set_theme(style="whitegrid", palette="viridis")

UF_COORDS = {
    "AM": (-3.42, -65.86), "BA": (-12.58, -41.70), "CE": (-5.50, -39.32),
    "DF": (-15.80, -47.86), "ES": (-19.18, -40.31), "GO": (-15.83, -49.84),
    "MA": (-4.96, -45.27), "MG": (-18.51, -44.56), "MS": (-20.77, -54.79),
    "MT": (-12.68, -56.92), "PA": (-5.00, -52.50), "PB": (-7.24, -36.78),
    "PE": (-8.81, -36.95), "PR": (-24.89, -51.25), "RJ": (-22.91, -43.21),
    "RO": (-10.95, -62.82), "RS": (-30.03, -53.22), "SC": (-27.24, -50.22),
    "SP": (-22.50, -48.50), "TO": (-10.18, -48.30),
}

ESTACAO_POR_MES = {
    12: "Verão", 1: "Verão", 2: "Verão",
    3: "Outono", 4: "Outono", 5: "Outono",
    6: "Inverno", 7: "Inverno", 8: "Inverno",
    9: "Primavera", 10: "Primavera", 11: "Primavera",
}


@st.cache_data(show_spinner="Carregando base de dados...")
def carregar_dados() -> pd.DataFrame:
    """Carrega os dados do SQLite; se o banco não existir, cria a partir do CSV."""
    if not os.path.exists(DB_PATH):
        criar_banco()
    df = carregar_dataframe()
    df["data"] = pd.to_datetime(df["data"])
    df["estacao"] = df["mes"].map(ESTACAO_POR_MES)
    df["taxa_internacao_pct"] = (df["internacoes"] / df["casos_dengue"]).replace([float("inf")], 0).fillna(0) * 100
    df["taxa_letalidade_pct"] = (df["obitos"] / df["casos_dengue"]).replace([float("inf")], 0).fillna(0) * 100
    return df


def formatar_numero(n: float) -> str:
    return f"{n:,.0f}".replace(",", ".")


# --------------------------------------------------------------------------- Cabeçalho
df_raw = carregar_dados()

st.title("🦟 Evolução dos Casos de Dengue no Brasil")
st.caption(
    "Projeto G1 — Tema 1 · Disciplina **Linguagem de Programação — Análise e Visualização "
    "de Dados com Python** · Professor **Alexandre Neves Louzada** · Aluno **Raphael Cortes**"
)

st.markdown(
    """
A dengue é uma das principais doenças transmitidas por mosquitos no Brasil e um importante
problema de saúde pública, com proliferação associada a fatores climáticos e urbanos. Este
dashboard explora um dataset simulado (2015–2024, 37 municípios, 20 estados) para apoiar a
identificação de padrões temporais e regionais e orientar ações preventivas de saúde pública.
"""
)

# --------------------------------------------------------------------------- Filtros (sidebar)
st.sidebar.header("🔎 Filtros")

anos = sorted(df_raw["ano"].unique())
ano_sel = st.sidebar.multiselect("Ano", anos, default=anos)

meses = sorted(df_raw["mes"].unique())
mes_sel = st.sidebar.multiselect("Mês", meses, default=meses)

regioes = sorted(df_raw["regiao"].unique())
regiao_sel = st.sidebar.multiselect("Região", regioes, default=regioes)

ufs_disponiveis = sorted(df_raw.loc[df_raw["regiao"].isin(regiao_sel), "uf"].unique())
uf_sel = st.sidebar.multiselect("Estado (UF)", ufs_disponiveis, default=ufs_disponiveis)

municipios_disponiveis = sorted(df_raw.loc[df_raw["uf"].isin(uf_sel), "municipio"].unique())
municipio_sel = st.sidebar.multiselect("Município", municipios_disponiveis, default=municipios_disponiveis)

niveis = sorted(df_raw["nivel_alerta"].unique())
nivel_sel = st.sidebar.multiselect("Nível de alerta", niveis, default=niveis)

if st.sidebar.button("🔄 Recriar banco a partir do CSV"):
    criar_banco()
    st.cache_data.clear()
    st.rerun()

df = df_raw[
    df_raw["ano"].isin(ano_sel)
    & df_raw["mes"].isin(mes_sel)
    & df_raw["regiao"].isin(regiao_sel)
    & df_raw["uf"].isin(uf_sel)
    & df_raw["municipio"].isin(municipio_sel)
    & df_raw["nivel_alerta"].isin(nivel_sel)
]

if df.empty:
    st.warning("Nenhum registro encontrado para os filtros selecionados. Ajuste os filtros na barra lateral.")
    st.stop()

# --------------------------------------------------------------------------- KPIs
st.subheader("📊 Indicadores (KPIs)")

total_casos = df["casos_dengue"].sum()
total_obitos = df["obitos"].sum()
media_mensal = df.groupby("data")["casos_dengue"].sum().mean()
casos_por_uf = df.groupby("uf", observed=True)["casos_dengue"].sum().sort_values(ascending=False)
incidencia_por_municipio = df.groupby("municipio", observed=True)["incidencia_100k"].mean().sort_values(ascending=False)

col1, col2, col3, col4, col5, col6 = st.columns(6)
col1.metric("Total de casos", formatar_numero(total_casos))
col2.metric("Total de óbitos", formatar_numero(total_obitos))
col3.metric("Média mensal de casos", formatar_numero(media_mensal))
col4.metric("Estado mais afetado", casos_por_uf.index[0] if len(casos_por_uf) else "—")
col5.metric("Município crítico", incidencia_por_municipio.index[0] if len(incidencia_por_municipio) else "—")
col6.metric("Incidência média", f"{df['incidencia_100k'].mean():.1f} /100k")

st.divider()

# --------------------------------------------------------------------------- Abas
tab_temporal, tab_regional, tab_mapa, tab_dados, tab_sobre = st.tabs(
    ["📈 Análise Temporal", "🗺️ Comparação Regional", "📍 Mapa Interativo", "📋 Dados", "ℹ️ Sobre o projeto"]
)

# ---- Aba Temporal
with tab_temporal:
    st.markdown("#### Evolução temporal dos casos")
    casos_por_periodo = df.groupby("data")["casos_dengue"].sum().reset_index()
    fig, ax = plt.subplots(figsize=(11, 4.5))
    ax.plot(casos_por_periodo["data"], casos_por_periodo["casos_dengue"], marker="o", markersize=3, color="#c0392b")
    ax.set_xlabel("Período")
    ax.set_ylabel("Casos de dengue")
    ax.set_title("Evolução mensal dos casos de dengue")
    fig.autofmt_xdate()
    st.pyplot(fig)
    plt.close(fig)

    st.markdown("#### Sazonalidade — heatmap mensal (mês x ano)")
    pivot = df.pivot_table(index="mes", columns="ano", values="casos_dengue", aggfunc="sum")
    fig2, ax2 = plt.subplots(figsize=(11, 5))
    sns.heatmap(pivot, cmap="YlOrRd", ax=ax2, cbar_kws={"label": "Casos"})
    ax2.set_xlabel("Ano")
    ax2.set_ylabel("Mês")
    st.pyplot(fig2)
    plt.close(fig2)

    casos_por_ano = df.groupby("ano")["casos_dengue"].sum()
    if len(casos_por_ano) >= 2:
        variacao = (casos_por_ano.iloc[-1] - casos_por_ano.iloc[0]) / casos_por_ano.iloc[0] * 100
        tendencia = "crescimento" if variacao > 0 else "queda"
        st.info(
            f"📝 **Interpretação:** no intervalo selecionado, os casos variaram "
            f"**{variacao:+.1f}%** entre {casos_por_ano.index[0]} e {casos_por_ano.index[-1]} "
            f"— uma tendência de **{tendencia}**. O heatmap acima evidencia os meses "
            f"historicamente mais críticos (tons mais escuros), geralmente concentrados no "
            f"período mais quente e chuvoso do ano."
        )

# ---- Aba Regional
with tab_regional:
    st.markdown("#### Total de casos por estado (UF)")
    fig3, ax3 = plt.subplots(figsize=(11, 5))
    casos_por_uf.plot(kind="bar", ax=ax3, color=sns.color_palette("viridis", len(casos_por_uf)))
    ax3.set_xlabel("UF")
    ax3.set_ylabel("Total de casos")
    st.pyplot(fig3)
    plt.close(fig3)

    col_a, col_b = st.columns(2)
    with col_a:
        st.markdown("#### Comparação entre regiões")
        casos_por_regiao = df.groupby("regiao", observed=True)["casos_dengue"].sum().sort_values(ascending=False)
        fig4, ax4 = plt.subplots(figsize=(5.5, 4.5))
        casos_por_regiao.plot(kind="bar", ax=ax4, color="#2980b9")
        ax4.set_xlabel("Região")
        ax4.set_ylabel("Total de casos")
        st.pyplot(fig4)
        plt.close(fig4)

    with col_b:
        st.markdown("#### Relação entre chuva e casos")
        fig5, ax5 = plt.subplots(figsize=(5.5, 4.5))
        sns.regplot(
            data=df, x="chuva_mm", y="casos_dengue",
            scatter_kws={"alpha": 0.3, "s": 15}, line_kws={"color": "#c0392b"}, ax=ax5,
        )
        ax5.set_xlabel("Chuva média (mm)")
        ax5.set_ylabel("Casos de dengue")
        st.pyplot(fig5)
        plt.close(fig5)

    correlacao = df["chuva_mm"].corr(df["casos_dengue"])
    regiao_top = casos_por_regiao.index[0] if len(casos_por_regiao) else "—"
    st.info(
        f"📝 **Interpretação:** a região **{regiao_top}** concentra o maior volume de casos "
        f"no recorte atual. A correlação entre chuva e casos é de **{correlacao:.2f}** "
        f"(escala -1 a 1): valores mais próximos de 1 indicam relação positiva mais forte "
        f"entre volume de chuva e número de casos registrados."
    )

# ---- Aba Mapa
with tab_mapa:
    st.markdown("#### Mapa interativo — casos por estado")
    mapa_df = casos_por_uf.reset_index()
    mapa_df.columns = ["uf", "casos_dengue"]
    mapa_df["lat"] = mapa_df["uf"].map(lambda u: UF_COORDS.get(u, (None, None))[0])
    mapa_df["lon"] = mapa_df["uf"].map(lambda u: UF_COORDS.get(u, (None, None))[1])
    mapa_df = mapa_df.dropna(subset=["lat", "lon"])

    fig_mapa = px.scatter_geo(
        mapa_df,
        lat="lat",
        lon="lon",
        size="casos_dengue",
        color="casos_dengue",
        hover_name="uf",
        color_continuous_scale="YlOrRd",
        scope="south america",
        projection="natural earth",
        title="Casos de dengue por estado (tamanho e cor proporcionais ao total de casos)",
    )
    fig_mapa.update_geos(fitbounds="locations", visible=True)
    fig_mapa.update_layout(height=550, margin=dict(l=0, r=0, t=40, b=0))
    st.plotly_chart(fig_mapa, use_container_width=True)
    st.caption(
        "Coordenadas aproximadas das capitais/centros de cada estado, usadas apenas para "
        "posicionamento no mapa (funcionalidade avançada: mapa interativo com Plotly)."
    )

# ---- Aba Dados
with tab_dados:
    st.markdown("#### Tabela dinâmica")
    st.caption(f"{len(df):,} registros após os filtros aplicados.".replace(",", "."))
    st.dataframe(
        df[[
            "data", "regiao", "uf", "municipio", "populacao", "chuva_mm", "temperatura_media",
            "casos_dengue", "internacoes", "obitos", "incidencia_100k", "nivel_alerta",
        ]].sort_values("data"),
        use_container_width=True,
        height=420,
    )

    st.markdown("#### Top 10 municípios por incidência média")
    st.dataframe(incidencia_por_municipio.head(10).reset_index().rename(
        columns={"municipio": "Município", "incidencia_100k": "Incidência média (/100k)"}
    ), use_container_width=True)

    csv_bytes = df.to_csv(index=False).encode("utf-8")
    st.download_button("⬇️ Baixar dados filtrados (CSV)", csv_bytes, file_name="dengue_filtrado.csv", mime="text/csv")

# ---- Aba Sobre
with tab_sobre:
    st.markdown(
        """
### Sobre o projeto

**Contextualização:** a dengue é uma das principais doenças transmitidas por mosquitos no
Brasil, com proliferação do *Aedes aegypti* associada a fatores climáticos, ambientais e
urbanos. O monitoramento da evolução dos casos é fundamental para apoiar campanhas de
conscientização e políticas públicas.

**Perguntas de negócio respondidas neste dashboard:**
- Quais estados apresentam mais casos de dengue?
- Existem períodos do ano mais críticos?
- Há crescimento dos casos ao longo dos anos?
- Existe relação entre chuva e aumento de casos?
- Quais municípios apresentam maior incidência?
- Há regiões mais vulneráveis?

**Tecnologias utilizadas:** Python, Pandas, Matplotlib, Seaborn, Streamlit, Plotly,
SQLAlchemy + SQLite, GitHub e GitHub Pages.

**Funcionalidades avançadas implementadas:**
1. Persistência e modelagem relacional em banco SQLite via SQLAlchemy (`database/models.py`).
2. Mapa interativo com Plotly (aba "Mapa Interativo").

### Conclusão executiva

A análise da década 2015–2024 reforça um padrão sazonal claro nos casos de dengue — com
concentração em períodos mais quentes e chuvosos — e uma distribuição desigual entre
estados e municípios, o que reforça a importância de políticas de saúde pública
regionalizadas e de monitoramento contínuo. Os filtros interativos deste dashboard permitem
que qualquer recorte (ano, mês, região, estado, município ou nível de alerta) seja
explorado em segundos, apoiando decisões rápidas e baseadas em dados pela vigilância
epidemiológica.
"""
    )

st.divider()
st.caption(
    "Projeto desenvolvido para fins educacionais — Linguagem de Programação: Análise e "
    "Visualização de Dados com Python · Professor Alexandre Neves Louzada · Aluno Raphael Cortes."
)
