import pandas as pd
from modules.limpeza.validadorPlanilha import ValidadorPlanilha
from modules.limpeza.main import PipelineFormatacao


def load_and_process(arquivo) -> pd.DataFrame:
    """
    Lê o arquivo .xlsx, valida colunas obrigatórias + complementares
    e aplica pipeline de formatação (com df.copy() no começo).
    """
    df = pd.read_excel(arquivo)
    faltantes = ValidadorPlanilha.validar_colunas(df)
    if faltantes:
        raise ValueError(f"Colunas ausentes: {', '.join(faltantes)}")
    return PipelineFormatacao.executar(df)
