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

    # Filtra apenas alunos que concluíram
    concluintes = df[df['FORMA_EVASAO_PADRONIZADA'] == 'Concluiu'].copy()

    if concluintes.empty:
        st.warning("⚠️ Nenhum aluno concluinte encontrado nos dados.")
        return

    concluintes = agrupar_ampla_concorrencia(concluintes)

    tempo_medio = (
        concluintes.groupby('FORMA_INGRESSO_PADRONIZADA')['TEMPO_CURSO']
        .mean()
        .reset_index()
        .sort_values(by='TEMPO_CURSO', ascending=False)
    )

    if tempo_medio.empty:
        st.warning("⚠️ Dados insuficientes para calcular o tempo médio de curso.")
        return

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


def grafico_periodo_evasao(df):
    st.subheader("Em qual período do curso ocorre mais evasão?")

    # Filtra apenas evadidos e que tenham o campo correto preenchido
    mask_evasao = df['FORMA_EVASAO_PADRONIZADA'].str.lower().isin(['evasão', 'evadido', 'evasao'])
    col_ultimo_periodo = 'ULTIMO_PERIODO_CURSADO'  # Ajuste para o nome correto no seu DF
    if col_ultimo_periodo not in df.columns:
        st.info("Coluna de período cursado ('ULTIMO_PERIODO_CURSADO') não encontrada.")
        return

    df_evadidos = df[mask_evasao & df[col_ultimo_periodo].notnull()].copy()
    if df_evadidos.empty:
        st.info("Nenhum aluno evadido com informação de último período cursado.")
        return

    # Garante que seja int
    df_evadidos['ULTIMO_PERIODO_CURSADO'] = df_evadidos['ULTIMO_PERIODO_CURSADO'].astype(int)

    contagem = df_evadidos['ULTIMO_PERIODO_CURSADO'].value_counts().sort_index().reset_index()
    contagem.columns = ['Período do Curso', 'Evasões']

    fig = px.bar(
        contagem, x='Período do Curso', y='Evasões',
        title='Evasões por Período do Curso',
        labels={'Período do Curso': 'Período cursado (1º, 2º, ...)', 'Evasões': 'Qtd. de Evasões'}
    )
    st.plotly_chart(fig, use_container_width=True)
    st.markdown("**📋 Tabela: Quantidade de evasões por período cursado**")
    st.dataframe(contagem, use_container_width=True)

    # Se quiser separar por cotista/não cotista:
    if 'FORMA_INGRESSO_SIMPLIFICADO' in df_evadidos.columns:
        cat = df_evadidos.groupby(['ULTIMO_PERIODO_CURSADO', 'FORMA_INGRESSO_SIMPLIFICADO']).size().reset_index(
            name='Evasões')
        fig_cat = px.bar(
            cat, x='ULTIMO_PERIODO_CURSADO', y='Evasões', color='FORMA_INGRESSO_SIMPLIFICADO',
            title='Evasão por Período e Categoria de Ingresso',
            labels={'ULTIMO_PERIODO_CURSADO': 'Período cursado', 'Evasões': 'Qtd. de Evasões'},
            barmode='group'
        )
        st.plotly_chart(fig_cat, use_container_width=True)

# --- Função Principal da Seção ---

def graficos_secao_ingresso(df: pd.DataFrame):
    st.header("📌 Formas de ingresso e Políticas Afirmativas")

    total_inicial = len(df)

    condicoes = [
        lambda d: ~(
            (d['ANO_INGRESSO'] <= 2013) &
            (~d['FORMA_INGRESSO_PADRONIZADA'].isin(['Outros', 'Ampla Concorrência - Pré-Cotas']))
        )
    ]
    df_filtrado, _, total_final, removidos = calcula_filtragem(df, condicoes)

    exibe_info_filtragem(total_inicial, total_final, removidos)


    # Formatação ingresso e evasão padronizada
    df_filtrado['FORMA_INGRESSO_SIMPLIFICADO'] = df_filtrado.apply(categorizar_ingresso_detalhado, axis=1)
    grafico_evolucao(df_filtrado)
    graficos_pizza(df_filtrado)
    grafico_cra(df_filtrado)
    grafico_tempo_medio(df_filtrado)
    grafico_evasao(df_filtrado)
    grafico_periodo_evasao(df_filtrado)

