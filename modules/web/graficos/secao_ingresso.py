import streamlit as st
import plotly.express as px
import pandas as pd

def graficos_secao_ingresso(df: pd.DataFrame):

    st.header("📌 Formas de ingresso e Políticas Afirmativas")

    # 🔍 Filtragem inicial clara: Excluir alunos de 2024 em diante para garantir confiabilidade
    df_filtrado = df[df['ANO_INGRESSO'] < 2024]

    # Categorização simplificada
    def categorizar_ingresso(forma):
        if 'Pré-Cotas' in forma:
            return 'Pré-Cotas'
        elif any(k in forma for k in ['escola pública', 'étnico', 'renda']):
            return 'Cotista'
        elif any(k in forma for k in ['Ampla Concorrência', 'Vestibular', 'ENEM']):
            return 'Ampla Concorrência'
        else:
            return 'Outros'

    df_filtrado['Categoria_Ingresso'] = df_filtrado['FORMA_INGRESSO_PADRONIZADA'].apply(categorizar_ingresso)

    # Pergunta 1: Distribuição antes e depois da Lei de Cotas
    st.subheader("Distribuição por Forma de Ingresso (Antes e Após Lei de Cotas)")
    evolucao = df_filtrado.groupby(['ANO_INGRESSO', 'Categoria_Ingresso']).size().reset_index(name='Total')
    fig_evolucao = px.bar(evolucao, x='ANO_INGRESSO', y='Total', color='Categoria_Ingresso',
                          title='Distribuição por Forma de Ingresso Antes e Após Lei de Cotas',
                          labels={'ANO_INGRESSO': 'Ano de Ingresso', 'Total': 'Quantidade'},
                          color_discrete_sequence=px.colors.qualitative.Set1)
    fig_evolucao.add_vline(x=2012, line_dash="dash", line_color="gray", annotation_text="Lei de Cotas (2012)")
    st.plotly_chart(fig_evolucao)

    # Gráficos comparativos de pizza: até 2012, geral e a partir de 2013
    st.subheader("Distribuição por Forma de Ingresso (Comparativo)")
    col1, col2, col3 = st.columns(3)

    with col1:
        ate_2012 = df_filtrado[df_filtrado['ANO_INGRESSO'] <= 2012]
        dist_ate_2012 = ate_2012['Categoria_Ingresso'].value_counts().reset_index()
        dist_ate_2012.columns = ['Categoria', 'Total']
        fig_ate_2012 = px.pie(dist_ate_2012, names='Categoria', values='Total',
                              title='Ingresso Geral 2001-2012',
                              color_discrete_sequence=px.colors.qualitative.Set3)
        st.plotly_chart(fig_ate_2012, use_container_width=True)

    with col2:
        de_2013 = df_filtrado[
            (df_filtrado['ANO_INGRESSO'] >= 2013) &
            (df_filtrado['FORMA_INGRESSO_PADRONIZADA'] != 'Ampla Concorrência - Pré-Cotas')
            ]
        dist_de_2013 = de_2013['FORMA_INGRESSO_PADRONIZADA'].value_counts().reset_index()
        dist_de_2013.columns = ['Categoria', 'Total']
        fig_de_2013 = px.pie(
            dist_de_2013,
            names='Categoria',
            values='Total',
            title='Ingresso Detalhado de 2013-2023',
            color_discrete_sequence=px.colors.qualitative.Pastel
        )
        st.plotly_chart(fig_de_2013, use_container_width=True)
    with col3:
        dist_geral = df_filtrado['FORMA_INGRESSO_PADRONIZADA'].value_counts().reset_index()
        dist_geral.columns = ['Categoria', 'Total']
        fig_geral = px.pie(dist_geral, names='Categoria', values='Total',
                           title='Ingresso Geral 2001-2023',
                           color_discrete_sequence=px.colors.qualitative.Set2)
        st.plotly_chart(fig_geral, use_container_width=True)

    # Pergunta 2: Diferença no CRA
    st.subheader("Diferença no CRA entre Cotistas e Não Cotistas")
    pos_cotas = df_filtrado[df_filtrado['Categoria_Ingresso'] != 'Pré-Cotas']
    fig_cra = px.box(pos_cotas,
                     x='Categoria_Ingresso',
                     y='CRA',
                     color='Categoria_Ingresso',
                     title='Diferença de CRA entre Cotistas e Não Cotistas Pós-Cotas',
                     color_discrete_sequence=px.colors.qualitative.Set2)
    st.plotly_chart(fig_cra)

    # Pergunta 3: Tempo médio de curso
    st.subheader("Tempo Médio de Curso (Cotistas vs. Não Cotistas)")
    concluintes = df_filtrado[df_filtrado['FORMA_EVASAO_PADRONIZADA'] == 'Concluiu']
    tempo_medio = concluintes.groupby('FORMA_INGRESSO_PADRONIZADA')['TEMPO_CURSO'].mean().reset_index()
    # Ordenar de forma decrescente
    tempo_medio = tempo_medio.sort_values(by='TEMPO_CURSO', ascending=False)

    fig_tempo = px.bar(
        tempo_medio,
        x='FORMA_INGRESSO_PADRONIZADA',
        y='TEMPO_CURSO',
        color='FORMA_INGRESSO_PADRONIZADA',
        title='Tempo Médio de Curso por Categoria',
        labels={'TEMPO_CURSO': 'Tempo Médio de Curso (anos)'},
        color_discrete_sequence=px.colors.qualitative.Set3
    )
    fig_tempo.update_xaxes(showticklabels=False)
    fig_tempo.update_layout(bargap=0.05)
    st.plotly_chart(fig_tempo)
    # Mostrar a tabela com os valores médios
    st.markdown("**📋 Tabela Resumo: Tempo Médio de Curso por Categoria**")
    st.dataframe(tempo_medio.style.format({'TEMPO_CURSO': '{:.2f}'}), use_container_width=True)

    # Pergunta 4: Taxa de evasão
    st.subheader("Taxa de Evasão (Cotistas vs. Não Cotistas)")
    evasao = df_filtrado[df_filtrado['FORMA_EVASAO_PADRONIZADA'] == 'Evasão'].groupby('FORMA_INGRESSO_PADRONIZADA').size()
    total = df_filtrado.groupby('FORMA_INGRESSO_PADRONIZADA').size()
    taxa_evasao = (evasao / total * 100).reset_index(name='Taxa de Evasão')
    taxa_evasao = taxa_evasao.sort_values(by='Taxa de Evasão', ascending=False)
    fig_evasao = px.bar(taxa_evasao, x='FORMA_INGRESSO_PADRONIZADA', y='Taxa de Evasão', color='FORMA_INGRESSO_PADRONIZADA',
                        title='Taxa de Evasão por Categoria',
                        labels={'Taxa de Evasão': 'Taxa de Evasão (%)'},
                        color_discrete_sequence=px.colors.qualitative.Vivid)
    fig_evasao.update_xaxes(showticklabels=False)
    fig_evasao.update_layout(bargap=0.05)
    st.plotly_chart(fig_evasao)
    st.markdown("**📋 Tabela Resumo: Taxa de Evasão por Categoria**")
    st.dataframe(taxa_evasao.style.format({'Taxa de Evasão': '{:.2f}'}), use_container_width=True)