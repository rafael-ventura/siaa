import pandas as pd

class ModuloClassificacao:
    @staticmethod
    def classificar_idade(df: pd.DataFrame) -> pd.DataFrame:
        if "DT_NASCIMENTO" in df.columns:
            df = df[df["DT_NASCIMENTO"].notna()].copy()

            # Calcular idade no ingresso
            if "ANO_INGRESSO" in df.columns and "SEMESTRE_INGRESSO" in df.columns:
                mes_ingresso = df["SEMESTRE_INGRESSO"].apply(lambda x: 1 if x == 1 else 7)
                data_ingresso = pd.to_datetime({
                    "year": df["ANO_INGRESSO"],
                    "month": mes_ingresso,
                    "day": 1
                }, errors="coerce")
                df["IDADE_INGRESSO"] = (data_ingresso - df["DT_NASCIMENTO"]).dt.days // 365

            # Faixas etárias
            df["FAIXA_IDADE_INGRESSO"] = pd.cut(
                df["IDADE_INGRESSO"],
                bins=[0, 19, 24, 29, 34, 39, 200],
                labels=["<20", "20-24", "25-29", "30-34", "35-39", "40+"],
                include_lowest=True
            )

        return df
