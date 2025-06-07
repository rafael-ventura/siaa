import streamlit as st
import pandas as pd
import re

from modules.web.graficos.utils import minutos_para_hrmin, tempo_em_minutos, safe_mode, formatar_sexo

def categorizar_ingresso(forma):
    if any(k in forma for k in ['escola pública', 'étnico', 'renda', 'Deficiência']):
        return 'Cotista'
    elif any(k in forma for k in ['Pré-Cotas','Ampla Concorrência', 'Vestibular', 'ENEM']):
        return 'Ampla Concorrência'
    else:
        return 'Outros'

# --- Gráfico Perfil do Aluno ---
def graficos_secao_perfil(df: pd.DataFrame):
    st.header("Perfil do Aluno de Sistemas de Informação (UNIRIO)")

    df = df[df['CRA'] <= 10].copy()
    df = formatar_sexo(df)  # Garante a coluna SEXO_FORMATADO

    colunas_esperadas = [
        'SEXO_FORMATADO', 'ESTADO_CIVIL', 'FAIXA_IDADE_INGRESSO', 'ZONA_GEOGRAFICA',
        'CIDADE', 'BAIRRO', 'FORMA_INGRESSO_PADRONIZADA', 'CRA', 'TEMPO_CURSO',
        'DISTANCIA_URCA', 'TEMPO_DESLOCAMENTO'
    ]
    for col in colunas_esperadas:
        if col not in df.columns:
            st.warning(f"Coluna obrigatória ausente nos dados: '{col}'")
            return

    df['CATEGORIA_INGRESSO'] = df['FORMA_INGRESSO_PADRONIZADA'].apply(categorizar_ingresso)

    sexo = safe_mode(df['SEXO_FORMATADO'])
    estado_civil = safe_mode(df['ESTADO_CIVIL'])
    faixa_idade = safe_mode(df['FAIXA_IDADE_INGRESSO'])
    zona = safe_mode(df['ZONA_GEOGRAFICA'])
    cidade = safe_mode(df['CIDADE'])
    bairro = safe_mode(df['BAIRRO'])
    forma_ingresso = safe_mode(df['CATEGORIA_INGRESSO'])

    cra_medio = df['CRA'].mean()
    cra_mediana = df['CRA'].median()
    tempo_medio = df['TEMPO_CURSO'].mean()
    tempo_mediano = df['TEMPO_CURSO'].median()
    distancia_media = df['DISTANCIA_URCA'].mean()
    distancia_mediana = df['DISTANCIA_URCA'].median()

    # --- TEMPO DE LOCOMOÇÃO ---
    df['TEMPO_MINUTOS'] = df['TEMPO_DESLOCAMENTO'].apply(tempo_em_minutos)
    bins_tempo = [0, 30, 60, 90, 120, 1000]
    labels_tempo = ['0-30 min', '31-60 min', '61-90 min', '91-120 min', '120 min+']
    df['FAIXA_TEMPO_DESLOC'] = pd.cut(df['TEMPO_MINUTOS'], bins=bins_tempo, labels=labels_tempo, right=False, include_lowest=True)
    faixa_tempo_mais_comum = safe_mode(df['FAIXA_TEMPO_DESLOC'])
    tempo_mediano_min = df['TEMPO_MINUTOS'].median()
    tempo_mediano_formatado = minutos_para_hrmin(tempo_mediano_min)

    # --- Mostra tabela resumo ---
    st.subheader("Resumo das Características dos Alunos")
    resumo = pd.DataFrame({
        "Indicador": [
            "Sexo mais comum",
            "Estado civil predominante",
            "Faixa de idade mais comum",
            "Zona geográfica mais frequente",
            "Cidade mais comum",
            "Bairro mais frequente",
            "Forma de ingresso mais comum",
            "CRA médio",
            "CRA mediano",
            "Tempo médio de curso (anos)",
            "Tempo mediano de curso (anos)",
            "Distância média até a UNIRIO (km)",
            "Distância mediana até a UNIRIO (km)",
            "Faixa de tempo de deslocamento mais comum",
            "Tempo mediano de deslocamento",
        ],
        "Valor": [
            sexo,
            estado_civil,
            faixa_idade,
            zona,
            cidade,
            bairro,
            forma_ingresso,
            f"{cra_medio:.2f}",
            f"{cra_mediana:.2f}",
            f"{tempo_medio:.2f}",
            f"{tempo_mediano:.2f}",
            f"{distancia_media:.2f}",
            f"{distancia_mediana:.2f}",
            faixa_tempo_mais_comum,
            tempo_mediano_formatado,
        ]
    })
    st.table(resumo)

    # --- Tabelas de frequência ---
    st.subheader("Distribuições Detalhadas")
    st.markdown("**Distribuição por Sexo:**")
    st.dataframe(df['SEXO_FORMATADO'].value_counts(normalize=True).rename("Proporção (%)").mul(100).round(1).to_frame())
    st.markdown("**Distribuição por Faixa de Idade:**")
    st.dataframe(df['FAIXA_IDADE_INGRESSO'].value_counts(normalize=True).rename("Proporção (%)").mul(100).round(1).to_frame())
    st.markdown("**Distribuição por Zona Geográfica:**")
    st.dataframe(df['ZONA_GEOGRAFICA'].value_counts(normalize=True).rename("Proporção (%)").mul(100).round(1).to_frame())
    st.markdown("**Distribuição por Forma de Ingresso:**")
    st.dataframe(df['CATEGORIA_INGRESSO'].value_counts(normalize=True).rename("Proporção (%)").mul(100).round(1).to_frame())
    st.markdown("**Distribuição por Estado Civil:**")
    st.dataframe(df['ESTADO_CIVIL'].value_counts(normalize=True).rename("Proporção (%)").mul(100).round(1).to_frame())
    st.markdown("**Distribuição por Tempo de Deslocamento (faixa):**")
    st.dataframe(df['FAIXA_TEMPO_DESLOC'].value_counts(normalize=True).rename("Proporção (%)").mul(100).round(1).to_frame())

    # --- Persona textual ---
    st.subheader("Síntese: Quem é o aluno típico do curso?")
    st.markdown(f"""
        > O aluno mais comum de Sistemas de Informação da UNIRIO é do sexo **{sexo.lower()}**, 
        estado civil **{estado_civil.lower()}**, tem idade de **{faixa_idade}** ao ingressar, 
        reside na **{zona}** (bairro mais comum: {bairro}, cidade: {cidade}), 
        ingressou principalmente como **{forma_ingresso}**, possui CRA mediano de **{cra_mediana:.2f}**, 
        leva em média **{tempo_mediano:.2f} anos** para concluir o curso, percorre cerca de **{distancia_mediana:.1f} km**
        até a universidade **e leva em torno de {tempo_mediano_formatado}** de transporte público para chegar até a UNIRIO.
    """)
