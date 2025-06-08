import pandas as pd


class ModuloClassificacao:
    @staticmethod
    def classificar_idade(df: pd.DataFrame) -> pd.DataFrame:
        if "DT_NASCIMENTO" in df.columns:
            mask = df["DT_NASCIMENTO"].notna()
            # calcula só para quem tem data de nascimento, mas não remove ninguém!
            if "ANO_INGRESSO" in df.columns and "SEMESTRE_INGRESSO" in df.columns:
                mes_ingresso = df["SEMESTRE_INGRESSO"].apply(lambda x: 1 if x == 1 else 7)
                data_ingresso = pd.to_datetime({
                    "year": df["ANO_INGRESSO"],
                    "month": mes_ingresso,
                    "day": 1
                }, errors="coerce")
                df.loc[mask, "IDADE_INGRESSO"] = (data_ingresso[mask] - df.loc[mask, "DT_NASCIMENTO"]).dt.days // 365

            # Faixa etária só para quem tem idade calculada
            df["FAIXA_IDADE_INGRESSO"] = pd.cut(
                df["IDADE_INGRESSO"],
                bins=[0, 19, 24, 29, 34, 39, 200],
                labels=["<20", "20-24", "25-29", "30-34", "35-39", "40+"],
                include_lowest=True
            )
        return df
