import streamlit as st
import pandas as pd
import plotly.express as px
import geopandas as gpd
import numpy as np
import re

from unidecode import unidecode


def calcula_filtragem(df, condicoes):
    total_inicial = len(df)
    df_filtrado = df.copy()
    for cond in condicoes:
        df_filtrado = df_filtrado[cond(df_filtrado)]
    total_final = len(df_filtrado)
    removidos = total_inicial - total_final
    return df_filtrado, total_inicial, total_final, removidos

def exibe_info_filtragem(total_inicial, total_final, removidos):
    st.info(f"Total original: **{total_inicial} alunos**  \n"
            f"Removidos pelos filtros: **{removidos} alunos**  \n"
            f"Total final para análise: **{total_final} alunos**")

def grafico_bairros(df):
    st.subheader("🗺️ Onde estão os alunos?")
    bairros_mais = (
        df.groupby(['BAIRRO', 'ZONA_GEOGRAFICA']).size().reset_index(name='Alunos').sort_values(by='Alunos', ascending=False)
    )
    st.markdown("**Top bairros com mais alunos:**")
    st.dataframe(bairros_mais.head(10), use_container_width=True)

    cidades_mais = (
        df.groupby('CIDADE').size().reset_index(name='Alunos').sort_values(by='Alunos', ascending=False)
    )
    st.markdown("**Top cidades com mais alunos:**")
    st.dataframe(cidades_mais.head(10), use_container_width=True)

    zona_mais = (
        df.groupby('ZONA_GEOGRAFICA').size().reset_index(name='Alunos').sort_values(by='Alunos', ascending=False)
    )
    st.markdown("**Distribuição por zona geográfica:**")
    st.dataframe(zona_mais, use_container_width=True)

    fig_zona = px.bar(
        zona_mais, x='ZONA_GEOGRAFICA', y='Alunos', title='Distribuição de Alunos por Zona Geográfica'
    )
    st.plotly_chart(fig_zona, use_container_width=True)
    return zona_mais

def grafico_evasao_zona(df, zonas_robustas, min_alunos=10):
    st.subheader("🚨 Estudantes de quais zonas têm maiores taxas de evasão?")
    st.markdown(f"Taxa calculada como proporção de alunos evadidos por zona geográfica. Só mostramos regiões com pelo menos {min_alunos} alunos.")

    evasao_zona = (
        df[df['ZONA_GEOGRAFICA'].isin(zonas_robustas)]
        .groupby('ZONA_GEOGRAFICA')
        .apply(lambda x: (x['FORMA_EVASAO_PADRONIZADA'].str.lower().isin(['evasão', 'evadido', 'evasao']).sum() / len(x)) * 100)
        .reset_index(name='Taxa de Evasão (%)')
        .sort_values(by='Taxa de Evasão (%)', ascending=False)
    )
    st.dataframe(evasao_zona, use_container_width=True)
    fig_evasao_zona = px.bar(
        evasao_zona, x='ZONA_GEOGRAFICA', y='Taxa de Evasão (%)', title='Taxa de Evasão por Zona Geográfica (n >= 10)'
    )
    st.plotly_chart(fig_evasao_zona, use_container_width=True)

def grafico_cra_zona(df, zonas_robustas):
    st.subheader("🎓 Diferença no perfil de CRA por zona geográfica")
    cra_zona = (
        df[df['ZONA_GEOGRAFICA'].isin(zonas_robustas)]
        .groupby('ZONA_GEOGRAFICA')['CRA']
        .mean()
        .reset_index(name='CRA Médio')
        .sort_values(by='CRA Médio', ascending=False)
    )
    st.dataframe(cra_zona, use_container_width=True)
    fig_cra_zona = px.bar(
        cra_zona, x='ZONA_GEOGRAFICA', y='CRA Médio', title='CRA Médio por Zona Geográfica (n >= 10)'
    )
    st.plotly_chart(fig_cra_zona, use_container_width=True)

def grafico_mapa_rio(df):
    st.subheader("🗺️ Mapa: Distribuição de Alunos por Bairro (Município do Rio de Janeiro)")
    geojson_path = r'R:\Dev\dashboard-bsi\dashboard\modules\dados\Limite_de_Bairros.geojson'
    df_rio = df[df['CIDADE'].str.lower() == 'rio de janeiro'].copy()
    alunos_fora_rio = len(df) - len(df_rio)

    def normaliza_nome(texto):
        return unidecode(str(texto)).strip().lower()

    df_rio['BAIRRO_NORM'] = df_rio['BAIRRO'].apply(normaliza_nome)
    gdf = gpd.read_file(geojson_path)
    gdf['BAIRRO_NORM'] = gdf['nome'].apply(normaliza_nome)
    bairros_contagem = df_rio.groupby('BAIRRO_NORM').size().reset_index(name='Alunos')
    gdf = gdf.merge(bairros_contagem, on='BAIRRO_NORM', how='left')
    gdf['Alunos'] = gdf['Alunos'].fillna(0)
    bins = [0, 2, 5, 8, 12, 20, 30, 50, 100, gdf['Alunos'].max() + 1]
    labels = ['0-2', '3-5', '6-8', '9-12', '13-20', '21-30', '31-50', '51-100', '100+']
    gdf['Faixa_Alunos'] = pd.cut(gdf['Alunos'], bins=bins, labels=labels, right=False, include_lowest=True)
    color_sequence = [
        "#e8f5e9", "#a5d6a7", "#66bb6a", "#dce775", "#fff176",
        "#ffd54f", "#ffb300", "#e53935", "#b71c1c"
    ]
    try:
        fig_mapa = px.choropleth_mapbox(
            gdf, geojson=gdf.geometry, locations=gdf.index, color="Faixa_Alunos",
            hover_name="nome", hover_data={"Alunos": True, "Faixa_Alunos": True},
            mapbox_style="carto-positron", center={"lat": -22.9068, "lon": -43.1729},
            zoom=9.8, opacity=0.6, category_orders={"Faixa_Alunos": labels},
            color_discrete_sequence=color_sequence,
            title="Distribuição de Alunos por Bairro - Rio de Janeiro"
        )
        fig_mapa.update_layout(margin={"r":0,"t":30,"l":0,"b":0}, height=550)
        st.plotly_chart(fig_mapa, use_container_width=True)
    except Exception as e:
        st.error(f"Erro ao gerar o mapa interativo: {e}")
    st.warning(f"**{alunos_fora_rio} alunos não são do município do Rio de Janeiro e não aparecem no mapa acima.**")

def grafico_evasao_distancia(df_box):
    st.subheader("🚨 Relação entre Evasão e Distância até a UNIRIO")
    df_box['Evadido'] = df_box['FORMA_EVASAO_PADRONIZADA'].str.lower().isin(['evasão', 'evadido', 'evasao']).map({True: "Evadido", False: "Não Evadido"})
    df_box = df_box.dropna(subset=['DISTANCIA_URCA', 'Evadido'])
    media_dist = df_box.groupby('Evadido')['DISTANCIA_URCA'].mean()
    mediana_dist = df_box.groupby('Evadido')['DISTANCIA_URCA'].median()
    concluintes = df_box[df_box['FORMA_EVASAO_PADRONIZADA'].str.lower().str.contains('concluiu')]
    media_concl = concluintes['DISTANCIA_URCA'].mean()
    mediana_concl = concluintes['DISTANCIA_URCA'].median()
    st.markdown(f"""
    - **Média (evadidos):** {media_dist.get('Evadido', float('nan')):.2f} km  
    - **Mediana (evadidos):** {mediana_dist.get('Evadido', float('nan')):.2f} km  
    - **Média (não evadidos):** {media_dist.get('Não Evadido', float('nan')):.2f} km  
    - **Mediana (não evadidos):** {mediana_dist.get('Não Evadido', float('nan')):.2f} km  
    - **Média (concluíram):** {media_concl:.2f} km  
    - **Mediana (concluíram):** {mediana_concl:.2f} km  
    """)

    from scipy.stats import mannwhitneyu
    evadidos = df_box[df_box['Evadido'] == "Evadido"]['DISTANCIA_URCA']
    nao_evadidos = df_box[df_box['Evadido'] == "Não Evadido"]['DISTANCIA_URCA']
    if len(evadidos) > 0 and len(nao_evadidos) > 0:
        stat, pvalue = mannwhitneyu(evadidos, nao_evadidos, alternative='two-sided')
        st.markdown(f"**Teste Mann-Whitney:** U = `{stat:.2f}`, p-valor = `{pvalue:.3g}`")
        if pvalue < 0.05:
            st.success("Diferença estatisticamente significativa na distância entre evadidos e não evadidos (p < 0.05).")
        else:
            st.info("Não há diferença estatisticamente significativa na distância.")
    else:
        st.info("Não há dados suficientes para o teste de hipótese.")

def grafico_proporcao_evasao_distancia(df_box):
    bins = [0, 2, 5, 8, 12, 20, 30, 50, 100, df_box['DISTANCIA_URCA'].max() + 1]
    labels = ['0-2km', '3-5km', '6-8km', '9-12km', '13-20km', '21-30km', '31-50km', '51-100km', '100km+']
    df_box['Faixa_Distancia'] = pd.cut(df_box['DISTANCIA_URCA'], bins=bins, labels=labels, right=False, include_lowest=True)
    faixa_evasao = (
        df_box.groupby('Faixa_Distancia')
        .apply(lambda x: (x['Evadido'] == "Evadido").mean() * 100)
        .reset_index(name='Taxa de Evasão (%)')
    )
    st.subheader("📊 Taxa de Evasão por Faixa de Distância")
    st.dataframe(faixa_evasao, use_container_width=True)
    fig_faixa = px.bar(
        faixa_evasao,
        x='Faixa_Distancia',
        y='Taxa de Evasão (%)',
        title='Taxa de Evasão por Faixa de Distância até a UNIRIO',
        labels={'Faixa_Distancia': 'Faixa de Distância (km)'}
    )
    st.plotly_chart(fig_faixa, use_container_width=True)

def grafico_tempo_deslocamento(df_box):
    def tempo_em_minutos(t):
        if pd.isna(t): return np.nan
        t = str(t)
        horas = re.search(r'(\d+)\s*h', t)
        mins  = re.search(r'(\d+)\s*min', t)
        h = int(horas.group(1)) if horas else 0
        m = int(mins.group(1)) if mins else 0
        return h*60 + m

    df_box['TEMPO_MINUTOS'] = df_box['TEMPO_DESLOCAMENTO'].apply(tempo_em_minutos)
    bins_tempo = [0, 30, 60, 90, 120, df_box['TEMPO_MINUTOS'].max() + 1]
    labels_tempo = ['0-30min', '31-60min', '61-90min', '91-120min', '120min+']
    df_box['Faixa_Tempo'] = pd.cut(df_box['TEMPO_MINUTOS'], bins=bins_tempo, labels=labels_tempo, right=False, include_lowest=True)
    tempo_faixas = df_box['Faixa_Tempo'].value_counts().sort_index().reset_index()
    tempo_faixas.columns = ['Faixa_Tempo', 'Quantidade de Alunos']
    st.subheader("⏳ Distribuição dos Tempos de Deslocamento por Faixa (Ônibus)")
    fig_dist_tempo = px.bar(
        tempo_faixas,
        x='Faixa_Tempo',
        y='Quantidade de Alunos',
        title='Distribuição dos Tempos de Deslocamento (min) via Transporte Público'
    )
    st.plotly_chart(fig_dist_tempo, use_container_width=True)

    faixa_evasao_tempo = (
        df_box.groupby('Faixa_Tempo')
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

    cra_tempo = (
        df_box.groupby('Faixa_Tempo')['CRA']
        .mean()
        .reset_index(name='CRA Médio')
        .sort_values(by='Faixa_Tempo')
    )
    st.subheader("🎓 CRA Médio por Faixa de Tempo de Deslocamento (Ônibus)")
    st.dataframe(cra_tempo, use_container_width=True)

def graficos_secao_geografica(df: pd.DataFrame):
    st.header("🌍 Análise Sociodemográfica dos Discentes")

    valores_ruins = ['', 'nan', 'na', 'desconhecido']
    condicoes = [
        lambda d: (~d['BAIRRO'].isin(valores_ruins)) & (d['BAIRRO'] != 'ufrrj') & (d['BAIRRO'] != 'rio de janeiro'),
        lambda d: ~d['CIDADE'].isin(valores_ruins),
        lambda d: ~d['ESTADO'].isin(valores_ruins),
        lambda d: (
            d['DISTANCIA_URCA'].notnull() &
            ((d['DISTANCIA_URCA'] > 0) | (d['BAIRRO'] == 'urca'))
        )
    ]
    df_filtrado, total_inicial, total_final, removidos = calcula_filtragem(df, condicoes)
    exibe_info_filtragem(total_inicial, total_final, removidos)

    zona_mais = grafico_bairros(df_filtrado)
    min_alunos = 10
    zonas_robustas = zona_mais[zona_mais['Alunos'] >= min_alunos]['ZONA_GEOGRAFICA']
    grafico_evasao_zona(df_filtrado, zonas_robustas, min_alunos)
    grafico_cra_zona(df_filtrado, zonas_robustas)
    grafico_mapa_rio(df_filtrado)
    grafico_evasao_distancia(df_filtrado)
    grafico_proporcao_evasao_distancia(df_filtrado)
    grafico_tempo_deslocamento(df_filtrado)
