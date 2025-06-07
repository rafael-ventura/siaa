import geopandas as gpd
import pandas as pd
import plotly.express as px
import streamlit as st

from modules.web.graficos.utils import (
    normaliza_nome, calcula_filtragem, exibe_info_filtragem, criar_faixas, calcular_taxa_evasao
)

def grafico_bairros(df):
    st.subheader("🗺️ Onde estão os alunos?")
    bairros_mais = df.groupby(['BAIRRO', 'ZONA_GEOGRAFICA']).size().reset_index(name='Alunos').sort_values(by='Alunos', ascending=False)
    cidades_mais = df.groupby('CIDADE').size().reset_index(name='Alunos').sort_values(by='Alunos', ascending=False)
    zona_mais = df.groupby('ZONA_GEOGRAFICA').size().reset_index(name='Alunos').sort_values(by='Alunos', ascending=False)

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
    cra_zona = df_filtrado.groupby('ZONA_GEOGRAFICA')['CRA'].mean().reset_index(name='CRA Médio').sort_values(by='CRA Médio', ascending=False)
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
    fig.update_layout(margin={"r":0,"t":30,"l":0,"b":0}, height=550)
    st.plotly_chart(fig, use_container_width=True)

    fora_rio = len(df) - len(df_rio)
    st.warning(f"**{fora_rio} alunos não são do município do Rio e não aparecem no mapa.**")

def graficos_secao_geografica(df: pd.DataFrame):
    st.header("🌍 Análise Sociodemográfica dos Discentes")

    condicoes = [
        lambda d: (~d['BAIRRO'].isin(['', 'nan', 'na', 'desconhecido'])) & (d['BAIRRO'] != 'ufrrj') & (d['BAIRRO'] != 'rio de janeiro'),
        lambda d: ~d['CIDADE'].isin(['', 'nan', 'na', 'desconhecido']),
        lambda d: ~d['ESTADO'].isin(['', 'nan', 'na', 'desconhecido']),
        lambda d: d['DISTANCIA_URCA'].notnull() & ((d['DISTANCIA_URCA'] > 0) | (d['BAIRRO'] == 'urca'))
    ]
    df_filtrado, total_inicial, total_final, removidos = calcula_filtragem(df, condicoes)
    exibe_info_filtragem(total_inicial, total_final, removidos)

    zonas_df = grafico_bairros(df_filtrado)
    zonas_validas = zonas_df[zonas_df['Alunos'] >= 10]['ZONA_GEOGRAFICA']

    grafico_evasao_zona(df_filtrado, zonas_validas)
    grafico_cra_zona(df_filtrado, zonas_validas)
    grafico_mapa_rio(df_filtrado)
