# ============================ IMPORTS ============================

import geopandas as gpd
import pandas as pd
import plotly.express as px
import streamlit as st
from scipy.stats import mannwhitneyu

from modules.web.graficos.utils import (
    normaliza_nome, calcula_filtragem, exibe_info_filtragem, criar_faixas,
    calcular_taxa_evasao, tempo_em_minutos
)


# ======================== FUNÇÕES DE GRÁFICOS =====================

def grafico_bairros(df):
    st.subheader("🗺️ Onde estão os alunos?")
    bairros_mais = df.groupby(['BAIRRO', 'ZONA_GEOGRAFICA']).size().reset_index(name='Alunos').sort_values(by='Alunos',
                                                                                                           ascending=False)
    cidades_mais = df.groupby('CIDADE').size().reset_index(name='Alunos').sort_values(by='Alunos', ascending=False)
    zona_mais = df.groupby('ZONA_GEOGRAFICA').size().reset_index(name='Alunos').sort_values(by='Alunos',
                                                                                            ascending=False)

    st.markdown("**Top bairros com mais alunos:**")
    st.dataframe(bairros_mais.head(10), use_container_width=True)
    st.markdown("**Top cidades com mais alunos:**")
    st.dataframe(cidades_mais.head(10), use_container_width=True)
    st.markdown("**Distribuição por zona geográfica:**")
    st.dataframe(zona_mais, use_container_width=True)

    fig_zona = px.bar(zona_mais, x='ZONA_GEOGRAFICA', y='Alunos', title='Distribuição de Alunos por Zona Geográfica')
    st.plotly_chart(fig_zona, use_container_width=True)
    return zona_mais


def grafico_evasao_zona(df, zonas_robustas):
    st.subheader("🚨 Estudantes de quais zonas têm maiores taxas de evasão?")
    taxa_evasao = calcular_taxa_evasao(df[df['ZONA_GEOGRAFICA'].isin(zonas_robustas)], 'ZONA_GEOGRAFICA')
    st.dataframe(taxa_evasao, use_container_width=True)
    fig = px.bar(taxa_evasao, x='ZONA_GEOGRAFICA', y='Taxa de Evasão (%)', title='Taxa de Evasão por Zona Geográfica')
    st.plotly_chart(fig, use_container_width=True)


def grafico_cra_zona(df, zonas_robustas):
    st.subheader("🎓 Diferença no perfil de CRA por zona geográfica")
    df_filtrado = df[df['ZONA_GEOGRAFICA'].isin(zonas_robustas)]
    cra_zona = df_filtrado.groupby('ZONA_GEOGRAFICA')['CRA'].mean().reset_index(name='CRA Médio').sort_values(
        by='CRA Médio', ascending=False)
    st.dataframe(cra_zona, use_container_width=True)
    fig = px.bar(cra_zona, x='ZONA_GEOGRAFICA', y='CRA Médio', title='CRA Médio por Zona Geográfica')
    st.plotly_chart(fig, use_container_width=True)


def grafico_mapa_rio(df):
    st.subheader("🗺️ Mapa: Distribuição de Alunos por Bairro (Município do Rio de Janeiro)")
    df_rio = df[df['CIDADE'].str.lower() == 'rio de janeiro'].copy()
    geojson_path = 'modules/dados/Limite_de_Bairros.geojson'

    df_rio['BAIRRO_NORM'] = df_rio['BAIRRO'].apply(normaliza_nome)
    gdf = gpd.read_file(geojson_path)
    gdf['BAIRRO_NORM'] = gdf['nome'].apply(normaliza_nome)

    contagem = df_rio.groupby('BAIRRO_NORM').size().reset_index(name='Alunos')
    gdf = gdf.merge(contagem, on='BAIRRO_NORM', how='left').fillna({'Alunos': 0})
    bins = [0, 2, 5, 8, 12, 20, 30, 50, 100, gdf['Alunos'].max() + 1]
    labels = ['0-2', '3-5', '6-8', '9-12', '13-20', '21-30', '31-50', '51-100', '100+']
    gdf = criar_faixas(gdf, 'Alunos', bins, labels, 'Faixa_Alunos')

    fig = px.choropleth_mapbox(
        gdf, geojson=gdf.geometry, locations=gdf.index, color="Faixa_Alunos",
        hover_name="nome", hover_data={"Alunos": True},
        mapbox_style="carto-positron", center={"lat": -22.9068, "lon": -43.1729},
        zoom=9.8, opacity=0.6,
        category_orders={"Faixa_Alunos": labels},
        color_discrete_sequence=px.colors.sequential.YlOrRd,
        title="Distribuição de Alunos por Bairro - RJ"
    )
    fig.update_layout(margin={"r": 0, "t": 30, "l": 0, "b": 0}, height=550)
    st.plotly_chart(fig, use_container_width=True)

    fora_rio = len(df) - len(df_rio)
    st.warning(f"**{fora_rio} alunos não são do município do Rio e não aparecem no mapa.**")


def grafico_evasao_distancia(df):
    st.subheader("🚨 Relação entre Evasão e Distância até a UNIRIO")

    if df.empty or 'DISTANCIA_URCA' not in df.columns:
        st.warning("Dados insuficientes para análise de distância.")
        return

    # Define evadido/não evadido
    df['Evadido'] = df['FORMA_EVASAO_PADRONIZADA'].str.lower().isin(
        ['evasão', 'evadido', 'evasao']).map({True: "Evadido", False: "Não Evadido"})

    df_box = df.dropna(subset=['DISTANCIA_URCA', 'Evadido'])

    # Cálculos das estatísticas
    media_dist = df_box.groupby('Evadido')['DISTANCIA_URCA'].mean()
    mediana_dist = df_box.groupby('Evadido')['DISTANCIA_URCA'].median()
    concluintes = df_box[df_box['FORMA_EVASAO_PADRONIZADA'].str.lower().str.contains('concluiu')]
    media_concl = concluintes['DISTANCIA_URCA'].mean()
    mediana_concl = concluintes['DISTANCIA_URCA'].median()

    # Construir DataFrame com os resultados
    resumo_df = pd.DataFrame({
        'Média (km)': {
            'Evadidos': round(media_dist.get('Evadido', float('nan')), 2),
            'Não Evadidos': round(media_dist.get('Não Evadido', float('nan')), 2),
            'Concluintes': round(media_concl, 2)
        },
        'Mediana (km)': {
            'Evadidos': round(mediana_dist.get('Evadido', float('nan')), 2),
            'Não Evadidos': round(mediana_dist.get('Não Evadido', float('nan')), 2),
            'Concluintes': round(mediana_concl, 2)
        }
    })

    st.dataframe(resumo_df)

    # Teste Mann-Whitney
    evadidos = df_box[df_box['Evadido'] == "Evadido"]['DISTANCIA_URCA']
    nao_evadidos = df_box[df_box['Evadido'] == "Não Evadido"]['DISTANCIA_URCA']

    if len(evadidos) > 0 and len(nao_evadidos) > 0:
        stat, pvalue = mannwhitneyu(evadidos, nao_evadidos, alternative='two-sided')
        st.markdown(f"**Teste Mann-Whitney:** U = `{stat:.2f}`, p-valor = `{pvalue:.3g}`")
        if pvalue < 0.05:
            st.success(
                "Diferença estatisticamente significativa na distância entre evadidos e não evadidos (p < 0.05).")
        else:
            st.info("Não há diferença estatisticamente significativa na distância.")
    else:
        st.info("Não há dados suficientes para o teste de hipótese.")


def grafico_proporcao_evasao_distancia(df):
    st.subheader("📊 Taxa de Evasão por Faixa de Distância")
    if df.empty or 'DISTANCIA_URCA' not in df.columns:
        st.warning("Dados insuficientes para análise de distância.")
        return

    bins = [0, 2, 5, 8, 12, 20, 30, 50, 100, df['DISTANCIA_URCA'].max() + 1]
    labels = ['0-2km', '3-5km', '6-8km', '9-12km', '13-20km', '21-30km', '31-50km', '51-100km', '100km+']
    df['Faixa_Distancia'] = pd.cut(df['DISTANCIA_URCA'], bins=bins, labels=labels, right=False, include_lowest=True)
    faixa_evasao = (
        df.groupby('Faixa_Distancia')
        .apply(lambda x: (x['Evadido'] == "Evadido").mean() * 100)
        .reset_index(name='Taxa de Evasão (%)')
    )
    st.dataframe(faixa_evasao, use_container_width=True)
    fig_faixa = px.bar(
        faixa_evasao,
        x='Faixa_Distancia',
        y='Taxa de Evasão (%)',
        title='Taxa de Evasão por Faixa de Distância até a UNIRIO',
        labels={'Faixa_Distancia': 'Faixa de Distância (km)'}
    )
    st.plotly_chart(fig_faixa, use_container_width=True)


def grafico_tempo_deslocamento(df):
    if df.empty or 'TEMPO_DESLOCAMENTO' not in df.columns:
        st.warning("Dados insuficientes para análise de tempo de deslocamento.")
        return

    # --- Distribuição dos Tempos de Deslocamento (em faixas) ---
    st.subheader("⏳ Distribuição dos Tempos de Deslocamento por Faixa (Ônibus)")
    df['TEMPO_MINUTOS'] = df['TEMPO_DESLOCAMENTO'].apply(tempo_em_minutos)
    bins_tempo = [0, 30, 60, 90, 120, df['TEMPO_MINUTOS'].max() + 1]
    labels_tempo = ['0-30min', '31-60min', '61-90min', '91-120min', '120min+']
    df['Faixa_Tempo'] = pd.cut(df['TEMPO_MINUTOS'], bins=bins_tempo, labels=labels_tempo, right=False,
                               include_lowest=True)
    tempo_faixas = df['Faixa_Tempo'].value_counts().sort_index().reset_index()
    tempo_faixas.columns = ['Faixa_Tempo', 'Quantidade de Alunos']
    fig_dist_tempo = px.bar(
        tempo_faixas,
        x='Faixa_Tempo',
        y='Quantidade de Alunos',
        title='Distribuição dos Tempos de Deslocamento (min) via Transporte Público'
    )
    st.plotly_chart(fig_dist_tempo, use_container_width=True)

    # --- Taxa de evasão por faixa de tempo de deslocamento ---
    faixa_evasao_tempo = (
        df.groupby('Faixa_Tempo')
        .apply(lambda x: (x['Evadido'] == "Evadido").mean() * 100)
        .reset_index(name='Taxa de Evasão (%)')
    )
    st.subheader("📊 Taxa de Evasão por Faixa de Tempo de Deslocamento (Ônibus)")
    st.dataframe(faixa_evasao_tempo, use_container_width=True)
    fig_faixa_tempo = px.bar(
        faixa_evasao_tempo,
        x='Faixa_Tempo',
        y='Taxa de Evasão (%)',
        title='Taxa de Evasão por Faixa de Tempo de Deslocamento até a UNIRIO',
        labels={'Faixa_Tempo': 'Faixa de Tempo (min)'}
    )
    st.plotly_chart(fig_faixa_tempo, use_container_width=True)

    # --- CRA médio por faixa de tempo de deslocamento ---
    cra_tempo = (
        df.groupby('Faixa_Tempo')['CRA']
        .mean()
        .reset_index(name='CRA Médio')
        .sort_values(by='Faixa_Tempo')
    )
    st.subheader("🎓 CRA Médio por Faixa de Tempo de Deslocamento (Ônibus)")
    st.dataframe(cra_tempo, use_container_width=True)


# ======================== FUNÇÃO PRINCIPAL =======================

def graficos_secao_geografica(df: pd.DataFrame):
    st.header("🌍 Análise Sociodemográfica dos Discentes")
    condicoes = [
        lambda d: (~d['BAIRRO'].isin(['', 'nan', 'na', 'desconhecido'])),
        lambda d: ~d['CIDADE'].isin(['', 'nan', 'na', 'desconhecido']),
        lambda d: ~d['ESTADO'].isin(['', 'nan', 'na', 'desconhecido']),
        lambda d: (d['ENDERECO'].notnull() & (d['ENDERECO'] != '') & d['ENDERECO'] != 'None'),
    ]
    # Filtro geral para a seção
    df_filtrado, total_inicial, total_final, removidos = calcula_filtragem(df, condicoes)
    exibe_info_filtragem(total_inicial, total_final, removidos)

    # 1. Distribuição geral
    zonas_df = grafico_bairros(df_filtrado)
    zonas_validas = zonas_df[zonas_df['Alunos'] >= 10]['ZONA_GEOGRAFICA']

    # 2. Comparação entre zonas
    grafico_evasao_zona(df_filtrado, zonas_validas)
    grafico_cra_zona(df_filtrado, zonas_validas)

    # 3. Gráficos de distância e deslocamento
    st.markdown("---")
    st.subheader("🔍 Análises considerando apenas alunos com DISTÂNCIA válida")
    filtro_dist = lambda d: d['DISTANCIA_URCA'].notnull() & (d['DISTANCIA_URCA'] >= 0)
    df_distancia, total_ini_d, total_fin_d, rem_d = calcula_filtragem(df_filtrado, [filtro_dist])
    exibe_info_filtragem(total_ini_d, total_fin_d, rem_d)

    grafico_evasao_distancia(df_distancia)
    grafico_proporcao_evasao_distancia(df_distancia)
    grafico_tempo_deslocamento(df_distancia)

    # 4. Mapa (zoom visual, conclusão da seção)
    st.markdown("---")
    grafico_mapa_rio(df_filtrado)
