import numpy as np
import pandas as pd
from datetime import datetime


class ModuloTemporal:
    @staticmethod
    def converter_datas(df: pd.DataFrame) -> pd.DataFrame:
        if "DT_NASCIMENTO" in df.columns:
            df["DT_NASCIMENTO"] = pd.to_datetime(df["DT_NASCIMENTO"], errors="coerce", dayfirst=True)
        return df

    @staticmethod
    def formatar_periodos(df: pd.DataFrame) -> pd.DataFrame:
        def limpar_semestre(valor):
            if pd.isna(valor):
                return np.nan
            valor = str(valor).strip().lower()
            if "1" in valor:
                return 1
            elif "2" in valor:
                return 2
            return np.nan

        if "PERIODO_INGRESSO" in df.columns:
            df["SEMESTRE_INGRESSO"] = df["PERIODO_INGRESSO"].apply(limpar_semestre)
            df.drop(columns=["PERIODO_INGRESSO"], inplace=True, errors="ignore")

        if "PERIODO_EVASAO" in df.columns:
            df["SEMESTRE_EVASAO"] = df["PERIODO_EVASAO"].apply(limpar_semestre)
            df.drop(columns=["PERIODO_EVASAO"], inplace=True, errors="ignore")

        return df

    @staticmethod
    def calcular_tempo_curso(df: pd.DataFrame) -> pd.DataFrame:
        def calcular(row):
            try:
                if pd.isna(row["ANO_INGRESSO"]) or pd.isna(row["ANO_EVASAO"]):
                    return np.nan
                ano_i, sem_i = int(row["ANO_INGRESSO"]), int(row["SEMESTRE_INGRESSO"])
                ano_e, sem_e = int(row["ANO_EVASAO"]), int(row["SEMESTRE_EVASAO"])

                mes_i = 1 if sem_i == 1 else 7
                mes_e = 1 if sem_e == 1 else 7

                dt_i = pd.Timestamp(year=ano_i, month=mes_i, day=1)
                dt_e = pd.Timestamp(year=ano_e, month=mes_e, day=1)

                return round((dt_e - dt_i).days / 365.25, 2)
            except:
                return np.nan

        if "ANO_INGRESSO" in df.columns and "ANO_EVASAO" in df.columns:
            df["TEMPO_CURSO"] = df.apply(calcular, axis=1)

        return df
