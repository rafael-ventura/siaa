import pandas as pd
import unidecode
import re

class ModuloFormaIngresso:

    MAPEAMENTO_REGEX = {
        "Ampla Concorrência": [
            r"sisu\s*ampla\s*concorrencia",
            r"\bve\s*[-:]?\s*vestibular\b",
            r"\ben\s*[-:]?\s*enem\b"
        ],
        "Escola pública, sem renda": [
            r"sisu.*escola.*publica.*indep.*renda(?!.*preto|.*pardo|.*indigen[ao]|.*indio)"
        ],
        "Escola pública, com renda": [
            r"sisu.*escola.*publica.*(ate|até).*1.*5.*s\.?m(?!.*preto|.*pardo|.*indigen[ao]|.*indio)"
        ],
        "Escola pública, sem renda + étnico-racial": [
            r"sisu.*indep.*renda.*(preto|pardo|indigen[ao]|indio)"
        ],
        "Escola pública, com renda + étnico-racial": [
            r"sisu.*(ate|até).*1.*5.*s\.?m.*(preto|pardo|indigen[ao]|indio)"
        ]
    }

    AGRUPAR_EM_OUTROS = {
        "Transferência externa",
        "Portador de diploma",
        "Transferência ex-ofício",
        "Mobilidade acadêmica",
        "Programa PEC-G (internacional)",
        "Aluno Especial / Disciplina Isolada",
        "Pessoas com deficiência",
        "Decisão judicial",
        "Transferência interna"
    }

    @staticmethod
    def _normalizar_texto(texto: str) -> str:
        texto = unidecode.unidecode(str(texto))
        texto = texto.lower().strip()
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

        # Chama a categorização por ano no final
        df = ModuloFormaIngresso._ajustar_pre_cotas(df)

        return df
