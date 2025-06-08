import re

import numpy as np
import pandas as pd
import streamlit as st
from unidecode import unidecode


# --- Funções Gerais de Texto ---

def normaliza_nome(texto: str) -> str:
    return unidecode(str(texto)).strip().lower()


# --- Funções de Conversão de Dados ---

def tempo_em_minutos(t):
    if pd.isna(t):
        return np.nan
    t = str(t).lower().strip()
    # Captura horas e minutos, seja qual for o formato
    horas = re.search(r'(\d+)\s*(h|hora)', t)
    mins = re.search(r'(\d+)\s*(m|min|minuto)', t)
    h = int(horas.group(1)) if horas else 0
    m = int(mins.group(1)) if mins else 0
    return h * 60 + m


def minutos_para_hrmin(m: float) -> str:
    if pd.isna(m): return "Não informado"
    m = int(m)
    horas, mins = divmod(m, 60)
    return f"{horas}h {mins}min" if horas else f"{mins}min"


# --- Funções de Formatação ---

def formatar_sexo(df: pd.DataFrame) -> pd.DataFrame:
    if 'SEXO' in df.columns:
        df = df.copy()
        df['SEXO_FORMATADO'] = df['SEXO'].map({'M': 'Masculino', 'F': 'Feminino'})
    return df


def safe_mode(s: pd.Series) -> str:
    return s.dropna().mode().iloc[0] if not s.dropna().empty else "Não informado"


# --- Funções de Categorização ---

def categorizar_ingresso_detalhado(row: pd.Series) -> str:
    forma = row['FORMA_INGRESSO_PADRONIZADA']
    ano = int(row['ANO_INGRESSO'])

    if forma == "Ampla Concorrência - Pré-Cotas" and ano < 2014:
        return "Pré-Cotas"
    elif forma == "Ampla Concorrência":
        return "Ampla Concorrência"
    elif forma in [
        "Escola pública, sem renda + étnico-racial",
        "Escola pública, com renda + étnico-racial",
        "Escola pública, com renda",
        "Escola pública, sem renda",
        "Pessoas com Deficiência"
    ]:
        return "Cotista"
    else:
        return "Outros"


# --- Funções de Filtros Comuns ---

def calcula_filtragem(df: pd.DataFrame, condicoes: list) -> tuple:
    total_inicial = len(df)
    df_filtrado = df.copy()
    for cond in condicoes:
        df_filtrado = df_filtrado[cond(df_filtrado)]
    total_final = len(df_filtrado)
    removidos = total_inicial - total_final
    return df_filtrado, total_inicial, total_final, removidos


def exibe_info_filtragem(total_inicial: int, total_final: int, removidos: int):
    st.info(f"Total original: **{total_inicial} alunos**  \n"
            f"Removidos pelos filtros: **{removidos} alunos**  \n"
            f"Total final para análise: **{total_final} alunos**")


# --- Funções de Estatística Básica ---

def calcula_media_mediana(df: pd.DataFrame, grupo: str, valor: str) -> pd.DataFrame:
    resultado = (
        df.groupby(grupo)[valor]
        .agg(['mean', 'median'])
        .rename(columns={'mean': 'Média', 'median': 'Mediana'})
        .reset_index()
    )
    return resultado


# --- Funções para Testes Estatísticos ---

from scipy.stats import mannwhitneyu


def mann_whitney(df: pd.DataFrame, grupo_coluna: str, valor_coluna: str, grupo1: str, grupo2: str):
    grupo1_valores = df[df[grupo_coluna] == grupo1][valor_coluna].dropna()
    grupo2_valores = df[df[grupo_coluna] == grupo2][valor_coluna].dropna()

    if len(grupo1_valores) > 0 and len(grupo2_valores) > 0:
        stat, pvalue = mannwhitneyu(grupo1_valores, grupo2_valores, alternative='two-sided')
        return stat, pvalue
    else:
        return None, None


def exibir_resultado_mannwhitney(stat, pvalue,
                                 mensagem_diferenca="Diferença estatisticamente significativa encontrada.",
                                 mensagem_sem_diferenca="Não há diferença estatisticamente significativa."):
    if stat is None:
        st.info("Não há dados suficientes para o teste de hipótese.")
    else:
        st.markdown(f"**Teste Mann-Whitney:** U = `{stat:.2f}`, p-valor = `{pvalue:.3g}`")
        if pvalue < 0.05:
            st.success(f"{mensagem_diferenca} (p < 0.05)")
        else:
            st.info(mensagem_sem_diferenca)


# --- Funções de Binning Genéricas ---

def criar_faixas(df: pd.DataFrame, coluna: str, bins: list, labels: list, nome_coluna_nova: str) -> pd.DataFrame:
    df[nome_coluna_nova] = pd.cut(df[coluna], bins=bins, labels=labels, right=False, include_lowest=True)
    return df


# --- Função de Evasão Genérica ---

def calcular_taxa_evasao(df: pd.DataFrame, coluna_agrupadora: str,
                         coluna_evasao: str = 'FORMA_EVASAO_PADRONIZADA') -> pd.DataFrame:
    taxa_evasao = (
        df.groupby(coluna_agrupadora)
        .apply(lambda x: (x[coluna_evasao].str.lower().isin(['evasão', 'evadido', 'evasao']).mean()) * 100)
        .reset_index(name='Taxa de Evasão (%)')
    )
    return taxa_evasao.sort_values('Taxa de Evasão (%)', ascending=False)


# --- Função padronizada para categorização da evasão ---

def categorizar_evasao(valor: str) -> str:
    valor = str(valor).strip().upper()
    if valor == "Concluiu":
        return "Concluiu"
    elif valor in ["Evasão"]:
        return "Evasão"
    elif valor == "Cursando":
        return "Cursando"
    else:
        return "Outros"


def agrupar_ampla_concorrencia(df, coluna='FORMA_INGRESSO_PADRONIZADA'):
    df = df.copy()
    df[coluna] = df[coluna].replace({
        "Ampla Concorrência - Pré-Cotas": "Ampla Concorrência",
        "Ampla Concorrência": "Ampla Concorrência"
    })
    return df


# --- Funções específicas para análise temporal/pandemia ---

def classificar_periodo(row: pd.Series) -> str:
    ano = row['ANO_INGRESSO']
    sem = int(row['SEMESTRE_INGRESSO']) if 'SEMESTRE_INGRESSO' in row and pd.notnull(row['SEMESTRE_INGRESSO']) else 1
    if ano < 2020:
        return "Pré-pandemia"
    elif (ano == 2020) or (ano == 2021 and sem <= 2):
        return "Pandemia/ERE"
    else:
        return "Pós-pandemia"


def categorizar_ingresso_pandemia(forma: str) -> str:
    if 'Pré-Cotas' in forma:
        return 'Pré-Cotas'
    elif any(k in forma for k in ['escola pública', 'étnico', 'renda']):
        return 'Cotista'
    elif any(k in forma for k in ['Ampla Concorrência', 'Vestibular', 'ENEM']):
        return 'Ampla Concorrência'
    else:
        return 'Outros'


def calcular_ultimo_periodo_cursado(df,
                                    ano_ingresso_col='ANO_INGRESSO',
                                    sem_ingresso_col='SEMESTRE_INGRESSO',
                                    ano_evasao_col='ANO_EVASAO',
                                    sem_evasao_col='SEMESTRE_EVASAO',
                                    col_saida='ULTIMO_PERIODO_CURSADO'):
    """
    Calcula quantos períodos (semestres) o aluno cursou desde o ingresso até a evasão/conclusão.
    Adiciona a coluna 'ULTIMO_PERIODO_CURSADO' ao DataFrame.
    """

    def calcular_periodo(row):
        try:
            ano_i = int(row[ano_ingresso_col])
            sem_i = int(row[sem_ingresso_col])
            ano_f = int(row[ano_evasao_col])
            sem_f = int(row[sem_evasao_col])
            # O primeiro semestre cursado é período 1
            return (ano_f - ano_i) * 2 + (sem_f - sem_i) + 1
        except Exception:
            return np.nan

    df[col_saida] = df.apply(calcular_periodo, axis=1)
    return df


def faixa_periodo(periodo):
    if pd.isna(periodo):
        return 'Não informado'
    periodo = int(periodo)
    if periodo <= 2:
        return "1º-2º período"
    elif periodo <= 4:
        return "3º-4º período"
    elif periodo <= 6:
        return "5º-6º período"
    elif periodo <= 8:
        return "7º-8º período"
    elif periodo <= 10:
        return "9º-10º período"
    else:
        return "Acima do 10º"
