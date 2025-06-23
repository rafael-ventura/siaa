import pandas as pd
import os
from dotenv import load_dotenv

load_dotenv()
from .distancia import ModuloDistanciaGoogle
from .forma_evasao import ModuloFormaEvasao
from .forma_ingresso import ModuloFormaIngresso
from .numerico import ModuloNumerico
from .temporal import ModuloTemporal
from .localizacao import ModuloLocalizacao
from .texto import ModuloTexto
from .validacao import ModuloValidacao
from ..dados.correcoes_localizacao import correcoes_bairros, correcoes_cidades


def log_etapa(df: pd.DataFrame, nome: str) -> pd.DataFrame:
    print(f"✔️ {nome}: {len(df)} linhas")
    return df


class PipelineFormatacao:
    @staticmethod
    def executar(df: pd.DataFrame) -> pd.DataFrame:
        print("🔧 Iniciando limpeza da planilha...")
        API_KEY = os.getenv("GOOGLE_MAPS_API_KEY")
        df = log_etapa(ModuloValidacao.remover_colunas_desnecessarias(df), "Após remover colunas")
        df = log_etapa(ModuloValidacao.preencher_valores_nulos(df), "Após preencher nulos")
        df = log_etapa(ModuloTemporal.converter_datas(df), "Após converter datas")
        df = log_etapa(ModuloTemporal.formatar_periodos(df), "Após formatar períodos")
        df = log_etapa(ModuloTexto.normalizar_e_corrigir(df, "BAIRRO", correcoes_bairros),
                       "Após normalizar/corrigir BAIRRO")
        df = log_etapa(ModuloTexto.normalizar_e_corrigir(df, "CIDADE", correcoes_cidades),
                       "Após normalizar/corrigir CIDADE")
        df = log_etapa(ModuloLocalizacao.corrigir_enderecos_especificos(df), "Após corrigir endereços específicos")
        df = log_etapa(ModuloLocalizacao.padronizar_bairros_cidades(df), "Após padronizar bairros e cidades")
        df = log_etapa(ModuloLocalizacao.adicionar_cidade_estado(df), "Após adicionar estado")
        df = log_etapa(ModuloLocalizacao.adicionar_zona_geografica(df), "Após classificar zona")
        df = log_etapa(ModuloTemporal.classificar_idade(df), "Após classificar idade")
        df = log_etapa(ModuloNumerico.converter_tipos_numericos(df), "Após converter tipos")
        df = log_etapa(ModuloNumerico.arredondar_cra(df), "Após arredondar CRA")
        df = log_etapa(ModuloTemporal.calcular_tempo_curso(df), "Após calcular tempo de curso")
        df = log_etapa(ModuloFormaIngresso.padronizar_forma_ingresso(df), "Após padronizar forma ingresso")
        df = log_etapa(ModuloFormaEvasao.padronizar_forma_evasao(df), "Após padronizar forma evasão")
        df = log_etapa(ModuloDistanciaGoogle.adicionar_distancia_urca(df, API_KEY), "Após calcular distância Google")
        return df
