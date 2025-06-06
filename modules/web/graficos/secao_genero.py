import streamlit as st
import plotly.express as px
import pandas as pd

def graficos_secao_genero(df: pd.DataFrame):
    st.header("📌 Relações de Gênero entre os Discentes")

    # 🔍 Filtragem inicial: Excluir alunos de 2024 em diante
    df_filtrado = df[df['ANO_INGRESSO'] < 2024].copy()

    # 1. Distribuição por sexo ao longo dos anos
    st.subheader("Distribuição de Alunos por Sexo ao Longo dos Anos")
    dist_ano = df_filtrado.groupby(['ANO_INGRESSO', 'SEXO']).size().reset_index(name='Total')
    fig_dist_ano = px.bar(
        dist_ano,
        x='ANO_INGRESSO',
        y='Total',
        color='SEXO',
        barmode='group',
        labels={'ANO_INGRESSO': 'Ano de Ingresso', 'Total': 'Quantidade', 'SEXO': 'Sexo'},
        color_discrete_map={'M': '#3498db', 'F': '#e17055'},
        title='Distribuição de Alunos por Sexo e Ano de Ingresso'
    )
    st.plotly_chart(fig_dist_ano)

    # 2. Diferença de desempenho (CRA) entre homens e mulheres
    st.subheader("Diferença de Desempenho (CRA) entre Homens e Mulheres")

    # Remove alunos com CRA > 10
    df_cra = df_filtrado[df_filtrado['CRA'] <= 10].copy()

    fig_cra_sexo = px.box(
        df_cra,
        x='SEXO',
        y='CRA',
        color='SEXO',
        title='Distribuição do CRA por Sexo',
        labels={'CRA': 'CRA', 'SEXO': 'Sexo'},
        color_discrete_map={'M': '#3498db', 'F': '#e17055'}
    )
    st.plotly_chart(fig_cra_sexo)

    # Média de CRA por sexo (após o filtro)
    media_cra_sexo = df_cra.groupby('SEXO')['CRA'].mean().reset_index()
    media_cra_sexo.columns = ['Sexo', 'Média CRA']
    st.markdown("**📋 Tabela Resumo: Média de CRA por Sexo**")
    st.dataframe(media_cra_sexo, use_container_width=True)

    # 3. Frequência de evasão por sexo
    st.subheader("Frequência de Evasão por Sexo")
    df_filtrado['EVADIU'] = df_filtrado['FORMA_EVASAO_PADRONIZADA'].apply(
        lambda x: 1 if str(x).lower() in ['evadido', 'evasão', 'evasao'] else 0
    )
    evasao_sexo = df_filtrado.groupby('SEXO')['EVADIU'].agg(['sum', 'count']).reset_index()
    evasao_sexo['Taxa de Evasão (%)'] = 100 * evasao_sexo['sum'] / evasao_sexo['count']

    fig_evasao = px.bar(
        evasao_sexo,
        x='SEXO',
        y='Taxa de Evasão (%)',
        color='SEXO',
        labels={'SEXO': 'Sexo', 'Taxa de Evasão (%)': 'Taxa de Evasão (%)'},
        color_discrete_map={'M': '#3498db', 'F': '#e17055'},
        title='Taxa de Evasão por Sexo'
    )
    st.plotly_chart(fig_evasao)
    st.markdown("**📋 Tabela Resumo: Taxa de Evasão por Sexo**")
    st.dataframe(evasao_sexo[['SEXO', 'Taxa de Evasão (%)']], use_container_width=True)
