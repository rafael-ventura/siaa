import pandas as pd
import unidecode
from typing import Dict, List


class ModuloTexto:
    @staticmethod
    def normalizar_coluna(df: pd.DataFrame, coluna: str) -> pd.DataFrame:
        if coluna in df.columns:
            df[coluna] = df[coluna].fillna('').astype(str)
            df[coluna] = df[coluna].apply(lambda x: unidecode.unidecode(x).strip().lower())
        return df

    @staticmethod
    def aplicar_correcoes(df: pd.DataFrame, coluna: str, mapa_correcoes: Dict[str, List[str]]) -> pd.DataFrame:
        if coluna in df.columns:
            for correto, errados in mapa_correcoes.items():
                df[coluna] = df[coluna].replace(errados, correto)
        return df

    @staticmethod
    def normalizar_e_corrigir(df: pd.DataFrame, coluna: str, mapa_correcoes: Dict[str, List[str]]) -> pd.DataFrame:
        df = ModuloTexto.normalizar_coluna(df, coluna)
        df = ModuloTexto.aplicar_correcoes(df, coluna, mapa_correcoes)
        return df