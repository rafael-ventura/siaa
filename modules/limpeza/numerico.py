import pandas as pd


class ModuloNumerico:
    COLUNAS_NUMERICAS = ["CRA"]

    TIPOS_ESPERADOS = {
        "CRA": float,
        "PERIODO_INGRESSO": float,
        "PERIODO_EVASAO": float,
        "ANO_INGRESSO": float,
        "ANO_EVASAO": float
    }

    @staticmethod
    def converter_tipos_numericos(df: pd.DataFrame) -> pd.DataFrame:
        for coluna, tipo in ModuloNumerico.TIPOS_ESPERADOS.items():
            if coluna in df.columns:
                df[coluna] = (
                    df[coluna]
                    .astype(str)
                    .str.replace(",", ".", regex=False)
                    .apply(pd.to_numeric, errors="coerce")
                )
        return df

    @staticmethod
    def arredondar_cra(df: pd.DataFrame) -> pd.DataFrame:
        if "CRA" in df.columns:
            df["CRA_ARREDONDADO"] = (df["CRA"] * 2).round() / 2
        return df
