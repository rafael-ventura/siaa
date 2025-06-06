from typing import Union
from pathlib import Path
import pandas as pd

class ModuloLeitura:
    @staticmethod
    def ler_dados_planilha(arquivo: Union[str, Path]) -> pd.DataFrame:
        try:
            return pd.read_excel(arquivo)
        except Exception as e:
            raise ValueError(f"Erro ao ler planilha: {str(e)}")

