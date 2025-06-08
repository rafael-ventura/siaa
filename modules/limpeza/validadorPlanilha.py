import re
import pandas as pd


class ValidadorPlanilha:
    # Campos obrigatórios mínimos para análise funcionar
    COLUNAS_OBRIGATORIAS = [
        "SEXO", "DT_NASCIMENTO", "CRA", "FORMA_INGRESSO", "FORMA_EVASAO"
    ]

    # Campos complementares que, se ausentes, limitam funcionalidades específicas
    COLUNAS_OPCIONAIS = [
        "PERIODO_INGRESSO", "PERIODO_EVASAO", "BAIRRO", "CIDADE", "ESTADO", "ENDERECO"
    ]

    COLUNAS_ENDERECO_ALVO = ["BAIRRO", "CIDADE", "ESTADO"]

    COLUNAS_ESPERADAS = COLUNAS_OBRIGATORIAS + COLUNAS_OPCIONAIS

    @classmethod
    def validar_colunas(cls, df: pd.DataFrame):
        faltando = [col for col in cls.COLUNAS_OBRIGATORIAS if col not in df.columns]

        if all(col not in df.columns for col in cls.COLUNAS_ENDERECO_ALVO):
            if "ENDERECO" in df.columns:
                cls._extrair_endereco(df)
                if all(col in df.columns for col in cls.COLUNAS_ENDERECO_ALVO):
                    return faltando
                else:
                    # Informar ausência dos campos complementares se não extraídos
                    faltando += [col for col in cls.COLUNAS_ENDERECO_ALVO if col not in df.columns]
            else:
                faltando += cls.COLUNAS_ENDERECO_ALVO

        return faltando

    @staticmethod
    def _extrair_endereco(df: pd.DataFrame):
        bairros, cidades, estados = [], [], []

        for endereco in df["ENDERECO"]:
            endereco = str(endereco)
            match = re.search(r'([^,\-]+)[,\-]\s*([^,\-]+)[,\-]\s*([A-Z]{2})$', endereco.strip())
            if match:
                bairro, cidade, estado = [m.strip().title() for m in match.groups()]
            else:
                bairro, cidade, estado = (None, None, None)

            bairros.append(bairro)
            cidades.append(cidade)
            estados.append(estado)

        df["BAIRRO"] = bairros
        df["CIDADE"] = cidades
        df["ESTADO"] = estados
