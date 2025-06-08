import streamlit as st
import plotly.express as px
import pandas as pd

from modules.web.graficos.utils import calcula_filtragem, exibe_info_filtragem, categorizar_ingresso_detalhado, \
    agrupar_ampla_concorrencia, faixa_periodo, calcular_ultimo_periodo_cursado

CORES_INGRESSO_DETALHADO = {
    "Ampla Concorrência": "#27ae60",  # Verde
    "Pré-Cotas": "#81c784",  # Verde claro
    "Escola pública, sem renda": "#81d4fa",  # Azul claro
    "Escola pública, com renda": "#1976d2",  # Azul escuro
    "Escola pública, sem renda + étnico-racial": "#ffd180",  # Laranja claro
    "Escola pública, com renda + étnico-racial": "#e17055",  # Laranja
    "Pessoas com Deficiência": "#a29bfe",  # Lilás
    "Outros": "#b2bec3",  # Cinza claro
    'Cotista': "#d63031",  # Vermelho
}


def cores_para_labels(labels):
    return [CORES_INGRESSO_DETALHADO.get(lbl, "#b2bec3") for lbl in labels]  # fallback para cinza claro


def grafico_evolucao(df):
    st.subheader("Distribuição por Forma de Ingresso (Antes e Após Lei de Cotas)")
    evolucao = df.groupby(['ANO_INGRESSO', 'FORMA_INGRESSO_SIMPLIFICADO']).size().reset_index(name='Total')
    labels = evolucao['FORMA_INGRESSO_SIMPLIFICADO'].unique().tolist()
    fig = px.bar(
        evolucao, x='ANO_INGRESSO', y='Total', color='FORMA_INGRESSO_SIMPLIFICADO',
        title='Distribuição por Forma de Ingresso Antes e Após Lei de Cotas',
        labels={'ANO_INGRESSO': 'Ano de Ingresso', 'Total': 'Quantidade'},
        color_discrete_sequence=cores_para_labels(labels),
        category_orders={'FORMA_INGRESSO_SIMPLIFICADO': labels}
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
        labels = dist['Categoria'].tolist()
        fig = px.pie(
            dist, names='Categoria', values='Total', title='Ingresso Geral 2001-2012',
            color_discrete_sequence=cores_para_labels(labels)
        )
        st.plotly_chart(fig, use_container_width=True)

    with col2:
        de_2013 = df[df['ANO_INGRESSO'] >= 2013]
        dist = de_2013['FORMA_INGRESSO_PADRONIZADA'].value_counts().reset_index()
        dist.columns = ['Categoria', 'Total']
        labels = dist['Categoria'].tolist()
        fig = px.pie(
            dist, names='Categoria', values='Total', title='Ingresso Detalhado de 2013-2023',
            color_discrete_sequence=cores_para_labels(labels)
        )
        st.plotly_chart(fig, use_container_width=True)

    with col3:
        dist = df['FORMA_INGRESSO_PADRONIZADA'].value_counts().reset_index()
        dist.columns = ['Categoria', 'Total']
        labels = dist['Categoria'].tolist()
        fig = px.pie(
            dist, names='Categoria', values='Total', title='Ingresso Geral 2001-2023',
            color_discrete_sequence=cores_para_labels(labels)
        )
        st.plotly_chart(fig, use_container_width=True)

    st.markdown("**📋 Tabela Resumo: Distribuição por Forma de Ingresso**")
    st.dataframe(dist.style.format({'Total': '{:,.0f}'}), use_container_width=True)


def grafico_cra(df):
    st.subheader("Diferença no CRA entre Cotistas e Não Cotistas")
    pos_cotas = df[df['FORMA_INGRESSO_SIMPLIFICADO'] != 'Pré-Cotas']
    labels = pos_cotas['FORMA_INGRESSO_SIMPLIFICADO'].unique().tolist()
    fig = px.box(
        pos_cotas, x='FORMA_INGRESSO_SIMPLIFICADO', y='CRA', color='FORMA_INGRESSO_SIMPLIFICADO',
        title='Diferença de CRA entre Cotistas e Não Cotistas Pós-Cotas',
        color_discrete_sequence=cores_para_labels(labels),
        category_orders={'FORMA_INGRESSO_SIMPLIFICADO': labels}
    )
    st.plotly_chart(fig)


def grafico_tempo_medio(df):
    st.subheader("Tempo Médio de Curso (Cotistas vs. Não Cotistas)")

    # Filtra apenas alunos que concluíram
    concluintes = df[df['FORMA_EVASAO_PADRONIZADA'] == 'Concluiu'].copy()

    if concluintes.empty:
        st.warning("Nenhum aluno concluinte encontrado nos dados.")
        return

    concluintes = agrupar_ampla_concorrencia(concluintes)

    tempo_medio = (
        concluintes.groupby('FORMA_INGRESSO_PADRONIZADA')['TEMPO_CURSO']
        .mean()
        .reset_index()
        .sort_values(by='TEMPO_CURSO', ascending=False)
    )

    if tempo_medio.empty:
        st.warning("Dados insuficientes para calcular o tempo médio de curso.")
        return

    labels = tempo_medio['FORMA_INGRESSO_PADRONIZADA'].tolist()
    fig = px.bar(
        tempo_medio,
        x='FORMA_INGRESSO_PADRONIZADA', y='TEMPO_CURSO',
        color='FORMA_INGRESSO_PADRONIZADA',
        title='Tempo Médio de Curso por Categoria',
        labels={'TEMPO_CURSO': 'Tempo Médio de Curso (anos)'},
        color_discrete_sequence=cores_para_labels(labels),
        category_orders={'FORMA_INGRESSO_PADRONIZADA': labels}
    )
    fig.update_xaxes(showticklabels=False)
    fig.update_layout(bargap=0.05)
    st.plotly_chart(fig)

    st.markdown("**📋 Tabela Resumo: Tempo Médio de Curso por Categoria**")
    st.dataframe(tempo_medio.style.format({'TEMPO_CURSO': '{:.2f}'}), use_container_width=True)


def grafico_evasao(df):
    st.subheader("Taxa de Evasão (Cotistas vs. Não Cotistas)")
    df = agrupar_ampla_concorrencia(df)

    evasao = df[df['FORMA_EVASAO_PADRONIZADA'] == 'Evasão'].groupby('FORMA_INGRESSO_PADRONIZADA').size()
    total = df.groupby('FORMA_INGRESSO_PADRONIZADA').size()
    taxa_evasao = (evasao / total * 100).reset_index(name='Taxa de Evasão').sort_values(by='Taxa de Evasão', ascending=False)

    labels = taxa_evasao['FORMA_INGRESSO_PADRONIZADA'].tolist()
    fig = px.bar(
        taxa_evasao,
        x='FORMA_INGRESSO_PADRONIZADA', y='Taxa de Evasão',
        color='FORMA_INGRESSO_PADRONIZADA',
        title='Taxa de Evasão por Categoria',
        labels={'Taxa de Evasão': 'Taxa de Evasão (%)'},
        color_discrete_sequence=cores_para_labels(labels),
        category_orders={'FORMA_INGRESSO_PADRONIZADA': labels}
    )
    fig.update_xaxes(showticklabels=False)
    fig.update_layout(bargap=0.05)
    st.plotly_chart(fig)
    st.markdown("**📋 Tabela Resumo: Taxa de Evasão por Categoria**")
    st.dataframe(taxa_evasao.style.format({'Taxa de Evasão': '{:.2f}'}), use_container_width=True)



def grafico_periodo_evasao(df):
    st.subheader("Em qual período do curso ocorre mais evasão?")

    df = calcular_ultimo_periodo_cursado(df)
    df['FAIXA_PERIODO_EVASAO'] = df['ULTIMO_PERIODO_CURSADO'].apply(faixa_periodo)

    mask_evasao = df['FORMA_EVASAO_PADRONIZADA'].str.lower().isin(['evasão', 'evadido', 'evasao'])
    df_evadidos = df[mask_evasao & df['ULTIMO_PERIODO_CURSADO'].notnull()].copy()

    if df_evadidos.empty:
        st.info("Nenhum aluno evadido com informação de período cursado.")
        return

    contagem = df_evadidos['FAIXA_PERIODO_EVASAO'].value_counts().sort_index().reset_index()
    contagem.columns = ['Faixa de Período', 'Evasões']
    total_evasoes = contagem['Evasões'].sum()
    contagem['Percentual'] = (contagem['Evasões'] / total_evasoes * 100).round(1)

    fig = px.bar(
        contagem,
        x='Faixa de Período',
        y='Evasões',
        title='Evasões por Faixa de Período Cursado',
        labels={'Faixa de Período': 'Faixa de Período (semestres)', 'Evasões': 'Qtd. de Evasões'},
        color='Evasões',
        color_continuous_scale=px.colors.sequential.Viridis,
        hover_data={'Percentual': ':.1f'}
    )
    st.plotly_chart(fig, use_container_width=True)
    st.dataframe(contagem[['Faixa de Período', 'Evasões', 'Percentual']].style.format({'Percentual': '{:.1f}%%'}), use_container_width=True)


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
    df_filtrado = calcular_ultimo_periodo_cursado(
        df_filtrado,
        ano_ingresso_col='ANO_INGRESSO',
        sem_ingresso_col='SEMESTRE_INGRESSO',
        ano_evasao_col='ANO_EVASAO',
        sem_evasao_col='SEMESTRE_EVASAO',
        col_saida='ULTIMO_PERIODO_CURSADO'
    )
    df_filtrado['FORMA_INGRESSO_SIMPLIFICADO'] = df_filtrado.apply(categorizar_ingresso_detalhado, axis=1)
    grafico_evolucao(df_filtrado)
    graficos_pizza(df_filtrado)
    grafico_cra(df_filtrado)
    grafico_tempo_medio(df_filtrado)
    grafico_evasao(df_filtrado)
    grafico_periodo_evasao(df_filtrado)
