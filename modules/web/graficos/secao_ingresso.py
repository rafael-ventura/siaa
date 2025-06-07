import streamlit as st
import plotly.express as px
import pandas as pd

from modules.web.graficos.utils import calcula_filtragem, exibe_info_filtragem, categorizar_ingresso_detalhado, \
    agrupar_ampla_concorrencia


# --- Funções para gráficos ---

def grafico_evolucao(df):
    st.subheader("Distribuição por Forma de Ingresso (Antes e Após Lei de Cotas)")
    evolucao = df.groupby(['ANO_INGRESSO', 'FORMA_INGRESSO_SIMPLIFICADO']).size().reset_index(name='Total')
    fig = px.bar(
        evolucao, x='ANO_INGRESSO', y='Total', color='FORMA_INGRESSO_SIMPLIFICADO',
        title='Distribuição por Forma de Ingresso Antes e Após Lei de Cotas',
        labels={'ANO_INGRESSO': 'Ano de Ingresso', 'Total': 'Quantidade'},
        color_discrete_sequence=px.colors.qualitative.Set1
    )
    fig.add_vline(x=2012, line_dash="dash", line_color="gray", annotation_text="Lei de Cotas (2012)")
    st.plotly_chart(fig)

def graficos_pizza(df):
    st.subheader("Distribuição por Forma de Ingresso (Comparativo)")
    df = agrupar_ampla_concorrencia(df)  # Agrupamento aqui

    col1, col2, col3 = st.columns(3)

    with col1:
        ate_2012 = df[df['ANO_INGRESSO'] <= 2012]
        dist = ate_2012['FORMA_INGRESSO_PADRONIZADA'].value_counts().reset_index()
        dist.columns = ['Categoria', 'Total']
        fig = px.pie(dist, names='Categoria', values='Total', title='Ingresso Geral 2001-2012', color_discrete_sequence=px.colors.qualitative.Set3)
        st.plotly_chart(fig, use_container_width=True)

    with col2:
        de_2013 = df[df['ANO_INGRESSO'] >= 2013]
        dist = de_2013['FORMA_INGRESSO_PADRONIZADA'].value_counts().reset_index()
        dist.columns = ['Categoria', 'Total']
        fig = px.pie(dist, names='Categoria', values='Total', title='Ingresso Detalhado de 2013-2023', color_discrete_sequence=px.colors.qualitative.Pastel)
        st.plotly_chart(fig, use_container_width=True)

    with col3:
        dist = df['FORMA_INGRESSO_PADRONIZADA'].value_counts().reset_index()
        dist.columns = ['Categoria', 'Total']
        fig = px.pie(dist, names='Categoria', values='Total', title='Ingresso Geral 2001-2023', color_discrete_sequence=px.colors.qualitative.Set2)
        st.plotly_chart(fig, use_container_width=True)

    st.markdown("**📋 Tabela Resumo: Distribuição por Forma de Ingresso**")
    st.dataframe(dist.style.format({'Total': '{:,.0f}'}), use_container_width=True)


def grafico_cra(df):
    st.subheader("Diferença no CRA entre Cotistas e Não Cotistas")
    pos_cotas = df[df['FORMA_INGRESSO_SIMPLIFICADO'] != 'Pré-Cotas']
    fig = px.box(
        pos_cotas, x='FORMA_INGRESSO_SIMPLIFICADO', y='CRA', color='FORMA_INGRESSO_SIMPLIFICADO',
        title='Diferença de CRA entre Cotistas e Não Cotistas Pós-Cotas',
        color_discrete_sequence=px.colors.qualitative.Set2
    )
    st.plotly_chart(fig)


def grafico_tempo_medio(df):
    st.subheader("Tempo Médio de Curso (Cotistas vs. Não Cotistas)")
    concluintes = df[df['FORMA_EVASAO_PADRONIZADA'] == 'Concluiu']

    concluintes = agrupar_ampla_concorrencia(concluintes)  # Agrupamento aqui

    tempo_medio = concluintes.groupby('FORMA_INGRESSO_PADRONIZADA')['TEMPO_CURSO'].mean().reset_index().sort_values(
        by='TEMPO_CURSO', ascending=False)
    fig = px.bar(
        tempo_medio,
        x='FORMA_INGRESSO_PADRONIZADA', y='TEMPO_CURSO',
        color='FORMA_INGRESSO_PADRONIZADA',
        title='Tempo Médio de Curso por Categoria',
        labels={'TEMPO_CURSO': 'Tempo Médio de Curso (anos)'},
        color_discrete_sequence=px.colors.qualitative.Set3
    )
    fig.update_xaxes(showticklabels=False)
    fig.update_layout(bargap=0.05)
    st.plotly_chart(fig)
    st.markdown("**📋 Tabela Resumo: Tempo Médio de Curso por Categoria**")
    st.dataframe(tempo_medio.style.format({'TEMPO_CURSO': '{:.2f}'}), use_container_width=True)


def grafico_evasao(df):
    st.subheader("Taxa de Evasão (Cotistas vs. Não Cotistas)")
    df = agrupar_ampla_concorrencia(df)  # Agrupamento aqui

    evasao = df[df['FORMA_EVASAO_PADRONIZADA'] == 'Evasão'].groupby('FORMA_INGRESSO_PADRONIZADA').size()
    total = df.groupby('FORMA_INGRESSO_PADRONIZADA').size()
    taxa_evasao = (evasao / total * 100).reset_index(name='Taxa de Evasão').sort_values(by='Taxa de Evasão',
                                                                                        ascending=False)
    fig = px.bar(
        taxa_evasao,
        x='FORMA_INGRESSO_PADRONIZADA', y='Taxa de Evasão',
        color='FORMA_INGRESSO_PADRONIZADA',
        title='Taxa de Evasão por Categoria',
        labels={'Taxa de Evasão': 'Taxa de Evasão (%)'},
        color_discrete_sequence=px.colors.qualitative.Vivid
    )
    fig.update_xaxes(showticklabels=False)
    fig.update_layout(bargap=0.05)
    st.plotly_chart(fig)
    st.markdown("**📋 Tabela Resumo: Taxa de Evasão por Categoria**")
    st.dataframe(taxa_evasao.style.format({'Taxa de Evasão': '{:.2f}'}), use_container_width=True)

# --- Função Principal da Seção ---

def graficos_secao_ingresso(df: pd.DataFrame):
    st.header("📌 Formas de ingresso e Políticas Afirmativas")

    total_inicial = len(df)

    # Aplicação dos filtros específicos da seção
    condicoes = [
        lambda d: ~(
            (d['ANO_INGRESSO'] <= 2013) &
            (~d['FORMA_INGRESSO_PADRONIZADA'].isin(['Outros', 'Ampla Concorrência - Pré-Cotas']))
        )
    ]
    df_filtrado, _, total_final, removidos = calcula_filtragem(df, condicoes)

    # Exibindo informações sobre registros filtrados
    exibe_info_filtragem(total_inicial, total_final, removidos)

    # Categorização simplificada detalhada
    df_filtrado['FORMA_INGRESSO_SIMPLIFICADO'] = df_filtrado.apply(categorizar_ingresso_detalhado, axis=1)

    # Gráficos específicos da seção
    grafico_evolucao(df_filtrado)
    graficos_pizza(df_filtrado)
    grafico_cra(df_filtrado)
    grafico_tempo_medio(df_filtrado)
    grafico_evasao(df_filtrado)
