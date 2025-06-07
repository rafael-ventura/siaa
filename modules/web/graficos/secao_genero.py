import streamlit as st
import plotly.express as px
import pandas as pd

from modules.web.graficos.utils import (
    calcula_filtragem,
    exibe_info_filtragem,
    formatar_sexo
)

# --- Gráficos ---

def grafico_distribuicao_sexo_por_ano(df):
    st.subheader("Distribuição de Alunos por Sexo ao Longo dos Anos")
    dist_ano = df.groupby(['ANO_INGRESSO', 'SEXO_FORMATADO']).size().reset_index(name='Total')
    fig = px.bar(
        dist_ano,
        x='ANO_INGRESSO',
        y='Total',
        color='SEXO_FORMATADO',
        barmode='group',
        labels={'ANO_INGRESSO': 'Ano de Ingresso', 'Total': 'Quantidade', 'SEXO_FORMATADO': 'Sexo'},
        color_discrete_map={'Masculino': '#3498db', 'Feminino': '#e17055'},
        title='Distribuição de Alunos por Sexo e Ano de Ingresso'
    )
    st.plotly_chart(fig, key='dist_sexo_ano')


def grafico_cra_por_sexo(df):
    st.subheader("Diferença de Desempenho (CRA) entre Homens e Mulheres")

    df_cra = df[df['CRA'] <= 10].copy()

    fig = px.box(
        df_cra,
        x='SEXO_FORMATADO',
        y='CRA',
        color='SEXO_FORMATADO',
        title='Distribuição do CRA por Sexo',
        labels={'CRA': 'CRA', 'SEXO_FORMATADO': 'Sexo'},
        color_discrete_map={'Masculino': '#3498db', 'Feminino': '#e17055'}
    )
    st.plotly_chart(fig, key='cra_por_sexo')

    media_cra_sexo = df_cra.groupby('SEXO_FORMATADO')['CRA'].mean().reset_index()
    media_cra_sexo.columns = ['Sexo', 'Média CRA']

    st.markdown("**📋 Tabela Resumo: Média de CRA por Sexo**")
    st.dataframe(media_cra_sexo, use_container_width=True)


def grafico_evasao_por_sexo(df):
    st.subheader("Frequência de Evasão por Sexo")

    df['EVADIU'] = df['FORMA_EVASAO_PADRONIZADA'].str.lower().isin(['evadido', 'evasão', 'evasao']).astype(int)

    evasao_sexo = df.groupby('SEXO_FORMATADO')['EVADIU'].agg(['sum', 'count']).reset_index()
    evasao_sexo['Taxa de Evasão (%)'] = 100 * evasao_sexo['sum'] / evasao_sexo['count']

    fig = px.bar(
        evasao_sexo,
        x='SEXO_FORMATADO',
        y='Taxa de Evasão (%)',
        color='SEXO_FORMATADO',
        labels={'SEXO_FORMATADO': 'Sexo', 'Taxa de Evasão (%)': 'Taxa de Evasão (%)'},
        color_discrete_map={'Masculino': '#3498db', 'Feminino': '#e17055'},
        title='Taxa de Evasão por Sexo'
    )
    st.plotly_chart(fig, key='evasao_por_sexo')

    st.markdown("**📋 Tabela Resumo: Taxa de Evasão por Sexo**")
    st.dataframe(evasao_sexo[['SEXO_FORMATADO', 'Taxa de Evasão (%)']], use_container_width=True)


# --- Função Principal da Seção ---

def graficos_secao_genero(df: pd.DataFrame):
    st.header("📌 Relações de Gênero entre os Discentes")

    total_inicial = len(df)

    # Aplicação dos filtros específicos da seção
    condicoes = [
        lambda d: d['SEXO'].isin(['M', 'F', 'Masculino', 'Feminino'])
    ]
    df_filtrado, _, total_final, removidos = calcula_filtragem(df, condicoes)

    exibe_info_filtragem(total_inicial, total_final, removidos)

    # Formatação do sexo e evasão padronizada
    df_filtrado = formatar_sexo(df_filtrado)

    grafico_distribuicao_sexo_por_ano(df_filtrado)
    grafico_cra_por_sexo(df_filtrado)
    grafico_evasao_por_sexo(df_filtrado)
