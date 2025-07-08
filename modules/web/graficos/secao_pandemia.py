import streamlit as st
import plotly.express as px
import pandas as pd
from pandas.api.types import CategoricalDtype
from modules.web.graficos.utils import classificar_periodo, categorizar_ingresso_pandemia, calcula_filtragem, \
    exibe_info_filtragem


def preparar_dados_pandemia(df: pd.DataFrame) -> pd.DataFrame:
    df = df.copy()
    df['Categoria_Ingresso'] = df['FORMA_INGRESSO_PADRONIZADA'].apply(categorizar_ingresso_pandemia)

    if 'SEMESTRE_INGRESSO' not in df.columns:
        df['SEMESTRE_INGRESSO'] = 1

    df['SEMESTRE_INGRESSO'] = df['SEMESTRE_INGRESSO'].astype(str).str.replace('.0', '')
    df['PERIODO_CONTINUO'] = df['ANO_INGRESSO'].astype(str) + '.' + df['SEMESTRE_INGRESSO'].astype(str)
    df['PERIODO_PANDEMIA'] = df.apply(classificar_periodo, axis=1)
    df['SEMESTRE_EVASAO'] = df['SEMESTRE_EVASAO'].astype(str).str.replace('.0', '')
    df['ANO_EVASAO'] = pd.to_numeric(df['ANO_EVASAO'], errors='coerce')
    df['SEMESTRE_EVASAO'] = pd.to_numeric(df['SEMESTRE_EVASAO'], errors='coerce')

    df['PERIODO_EVASAO_CONTINUO'] = df.apply(
        lambda row: f"{int(row['ANO_EVASAO'])}.{int(row['SEMESTRE_EVASAO'])}"
        if pd.notnull(row['ANO_EVASAO']) and pd.notnull(row['SEMESTRE_EVASAO'])
        else None,
        axis=1
    )

    ordem_periodos = ["Pré-pandemia", "Pandemia/ERE", "Pós-pandemia"]
    tipo_categ = CategoricalDtype(categories=ordem_periodos, ordered=True)
    df['PERIODO_PANDEMIA'] = df['PERIODO_PANDEMIA'].astype(tipo_categ)

    df_filtrado = df[df['ANO_INGRESSO'] < 2024].copy()
    df_filtrado['PERIODO_PANDEMIA'] = df_filtrado['PERIODO_PANDEMIA'].astype(tipo_categ)
    df_filtrado['EVADIDO'] = df_filtrado['FORMA_EVASAO_PADRONIZADA'].str.lower().isin(['evasão', 'evadido', 'evasao'])

    return df_filtrado


def exibir_grafico_cra_periodo_continuo(df):
    st.subheader("Média do CRA por Período de Ingresso")
    cra_periodo = (
        df[df['CRA'] <= 10]
        .groupby('PERIODO_CONTINUO')['CRA']
        .mean()
        .reset_index(name='CRA Médio')
        .sort_values(by='PERIODO_CONTINUO')
    )
    fig = px.line(cra_periodo, x='PERIODO_CONTINUO', y='CRA Médio',
                  title='Evolução do CRA Médio por Período de Ingresso', markers=True)
    fig.add_vrect(x0="2020.1", x1="2021.2", fillcolor="red", opacity=0.15, line_width=0, annotation_text="Pandemia/ERE",
                  annotation_position="top left")
    ticks = [p for p in cra_periodo['PERIODO_CONTINUO'] if p.endswith('.1')]
    fig.update_xaxes(tickvals=ticks, ticktext=[t.replace('.1', '') for t in ticks])
    st.plotly_chart(fig, use_container_width=True)


def exibir_grafico_evasao_periodo(df):
    st.subheader("Taxa de Evasão por Período (Evasão)")

    # Filtra somente os evadidos com período de evasão válido
    df_evasao = df[
        df['EVADIDO'] & df['PERIODO_EVASAO_CONTINUO'].notnull()
    ].copy()

    if df_evasao.empty:
        st.info("Nenhum dado de evasão com período válido.")
        return

    # Agrupa por período de evasão e conta quantos alunos evadiram
    evasao = (
        df_evasao
        .groupby('PERIODO_EVASAO_CONTINUO')
        .size()
        .reset_index(name='Qtd. de Evasões')
    )

    # Ordena os períodos corretamente
    evasao = evasao.sort_values(by='PERIODO_EVASAO_CONTINUO')

    # Plot
    fig = px.line(
        evasao,
        x='PERIODO_EVASAO_CONTINUO',
        y='Qtd. de Evasões',
        title='Taxa de Evasão por Período (Evasão)',
        markers=True
    )

    # Destaque da pandemia
    fig.add_vrect(
        x0="2020.1", x1="2021.2",
        fillcolor="red", opacity=0.15,
        line_width=0,
        annotation_text="Pandemia/ERE", annotation_position="top left"
    )

    # Deixa só os semestres .1 como tick
    ticks = [p for p in evasao['PERIODO_EVASAO_CONTINUO'] if p.endswith('.1')]
    fig.update_xaxes(tickvals=ticks, ticktext=[t.replace('.1', '') for t in ticks])

    st.plotly_chart(fig, use_container_width=True)



def exibir_grafico_cra_periodo_pandemico(df):
    st.subheader("🎓 CRA médio antes, durante e após a pandemia")
    cra = df[df['CRA'] <= 10].groupby('PERIODO_PANDEMIA')['CRA'].mean().reset_index(name='CRA Médio')
    st.dataframe(cra, use_container_width=True)
    fig = px.bar(cra, x='PERIODO_PANDEMIA', y='CRA Médio', color='PERIODO_PANDEMIA',
                 title="CRA Médio por Período Pandêmico")
    st.plotly_chart(fig, use_container_width=True)


def exibir_grafico_evasao_forma_periodo(df):
    st.subheader("🚦 Evasão por Forma de Ingresso e Período Pandêmico")
    evasao = df.groupby(['PERIODO_PANDEMIA', 'Categoria_Ingresso'])['EVADIDO'].mean().reset_index(
        name='Taxa de Evasão (%)')
    evasao['Taxa de Evasão (%)'] *= 100
    ordem = ["Pré-pandemia", "Pandemia/ERE", "Pós-pandemia"]
    tipo_categ = CategoricalDtype(categories=ordem, ordered=True)
    evasao['PERIODO_PANDEMIA'] = evasao['PERIODO_PANDEMIA'].astype(tipo_categ)
    evasao = evasao.sort_values(['Categoria_Ingresso', 'PERIODO_PANDEMIA'])
    fig = px.bar(evasao, x='Categoria_Ingresso', y='Taxa de Evasão (%)', color='PERIODO_PANDEMIA', barmode='group',
                 category_orders={'PERIODO_PANDEMIA': ordem},
                 title="Taxa de Evasão por Forma de Ingresso em cada Período")
    st.plotly_chart(fig, use_container_width=True)
    st.dataframe(evasao, use_container_width=True)


def exibir_grafico_cra_forma_periodo(df):
    st.subheader("🎯 CRA Médio por Forma de Ingresso e Período")
    cra = df[df['CRA'] <= 10].groupby(['PERIODO_PANDEMIA', 'Categoria_Ingresso'])['CRA'].mean().reset_index(
        name='CRA Médio')
    ordem = ["Pré-pandemia", "Pandemia/ERE", "Pós-pandemia"]
    tipo_categ = CategoricalDtype(categories=ordem, ordered=True)
    cra['PERIODO_PANDEMIA'] = cra['PERIODO_PANDEMIA'].astype(tipo_categ)
    cra = cra.sort_values(['Categoria_Ingresso', 'PERIODO_PANDEMIA'])
    fig = px.bar(cra, x='Categoria_Ingresso', y='CRA Médio', color='PERIODO_PANDEMIA', barmode='group',
                 category_orders={'PERIODO_PANDEMIA': ordem}, title="CRA Médio por Forma de Ingresso e Período")
    st.plotly_chart(fig, use_container_width=True)
    st.dataframe(cra, use_container_width=True)
    st.info("> **Observação:** O período de pandemia/ERE corresponde de 2020.1 até 2021.2.")


def graficos_secao_pandemia(df: pd.DataFrame):
    st.header("📱 Impactos da COVID-19 e Ensino Remoto Emergencial (ERE)")

    total_inicial = len(df)

    condicoes = []
    df_filtrado, _, total_final, removidos = calcula_filtragem(df, condicoes)

    exibe_info_filtragem(total_inicial, total_final, removidos)

    # Preparação específica para a análise pandêmica
    df_filtrado = preparar_dados_pandemia(df_filtrado)

    exibir_grafico_cra_periodo_continuo(df_filtrado)
    exibir_grafico_evasao_periodo(df_filtrado)
    exibir_grafico_cra_periodo_pandemico(df_filtrado)
    exibir_grafico_evasao_forma_periodo(df_filtrado)
    exibir_grafico_cra_forma_periodo(df_filtrado)
