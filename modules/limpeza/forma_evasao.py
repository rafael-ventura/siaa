import pandas as pd
import unidecode
import re


class ModuloFormaEvasao:
    MAPEAMENTO_REGEX = {
        "Concluiu": [
            r"\bcon\b", r"curso\s+concluido"
        ],
        "Evasão": [
            r"\baba\b", r"abandono\s+do\s+curso",
            r"\bcan\b", r"cancelamento\s+geral\s+do\s+curso",
            r"desistencia\s*sisu",
            r"\bdes\b", r"desligamento",
            r"\bjub\b", r"jubilamento",
            r"\btic\b", r"transferencia\s+interna"
        ],
        "Cursando": [
            r"sem\s+evasao"
        ],
        "Outros": [
            r"nao\s+identificada",
            r"\bfal\b", r"falecimento"
        ]
    }

    @staticmethod
    def _normalizar_texto(texto: str) -> str:
        texto = unidecode.unidecode(str(texto or ""))
        texto = texto.lower().strip()
        texto = re.sub(r"\s+", " ", texto)
        return texto

    @staticmethod
    def padronizar_forma_evasao(df: pd.DataFrame) -> pd.DataFrame:
        if "FORMA_EVASAO" not in df.columns:
            return df

        padronizadas = []

        for valor in df["FORMA_EVASAO"]:
            val_norm = ModuloFormaEvasao._normalizar_texto(valor)
            categoria_encontrada = "Outros"

            for categoria, regex_list in ModuloFormaEvasao.MAPEAMENTO_REGEX.items():
                for pattern in regex_list:
                    if re.search(pattern, val_norm):
                        categoria_encontrada = categoria
                        break
                if categoria_encontrada != "Outros":
                    break

            padronizadas.append(categoria_encontrada)

        df["FORMA_EVASAO_PADRONIZADA"] = padronizadas
        return df
