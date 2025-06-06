import streamlit as st
import plotly.express as px
import pandas as pd
from pandas.api.types import CategoricalDtype

def graficos_secao_pandemia(df: pd.DataFrame):
    st.header("📱 Impactos da COVID-19 e Ensino Remoto Emergencial (ERE)")

    def categorizar_ingresso(forma):
        if 'Pré-Cotas' in forma:
            return 'Pré-Cotas'
        elif any(k in forma for k in ['escola pública', 'étnico', 'renda']):
            return 'Cotista'
        elif any(k in forma for k in ['Ampla Concorrência', 'Vestibular', 'ENEM']):
            return 'Ampla Concorrência'
        else:
            return 'Outros'

    df = df.copy()
    df['Categoria_Ingresso'] = df['FORMA_INGRESSO_PADRONIZADA'].apply(categorizar_ingresso)

    # -----------------------------------------
    # Períodos ajustados: 2020.1 a 2021.2 como Pandemia/ERE
    def classificar_periodo(row):
        ano = row['ANO_INGRESSO']
        sem = int(row['SEMESTRE_INGRESSO']) if 'SEMESTRE_INGRESSO' in row and pd.notnull(row['SEMESTRE_INGRESSO']) else 1
        if ano < 2020:
            return "Pré-pandemia"
        elif (ano == 2020) or (ano == 2021 and sem <= 2):
            return "Pandemia/ERE"
        else:
            return "Pós-pandemia"

    if 'SEMESTRE_INGRESSO' not in df.columns:
        df['SEMESTRE_INGRESSO'] = 1  # fallback se não tiver a coluna

    df['SEMESTRE_INGRESSO'] = df['SEMESTRE_INGRESSO'].astype(str).str.replace('.0', '')
    df['PERIODO_CONTINUO'] = df['ANO_INGRESSO'].astype(str) + '.' + df['SEMESTRE_INGRESSO'].astype(str)
    df['PERIODO_PANDEMIA'] = df.apply(classificar_periodo, axis=1)

    # >>>> CATEGORIA ORDENADA <<<<
    ordem_periodos = ["Pré-pandemia", "Pandemia/ERE", "Pós-pandemia"]
    tipo_categ = CategoricalDtype(categories=ordem_periodos, ordered=True)
    df['PERIODO_PANDEMIA'] = df['PERIODO_PANDEMIA'].astype(tipo_categ)

    # Remove dados futuros SÓ DEPOIS de criar as colunas
    df_filt = df[df['ANO_INGRESSO'] < 2024].copy()
    df_filt['PERIODO_PANDEMIA'] = df_filt['PERIODO_PANDEMIA'].astype(tipo_categ)

    st.header("⏳ Evolução Temporal dos Indicadores Acadêmicos")

    # CRA médio por período
    st.subheader("Média do CRA por Período de Ingresso")
    cra_periodo = (
        df_filt[df_filt['CRA'] <= 10]
        .groupby('PERIODO_CONTINUO')['CRA']
        .mean()
        .reset_index(name='CRA Médio')
        .sort_values(by='PERIODO_CONTINUO')
    )
    fig_cra_periodo = px.line(
        cra_periodo,
        x='PERIODO_CONTINUO',
        y='CRA Médio',
        title='Evolução do CRA Médio por Período de Ingresso',
        markers=True
    )
    fig_cra_periodo.add_vrect(
        x0="2020.1", x1="2021.2", fillcolor="red", opacity=0.15, line_width=0,
        annotation_text="Pandemia/ERE", annotation_position="top left"
    )

    # Só mostra ticks do primeiro semestre de cada ano
    ticks = [p for p in cra_periodo['PERIODO_CONTINUO'] if p.endswith('.1')]
    fig_cra_periodo.update_xaxes(
        tickvals=ticks,
        ticktext=[t.replace('.1', '') for t in ticks]
    )
    st.plotly_chart(fig_cra_periodo, use_container_width=True)

    # Taxa de evasão por período
    st.subheader("Taxa de Evasão por Período de Ingresso")
    df_filt['EVADIDO'] = df_filt['FORMA_EVASAO_PADRONIZADA'].str.lower().isin(['evasão', 'evadido', 'evasao'])
    evasao_periodo = (
        df_filt.groupby('PERIODO_CONTINUO')['EVADIDO']
        .mean()
        .reset_index(name='Taxa de Evasão (%)')
    )
    evasao_periodo['Taxa de Evasão (%)'] *= 100
    fig_evasao_periodo = px.line(
        evasao_periodo,
        x='PERIODO_CONTINUO',
        y='Taxa de Evasão (%)',
        title='Evolução da Taxa de Evasão por Período de Ingresso',
        markers=True
    )
    fig_evasao_periodo.add_vrect(
        x0="2020.1", x1="2021.2", fillcolor="red", opacity=0.15, line_width=0,
        annotation_text="Pandemia/ERE", annotation_position="top left"
    )
    fig_evasao_periodo.update_xaxes(
        tickvals=ticks,
        ticktext=[t.replace('.1', '') for t in ticks]
    )
    st.plotly_chart(fig_evasao_periodo, use_container_width=True)

    st.info("""
       > O destaque em vermelho corresponde ao período de Ensino Remoto Emergencial (2020.1 a 2021.2).
       > Os valores para períodos recentes podem ser provisórios, pois alunos podem não ter finalizado o curso.
       """)

    # --- CRA médio por período categórico ---
    st.subheader("🎓 CRA médio antes, durante e após a pandemia")
    cra_periodo_cat = (
        df_filt[df_filt['CRA'] <= 10]
        .groupby('PERIODO_PANDEMIA')['CRA']
        .mean()
        .reset_index(name='CRA Médio')
        .sort_values(by='PERIODO_PANDEMIA')  # Ordenado
    )
    st.dataframe(cra_periodo_cat, use_container_width=True)
    fig_cra = px.bar(
        cra_periodo_cat, x='PERIODO_PANDEMIA', y='CRA Médio',
        color='PERIODO_PANDEMIA', title="CRA Médio por Período Pandêmico"
    )
    st.plotly_chart(fig_cra, use_container_width=True)

    # --- Taxa de evasão por forma de ingresso em cada período ---
    st.subheader("🚦 Evasão por Forma de Ingresso e Período Pandêmico")
    df_filt['EVADIDO'] = df_filt['FORMA_EVASAO_PADRONIZADA'].str.lower().isin(['evasão', 'evadido', 'evasao'])
    evasao_forma_periodo = (
        df_filt.groupby(['PERIODO_PANDEMIA', 'Categoria_Ingresso'])['EVADIDO']
        .mean().reset_index(name='Taxa de Evasão (%)')
    )
    evasao_forma_periodo['Taxa de Evasão (%)'] = evasao_forma_periodo['Taxa de Evasão (%)'] * 100
    # Ordenação manual aqui também
    evasao_forma_periodo['PERIODO_PANDEMIA'] = evasao_forma_periodo['PERIODO_PANDEMIA'].astype(tipo_categ)
    evasao_forma_periodo = evasao_forma_periodo.sort_values(['Categoria_Ingresso', 'PERIODO_PANDEMIA'])

    fig_evasao_forma = px.bar(
        evasao_forma_periodo,
        x='Categoria_Ingresso', y='Taxa de Evasão (%)',
        color='PERIODO_PANDEMIA', barmode='group',
        category_orders={'PERIODO_PANDEMIA': ordem_periodos},
        title="Taxa de Evasão por Forma de Ingresso em cada Período"
    )
    st.plotly_chart(fig_evasao_forma, use_container_width=True)
    st.dataframe(evasao_forma_periodo, use_container_width=True)

    # --- CRA médio por forma de ingresso e período ---
    st.subheader("🎯 CRA Médio por Forma de Ingresso e Período")
    cra_forma_periodo = (
        df_filt[df_filt['CRA'] <= 10]
        .groupby(['PERIODO_PANDEMIA', 'Categoria_Ingresso'])['CRA']
        .mean().reset_index(name='CRA Médio')
    )
    cra_forma_periodo['PERIODO_PANDEMIA'] = cra_forma_periodo['PERIODO_PANDEMIA'].astype(tipo_categ)
    cra_forma_periodo = cra_forma_periodo.sort_values(['Categoria_Ingresso', 'PERIODO_PANDEMIA'])

    fig_cra_forma = px.bar(
        cra_forma_periodo,
        x='Categoria_Ingresso', y='CRA Médio',
        color='PERIODO_PANDEMIA', barmode='group',
        category_orders={'PERIODO_PANDEMIA': ordem_periodos},
        title="CRA Médio por Forma de Ingresso e Período"
    )
    st.plotly_chart(fig_cra_forma, use_container_width=True)
    st.dataframe(cra_forma_periodo, use_container_width=True)

    st.info("""
    > **Observação:** O período de pandemia/ERE corresponde de 2020.1 até 2021.2. 
    O restante é considerado pré ou pós-pandemia conforme o ano/semestre de ingresso.
    """)

