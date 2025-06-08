import pandas as pd
import unidecode
import re


class ModuloFormaIngresso:
    MAPEAMENTO_REGEX = {
        "Ampla Concorrência": [
            r"\bampla\s*concorr[êe]ncia\b",
            r"sisu\s*ampla\s*concorrencia"
            r"sisu\s*ampla\s*concorr[êe]ncia",
            r"\bve\s*[-:]?\s*vestibular\b",
            r"\ben\s*[-:]?\s*enem\b"
        ],
        "Escola pública, sem renda + étnico-racial": [
            r"indep.*renda.*pret[oa]s?.*pard[oa]s?",
            r"indep.*renda.*indigen[ao]|indio",
        ],
        "Escola pública, com renda + étnico-racial": [
            r"baixa.*renda.*pret[oa]s?.*pard[oa]s?",
            r"(ate|até).*1.*5.*s\.?m.*pret[oa]s?.*pard[oa]s?",
            r"(ate|até).*1.*5.*s\.?m.*indigen[ao]|indio"
        ],
        "Escola pública, sem renda": [
            r"sisu.*escola.*publica.*indep.*renda",
            r"indep.*renda.*escola.*publica",
            r"independente.*renda.*escola.*publica"
        ],
        "Escola pública, com renda": [
            r"sisu.*escola.*publica.*(ate|até).*1.*5.*s\.?m",
            r"baixa.*renda.*escola.*publica",
            r"baixa.*renda.*-.*escola.*publica"
        ],
        "Pessoas com Deficiência": [
            r"pessoa com deficiencia",
            r"\bpcd\b",
            r"deficiencia",
            r"\bcota.*deficiencia\b",
            r"\bcota.*pcd\b"
        ]
    }

    AGRUPAR_EM_OUTROS = {
        "Transferência externa",
        "Portador de diploma",
        "Transferência ex-ofício",
        "Mobilidade acadêmica",
        "Programa PEC-G (internacional)",
        "Aluno Especial / Disciplina Isolada",
        "Decisão judicial",
        "Transferência interna"
    }

    @staticmethod
    def _normalizar_texto(texto: str) -> str:
        texto = unidecode.unidecode(str(texto)).lower().strip()
        texto = re.sub(r"\s+", " ", texto)
        return texto

    @staticmethod
    def _ajustar_pre_cotas(df: pd.DataFrame) -> pd.DataFrame:
        if "ANO_INGRESSO" not in df.columns:
            return df

        def categorizar(row):
            if row["FORMA_INGRESSO_PADRONIZADA"] == "Ampla Concorrência":
                try:
                    if int(row["ANO_INGRESSO"]) < 2014:
                        return "Ampla Concorrência - Pré-Cotas"
                except:
                    pass
            return row["FORMA_INGRESSO_PADRONIZADA"]

        df["FORMA_INGRESSO_PADRONIZADA"] = df.apply(categorizar, axis=1)
        return df

    @staticmethod
    def padronizar_forma_ingresso(df: pd.DataFrame) -> pd.DataFrame:
        if "FORMA_INGRESSO" not in df.columns:
            return df

        padronizadas = []
        for valor in df["FORMA_INGRESSO"]:
            val_norm = ModuloFormaIngresso._normalizar_texto(valor)
            categoria_encontrada = "Outros"
            for categoria, regex_list in ModuloFormaIngresso.MAPEAMENTO_REGEX.items():
                if any(re.search(p, val_norm) for p in regex_list):
                    categoria_encontrada = categoria
                    break
            padronizadas.append(categoria_encontrada)

        df["FORMA_INGRESSO_PADRONIZADA"] = [
            "Outros" if val in ModuloFormaIngresso.AGRUPAR_EM_OUTROS else val
            for val in padronizadas
        ]
        df = ModuloFormaIngresso._ajustar_pre_cotas(df)
        return df
