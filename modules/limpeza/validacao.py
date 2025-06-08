import pandas as pd


class ModuloValidacao:
    COLUNAS_REMOVER = ["Seq."]

    @staticmethod
    def remover_colunas_desnecessarias(df: pd.DataFrame) -> pd.DataFrame:
        return df.drop(columns=[col for col in ModuloValidacao.COLUNAS_REMOVER if col in df.columns], errors="ignore")

    @staticmethod
    def preencher_valores_nulos(df: pd.DataFrame) -> pd.DataFrame:
        substituicoes = {
            'BAIRRO': 'Desconhecido',
            'CIDADE': 'Desconhecido',
            'ESTADO': 'Desconhecido'
        }
        for coluna, valor in substituicoes.items():
            if coluna in df.columns:
                df[coluna] = df[coluna].fillna(valor)
        return df
